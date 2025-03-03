from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urlparse
# Set up Selenium with ChromeDriver
options = Options()
# Comment out headless to see the browser window
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Base URL for the LeetCode problem set
base_url = "https://leetcode.com/problemset/?page="

# List to store extracted problem links
problem_links = []

# Function to save links to a file
sequence_counter = 1  # To keep track of the sequence number of each link

def save_links_to_file(links, file_name="problem_links.txt"):
    global sequence_counter
    with open(file_name, "a") as file:
        for link in links:
            file.write(f"{sequence_counter}. {link}\n")
            sequence_counter += 1


# Loop through pages from 1 to 69
for page_num in range(1, 70):
    url = f"{base_url}{page_num}"
    driver.get(url)
    time.sleep(5)  # Wait for the page to fully load

    try:
        # Find all <a> tags on the page
        links = driver.find_elements(By.TAG_NAME, "a")
        # print(f"Page {page_num}: Found {len(links)} <a> tags")

        # Extract href from each <a> tag
        new_links = []
        for link in links:
            href = link.get_attribute("href")
            if href and "/problems/" in href:
                # Parse the URL to ensure it has exactly one path after /problems/
                path = urlparse(href).path.split("/")
                if len(path) == 3 and path[1] == "problems":
                    new_links.append(href)
                    # print(f"Found valid problem link: {href}")

        # Add new links to the main list
        problem_links.extend(new_links)
        print(f"Current list: {len(problem_links)}")
        # Save to file every 5 pages
        if page_num % 5 == 0:
            save_links_to_file(new_links)
            print(f"Saved links from pages {page_num - 4} to {page_num} to file.")

    except Exception as e:
        print(f"Failed to fetch page {page_num}: {e}")
        break

# Close the browser
driver.quit()

# Final save of any remaining links
save_links_to_file(problem_links)
print("All problem links saved to file.")