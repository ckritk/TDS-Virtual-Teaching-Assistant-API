from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep

# Headless browser setup
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# Load the base page to extract all links
driver.get("https://tds.s-anand.net/#/README")
sleep(3)

# Expand sidebar
for btn in driver.find_elements("css selector", ".sidebar .sidebar-group .sidebar-heading"):
    try:
        btn.click()
        sleep(0.3)
    except:
        pass
sleep(1)

# Collect all unique page URLs
sidebar_links = driver.find_elements("css selector", ".sidebar a")
fragment_urls = sorted(set(
    link.get_attribute("href")
    for link in sidebar_links
    if link.get_attribute("href") and "/#/" in link.get_attribute("href")
))

print(f"Found {len(fragment_urls)} internal pages.")

youtube_links = []

# Go to each page and extract all <a> tags pointing to YouTube
for url in fragment_urls:
    print(f"Visiting: {url}")
    driver.get(url)
    sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "youtu.be" in href or "youtube.com" in href:
            youtube_links.append((url, href))
            print(f"Found YouTube link: {href}")

driver.quit()

# Save results
with open("tds_youtube_links.txt", "w", encoding="utf-8") as f:
    for page_url, yt_url in youtube_links:
        f.write(f"{yt_url}\n")

print("Done! All YouTube links saved.")