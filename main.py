import os
import requests
from fastapi import FastAPI, HTTPException
from bs4 import BeautifulSoup

app = FastAPI()
base_url = "https://wallpaperscraft.com/catalog/nature"
image_directory = "wallpapers"

# Create a directory to save images
if not os.path.exists(image_directory):
    os.makedirs(image_directory)

# Function to download images
def download_image(img_url, image_name):
    try:
        img_data = requests.get(img_url).content
        with open(f"{image_directory}/{image_name}", "wb") as f:
            f.write(img_data)
        return {"status": "success", "image": image_name}
    except Exception as e:
        return {"status": "failed", "image": image_name, "error": str(e)}

# Function to scrape the image URLs from a page
def scrape_images(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch the page.")

    soup = BeautifulSoup(response.text, "html.parser")
    image_elements = soup.find_all("img", class_="wallpapers__image")
    download_results = []

    for img in image_elements:
        img_url = img.get("src").replace("300x168", "1920x1080")
        image_name = img_url.split("/")[-1]
        result = download_image(img_url, image_name)
        download_results.append(result)

    next_page = soup.find("a", class_="pagination__next")
    next_page_url = base_url + next_page.get("href") if next_page else None
    return download_results, next_page_url

@app.get("/scrape")
async def scrape_wallpapers():
    current_page_url = base_url
    all_results = []

    while current_page_url:
        download_results, next_page_url = scrape_images(current_page_url)
        all_results.extend(download_results)
        current_page_url = next_page_url

    return {"message": "Scraping complete", "results": all_results}
