import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

# SELECT BEFORE RUNNING (did this for every role I was interested)
job_title = "Business Intelligence"
location_title = "Barcelona"

# Create a Chrome WebDriver variable to run Selenium
s = Service("./chromedriver")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")  # Maximize the browser window
driver = webdriver.Chrome(service=s, options=chrome_options)

# Navigate to LinkedIn's homepage
url = "https://www.linkedin.com/"
driver.get(url)

# Wait for the page to load 
time.sleep(2)

# Find and click on the "Jobs" option
jobs_element = driver.find_element(
    By.CSS_SELECTOR,
    '[data-tracking-control-name="guest_homepage-basic_guest_nav_menu_jobs"]',
)
jobs_element.click()

# Wait for the jobs page to load 
time.sleep(2)


def select_job(job_title):
    # Find the job_title box using SELECTOR
    search_input = driver.find_element(
        By.CSS_SELECTOR, '[aria-controls="job-search-bar-keywords-typeahead-list"]'
    )
    # Type "Data Scientist" into the input element
    search_input.send_keys(job_title)

    # Sometimes this takes long to load results
    time.sleep(8)

    # Find the dropdown wrapper in job_title box
    dropdown = driver.find_element(By.CLASS_NAME, "typeahead-input__dropdown")
    # Find the ul element
    ul = dropdown.find_element(By.CLASS_NAME, "typeahead-input__dropdown-list")
    # Find the first li element inside the ul and click it
    li = ul.find_element(By.TAG_NAME, "li")
    li.click()


select_job(job_title)
time.sleep(2)


def select_location(location_title):
    search_input = driver.find_element(
        By.CSS_SELECTOR, '[aria-controls="job-search-bar-location-typeahead-list"]'
    )
    search_input.click() 
    time.sleep(2)
    clear_contents_btn = driver.find_element(
        By.CSS_SELECTOR,
        '.location-typeahead-input [data-tracking-control-name="public_jobs_dismissable-input-clear"]',
    )
    clear_contents_btn.click()
    time.sleep(2)
    search_input.send_keys(location_title)

    # Wait for 2 seconds
    time.sleep(4)

    # Find the dropdown element
    dropdown = driver.find_element(
        By.CSS_SELECTOR, ".location-typeahead-input .typeahead-input__dropdown"
    )

    # Find the ul element 
    ul = dropdown.find_element(By.CLASS_NAME, "typeahead-input__dropdown-list")

    time.sleep(3)

    # Find the first li element inside the ul and click it
    li = ul.find_element(By.TAG_NAME, "li")
    li.click()



select_location(location_title)

# Wait for 2 seconds
time.sleep(2)


# Function to scroll to the bottom of the page
def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


# Scroll to the bottom of the page multiple times to load more job cards (adjust the number of scrolls as needed)
for _ in range(15):
    # Check if "see more" is displayed
    try:
        see_more = driver.find_element(By.CLASS_NAME, 'infinite-scroller__show-more-button--visible')
        # Scroll down until the "see more" button is displayed
        see_more.click()
        time.sleep(3)  # Add a delay to allow content to load
        continue
    except NoSuchElementException:
        pass

    # First group of results
    scroll_to_bottom(driver)
    time.sleep(3)  # Add a delay to allow content to load


# Get the job card elements
left_side_cards = driver.find_elements(By.CSS_SELECTOR, ".base-card")


# Function to run the scraping logic and store results in a text file
def run_scraping_and_store(folder_title_raw, cards):
    ROOT_DATA_FOLDER = 'scraped_data'

    # Clean job title to be used as folder name
    folder_title = folder_title_raw.lower().replace(" ", "_")

    import os

    folder_path = f"{ROOT_DATA_FOLDER}/{folder_title}"

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    resultados = []

    for i, card in enumerate(cards):
        # Click on the card
        actions = ActionChains(driver)
        actions.move_to_element(card).click().perform()

        time.sleep(2)  # Wait for the card to expand

        # Get the right-side content
        right_side = driver.find_element(
            By.CSS_SELECTOR, ".two-pane-serp-page__detail-view"
        )
        contents = right_side.get_attribute("outerHTML")

        resultados.append(contents)

        # Store inside of the folder
        filename = f"job_result_{i}.txt"

        with open(f"{folder_path}/{filename}", "w") as f:
            f.write(contents)

# Run the scraping function and store results in 'job_results.txt'
run_scraping_and_store(f"{location_title}_{job_title}", left_side_cards)

# Close the WebDriver
driver.quit()
