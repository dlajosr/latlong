import csv
from fastapi import FastAPI
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

app = FastAPI()

def get_coordinates(zip_code):
    
    # Initialize Chrome webdriver
    driver = webdriver.Chrome()

    # Open Google and search for latitude and longitude of zip code
    driver.get(f"https://www.google.com/search?q={zip_code}+latitude+longitude&hl=en")
    time.sleep(2)  # Wait for page to load

    # Extract latitude and longitude from search results
    try:
        result = driver.find_element(By.XPATH ,'//*[@id="rso"]/div[1]/div/block-component/div/div[1]/div[1]/div/div/div[1]/div/div/div[2]/div/div/div/div[1]')
        coordinates = result.text.split(',')
        latitude = coordinates[0].strip()
        longitude = coordinates[1].strip()
        return latitude, longitude
    except Exception as e:
        return 'NA','NA'
    finally:
        # Close the browser
        driver.quit()

@app.post("/coordinates/")
async def get_coordinates_for_zip_codes(zip_codes: List[str]):
    with open('data/zip_codes.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        zip_codes = [row[0] for row in reader]

    results = []
    for zip_code in zip_codes:
        lat, long = get_coordinates(zip_code)
        if (lat == 'NA' or long == 'NA') :
            results.append((zip_code,'Not Found','Not Found'))
        else :
            latitude = f"{lat[:1]}{lat[1:].split('°')[0]}" if lat.endswith('N') else f"-{lat[:1]}{lat[1:].split('°')[0]}"
            longitude = f"{long[:1]}{long[1:].split('°')[0]}" if long.endswith('E') else f"-{long[:1]}{long[1:].split('°')[0]}"
            results.append((zip_code, latitude, longitude))

    # Write results to CSV file
    with open('data/coordinates.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['zip_code', 'latitude', 'longitude'])  # Write headers
        writer.writerows(results)  # Write coordinates data

    return {"message": "Coordinates saved to coordinates.csv"}