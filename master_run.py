import subprocess
import time
print("Running Google Maps Scraper...")
subprocess.run(["python3", "GoogleMap_Scraper.py"])

print("Google Maps Scraper Completed.")
time.sleep(5)
print("Starting Email Scraper...")

subprocess.run(["scrapy", "crawl", "email_spider"])

print("All Tasks Completed.")