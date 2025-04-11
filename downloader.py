import json
import os
import glob
import time
import requests
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_downloads(download_dir, timeout=120):
    print("Waiting for downloads to finish...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        if not any(glob.glob(os.path.join(download_dir, "*.crdownload"))):
            print("Download complete!")
            return True
        time.sleep(1)
    raise TimeoutError("Download did not complete within the timeout.")

def download_sharepoint(sharepoint_url, download_dir):
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--headless=new")  # Comment out for debug
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        print(f"Trying to download from sharepoint")
        driver.get(sharepoint_url)
        wait = WebDriverWait(driver, 10)
        print("Page loading...")
        try:
            download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-id="download"]')))
            print("Clicking download...")
            download_button.click()
            time.sleep(7)
            print("Download started. Waiting for download to complete...")
            wait_for_downloads(download_dir)
            print("Download should be complete.")
            return 1
        except Exception as e:
            print("Could not find the download button. You might not have access.")
            print(f"Details: {e}")
            return 0
    finally:
        driver.quit()

def download_dropbox(dropbox_url, download_dir):
    try:
        print(f"Downloading folder from Dropbox URL")
        if "dl=0" in dropbox_url:
            dropbox_url = dropbox_url.replace("dl=0", "dl=1")
        elif "dl=1" not in dropbox_url:
            dropbox_url += "&dl=1"
        zip_file_path = os.path.join(download_dir, "context.zip")

        response = requests.get(dropbox_url, stream=True)
        content_type = response.headers.get("Content-Type", "")
        if response.status_code == 200 and "text/html" not in content_type.lower():
            with open(zip_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            # Validate file size
            if os.path.getsize(zip_file_path) < 1024:  # Veryyyy small
                os.remove(zip_file_path)
                print("Download failed: Received unexpected or empty content.")
                return 0
            print(f"Downloaded from Dropbox Successfully")
            return 1
        else:
            print(f"Failed to download from Dropbox")
            return 0
    except Exception as e:
        print(f"Error downloading from Dropbox")
        return 0


def download_folder(config_key="home-url", json_file="config.json", destination="downloads"):
    try:
        with open(json_file) as f:
            config = json.load(f)
            sharepoint_url = config.get(config_key, "")
            if not sharepoint_url:
                print(f"Error: {config_key} not found in config.json")
                return 0
    except Exception as e:
        print(f"Error loading config: {e}")
        return 0

    download_dir = os.path.join(os.getcwd(), destination)
    os.makedirs(download_dir, exist_ok=True)

    if "sharepoint" in sharepoint_url.lower():
        return download_sharepoint(sharepoint_url, download_dir)
    elif "dropbox" in sharepoint_url.lower():
        return download_dropbox(sharepoint_url, download_dir)
    else:
        print(f"URL not supported: {sharepoint_url}")
        return 0

# download_folder("home-url", "config.json", "downloads")
