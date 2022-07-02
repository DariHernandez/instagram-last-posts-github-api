import os
import requests
from time import sleep
from config import Config
from scraping_manager.automate import Web_scraping

def main (): 

    # Get credentials
    credentials = Config ()
    profiles = credentials.get ("profiles")
    post_num = credentials.get ("post_num")
    show_browser = not credentials.get ("show_browser")
    chrome_data_folder = credentials.get ("chrome_data_folder")

    # Paths
    current_path = os.path.dirname (__file__)
    images_path = os.path.join (current_path, "imgs")

    # Open scraper
    scraper = Web_scraping (web_page="https://www.instagram.com/",
                            headless=show_browser, 
                            chrome_folder=chrome_data_folder, 
                            start_killing=True)

    # Loop for each user in profile lists
    for profile in profiles:

        # Open profile
        profile_url = f"https://www.instagram.com/{profile}/"
        scraper.set_page (profile_url)
        sleep (3)
        scraper.refresh_selenium ()

        # Get profile image link
        profile_photo_selector = 'img[data-testid="user-avatar"]'
        image_url = scraper.get_attrib (profile_photo_selector, "src")
        if not image_url:
            profile_photo_selector = 'img[alt="Change profile photo"]'
            image_url = scraper.get_attrib (profile_photo_selector, "src")

        # Download profile image
        res = requests.get (image_url)
        res.raise_for_status ()
        profile_photo_path = os.path.join (images_path, f"{profile} profile.jpg")
        profile_photo = open (profile_photo_path, "wb")
        for chunk in res.iter_content (100000):
            profile_photo.write (chunk)
        profile_photo.close ()


if __name__ == "__main__":
    main()
    input ("end?")