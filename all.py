import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Companies list
comp = [
    'https://www.linkedin.com/jobs/search?location=India&geoId=102713980&f_C=1035&position=1&pageNum=0',  # Microsoft
    'https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1586&position=1&pageNum=0',  # Amazon
    'https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1441'  # Google
]

def scrape_linkedin_jobs():
    options = Options()
    # options.add_argument("--headless")  # Uncomment for headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 4)

    # List to hold all job data
    job_listings = []

    for url in comp:
        driver.get(url)
        time.sleep(5)  # Wait for the page to load

        # Apply "Past week" filter
        try:
            any_time_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Date posted filter. Any time filter is currently applied')]")))
            any_time_button.click()
            time.sleep(2)  # Wait for dropdown to expand

            past_week_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Past week')]")))
            past_week_option.click()

            done_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='filter__submit-button' and @data-tracking-control-name='public_jobs_f_TPR']")))
            done_button.click()
            time.sleep(5)  # Wait for the filter to apply
        except Exception as e:
            print(f"Error applying filter: {e}")

        # Click through job listings
        data_row_index = 1
        while data_row_index <= 50:
            try:
                # Locate job listing element
                job = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@data-row, '{data_row_index}')]")))
                job.click()
                time.sleep(5)  # Wait for the job details to load

                # Extract job title, company name, location, posted date, and job criteria details
                try:
                    # Extract job title
                    job_title = driver.find_element(By.XPATH, "//h1[@class='top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title']").text
                    
                    # Extract company name
                    company_name = driver.find_element(By.XPATH, "//a[@class='topcard__org-name-link topcard__flavor--black-link']").text
                    
                    # Extract location
                    location = driver.find_element(By.XPATH, "//span[@class='topcard__flavor topcard__flavor--bullet']").text
                    
                    # Extract posted date
                    posted_date = driver.find_element(By.XPATH, "//span[@class='posted-time-ago__text topcard__flavor--metadata']").text
                    
                    # Extract job criteria details
                    job_criteria = driver.find_element(By.XPATH, "//ul[@class='description__job-criteria-list']")
                    criteria_items = job_criteria.find_elements(By.CLASS_NAME, "description__job-criteria-item")
                    
                    # Collect job information
                    job_data = {
                        "Job Title": job_title,
                        "Company Name": company_name,
                        "Location": location,
                        "Posted Date": posted_date
                    }

                    for item in criteria_items:
                        header = item.find_element(By.CLASS_NAME, "description__job-criteria-subheader").text
                        text = item.find_element(By.CLASS_NAME, "description__job-criteria-text--criteria").text
                        # Only add these specific fields
                        if header in ["Seniority level", "Employment type", "Job function", "Industries"]:
                            job_data[header] = text

                    job_listings.append(job_data)

                except Exception as e:
                    print(f"Error extracting job details at data-row {data_row_index}: {e}")

                # Go back to the job list page
                driver.back()
                time.sleep(5)  # Wait for the job list to reload
            except Exception as e:
                print(f"Error opening job listing at data-row {data_row_index}: {e}")
                break  # Exit the loop if there's an error to avoid infinite loop

            data_row_index += 1

    driver.quit()

    # Save the job listings to CSV and JSON
    csv_file = "job_listings.csv"
    json_file = "job_listings.json"

    # Ensure all necessary headers are present in CSV
    headers = ["Job Title", "Company Name", "Location", "Posted Date", "Seniority level", "Employment type", "Job function", "Industries"]

    # Save to CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(job_listings)

    # Save to JSON
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(job_listings, file, indent=4)

# Run the LinkedIn job scraping function
scrape_linkedin_jobs()