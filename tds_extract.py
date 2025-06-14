from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep

# Setup headless Chrome
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

base_url = "https://tds.s-anand.net/#/README"
driver.get(base_url)
sleep(3)  # Let JavaScript render

# Step 1: Expand all collapsible sidebar sections
toggle_buttons = driver.find_elements(By.CSS_SELECTOR, ".sidebar .sidebar-group .sidebar-heading")

print(f"Found {len(toggle_buttons)} collapsible sidebar groups.")
for btn in toggle_buttons:
    try:
        btn.click()
        sleep(0.5)
    except:
        pass  # Some are already expanded

sleep(2)  # Wait for all items to expand

# Step 2: Get all sidebar links
sidebar_links = driver.find_elements(By.CSS_SELECTOR, ".sidebar a")
fragment_urls = []
for link in sidebar_links:
    href = link.get_attribute("href")
    if href and "/#/" in href:
        fragment_urls.append(href)

# Remove duplicates
fragment_urls = sorted(set(fragment_urls))
print(f"Total internal pages found: {len(fragment_urls)}")

# Step 3: Visit each link and scrape content
with open("tds_full_course_content.txt", "w", encoding="utf-8") as file:
    for url in fragment_urls:
        print(f"Visiting: {url}")
        driver.get(url)
        sleep(2)

        try:
            content = driver.find_element(By.CLASS_NAME, "markdown-body").text
        except:
            content = driver.find_element(By.TAG_NAME, "body").text

        file.write(f"--- Content from: {url} ---\n")
        file.write(content)
        file.write("\n\n")

driver.quit()
print("Done! All pages saved.")
