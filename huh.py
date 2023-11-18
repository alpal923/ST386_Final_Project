from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.by import By
import json
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import defaultdict

# Initialize the web driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Initial search page URL
url = "https://samlingar.shm.se/sok?type=object&query=Vikingatid&rows=1000&offset=0"
driver.get(url)

# Wait for the page to load (you may need to adjust the sleep duration)
time.sleep(2)

# Handle the cookie disclaimer if it exists
try:
    cookie_disclaimer = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Godkänn alla kakor"]'))
    )
    if cookie_disclaimer.is_displayed():
        cookie_disclaimer.click()
except Exception as e:
    print("No cookie disclaimer found or an error occurred:", e)

# Function to scroll to the bottom of the page
def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Wait for new content to load

# Scroll to the bottom of the page until no new content is loaded
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    scroll_to_bottom(driver)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Now, find all the search result items
results = driver.find_elements(By.XPATH, "//a[contains(@class,'rKAserSVOTC2Sy4lh50nJg') and contains(@class,'miFVghdNq-ew7wuzMJWdDw')]")

# Dictionary to hold the title and its corresponding URL
titles_and_urls = defaultdict(list)

for result in results:
    # Extract the aria-label attribute and split it to get the title
    aria_label = result.get_attribute('aria-label')
    title_split = aria_label.split(' - Föremålsbenämning:')
    title = title_split[0].strip()

    # Extract the URL
    url = result.get_attribute('href')

    # Modify title if it's a duplicate
    if titles_and_urls[title]:
        count = len(titles_and_urls[title]) + 1
        title = f"{title} ({count})"
    
    # Add the title and URL to the dictionary
    titles_and_urls[title].append(url)

# Flatten the dictionary to ensure each title has a unique URL
titles_and_urls = {k: v[0] for k, v in titles_and_urls.items()}

# Dictionary to hold the data for all items
all_items_dict = {}

# Iterate over titles and URLs to fetch table data
for title, url in titles_and_urls.items():
    # Open the link of the result
    driver.get(url)
    time.sleep(3)  # wait for the page to load

    # Grab the first table on the page as the data source
    try:
        table = pd.read_html(driver.page_source)[0]
        row_dict = {row[0]: row[1] for row in table.itertuples(index=False)}
        all_items_dict[title] = row_dict
    except IndexError:
        print(f"No table found on page for {title}")
    except Exception as e:
        print(f"Error processing table for {title}: {e}")

driver.quit()

# You now have a dictionary with item titles as keys and table data (as dictionaries) as values
all_data_json = json.dumps(all_items_dict, indent=4)

# Convert the JSON string to a Python dictionary
data_dict = json.loads(all_data_json)

# Convert the dictionary to a DataFrame
df = pd.DataFrame.from_dict(data_dict, orient='index')

# Reset the index to make the item titles a column
df = df.reset_index()

# Rename the former index column to 'unique_name'
df = df.rename(columns={'index': 'unique_name'})
df.to_csv('Viking_artifacts.csv')
