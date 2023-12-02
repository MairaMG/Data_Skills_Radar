import os
from bs4 import BeautifulSoup
import json

ROOT_RESULTS_FOLDER = 'extracted_data'
ROOT_DATA_FOLDER = 'scraped_data'

# Create ROOT_RESULTS_FOLDER if it doesn't exist
if not os.path.exists(ROOT_RESULTS_FOLDER):
    os.mkdir(ROOT_RESULTS_FOLDER)

def get_title(soup):
    return soup.select_one('.details-pane__content .top-card-layout__title').text

def get_description(soup):
    return soup.select_one('.details-pane__content .description__text').text

def get_org_name(soup):
    return soup.select_one('[data-tracking-control-name="public_jobs_topcard-org-name"]').text

def seniority_level(soup):
    return soup.select_one('[data-tracking-control-name="public_jobs_topcard-job-details"]').text

def get_posted_time_ago(soup):
    return soup.select_one('.details-pane__content .posted-time-ago__text').text

def replace_breakline_for_space(raw_text):
    return raw_text.replace("\n", " ")

def replace_commas_for_csv(raw_text):
    # Replace commas in raw_text for a csv
    return raw_text.replace(",", " ")

def clean(raw_text):
    return replace_commas_for_csv(replace_breakline_for_space(raw_text))

# Read every folder immediaely inside the ROOT_DATA_FOLDER
for folder in os.listdir(ROOT_DATA_FOLDER):
    # Get the path to the folder
    folder_path = os.path.join(ROOT_DATA_FOLDER, folder)

    # Create a .csv file with the 
    results_csv_file = os.path.join(ROOT_RESULTS_FOLDER, f"{folder}.csv")

    # Write the headers to the csv
    with open(results_csv_file, 'w') as f:
        f.write("title,company_name,location,posted_time_ago,seniority_level,employment_type,job_function,industries,description\n") 

    # Read every file inside the folder
    for file in os.listdir(folder_path):
        # Get the path to the file
        file_path = os.path.join(folder_path, file)

        # Read the file
        with open(file_path, 'r') as f:
            print(f"Reading file {file_path}")
            # Read the file content
            file_content = f.read()

            # Parse the file content with BeautifulSoup
            soup = BeautifulSoup(file_content, 'html.parser')

            title = clean(get_title(soup))
            description = clean(get_description(soup))

            header_section = soup.select('.top-card-layout__second-subline .topcard__flavor-row')
            row_with_company_and_location = header_section[0]

            company_name = clean(row_with_company_and_location.select('.topcard__flavor')[0].text)
            location = clean(row_with_company_and_location.select('.topcard__flavor')[1].text)

            posted_time_ago = clean(get_posted_time_ago(soup))

            job_criteria_list = soup.select('.description__job-criteria-list .description__job-criteria-item')

            seniority_level, employment_type, job_function, industries = 'N/A', 'N/A', 'N/A', 'N/A'

            for job_criteria in job_criteria_list:
                job_criteria_text = job_criteria.text
                if 'Seniority level' in job_criteria_text:
                    seniority_level_raw = job_criteria.select_one('.description__job-criteria-text').text
                    seniority_level = clean(seniority_level_raw)
                elif 'Employment type' in job_criteria_text:
                    employment_type_raw = job_criteria.select_one('.description__job-criteria-text').text
                    employment_type = clean(employment_type_raw)
                elif 'Job function' in job_criteria_text:
                    job_function_raw = job_criteria.select_one('.description__job-criteria-text').text
                    job_function = clean(job_function_raw)
                elif 'Industries' in job_criteria_text:
                    industries_raw = job_criteria.select_one('.description__job-criteria-text').text
                    industries = clean(industries_raw)
            
            # Append the job_data to the results file as csv in a new line
            # Order is: title, company_name, location, posted_time_ago, seniority_level, employment_type, job_function, industries, description
            with open(results_csv_file, 'a') as f:
                f.write(f"{title},{company_name},{location},{posted_time_ago},{seniority_level},{employment_type},{job_function},{industries},{description}\n")
