import os
import math
import json
import datetime
import requests
from time import sleep
from config import Config
from scraping_manager.automate import Web_scraping

# Paths
current_path = os.path.dirname (__file__)
images_path = os.path.join (current_path, "imgs")
json_path = os.path.join (current_path, "data.json")

# Get credentials
credentials = Config ()
profiles = credentials.get ("profiles")
post_num = credentials.get ("post_num")
show_browser = not credentials.get ("show_browser")
chrome_data_folder = credentials.get ("chrome_data_folder")
github_repo = credentials.get ("github_repo")
wait_login = credentials.get ("wait_login")


def download_image (url:str, filename:str):
    """Download image from instagram and save it as a local file in imgs folder

    Args:
        url (str): instagram image url
        filename (str): file name to save (.jpg)
    """
    
    # Get image data
    res = requests.get (url)
    res.raise_for_status ()
    image_path = os.path.join (images_path, filename)
    image = open (image_path, "wb")
    for chunk in res.iter_content (100000):
        image.write (chunk)
    image.close ()

def save_data (): 
    """Save instagram data in json file, and download images.
    """

    # Open scraper
    scraper = Web_scraping (web_page="https://www.instagram.com/",
                            headless=show_browser, 
                            chrome_folder=chrome_data_folder)
    sleep (2)
    
    if wait_login:
        input ("continue?")

    # Loop for each user in profile lists
    data = {}
    for profile in profiles:

        profile_data = {}

        # Open profile
        profile_url = f"https://www.instagram.com/{profile}/"
        scraper.set_page (profile_url)
        scraper.refresh_selenium ()

        # Get profile image link
        image_url = None
        while (image_url == "None" or image_url == None):

            # Get image for self other user
            profile_photo_selector = 'canvas + span._aa8h > img'
            image_url = scraper.get_attrib (profile_photo_selector, "src")

            # get image from self user profile
            if not image_url:
                profile_photo_selector = 'img'
                image_url = scraper.get_attrib (profile_photo_selector, "src")

            # Try again
            sleep (2)
            scraper.refresh_selenium ()

        # Download profile image
        profile_photo_name = f"{profile} profile.jpg"
        download_image (image_url, profile_photo_name)

        # Get profile info
        profile_name_selector = "h2"
        name_selector = "ul + ._aa_c > span:nth-child(1)"
        num_posts_selector = "ul._aa_7 li:nth-child(1) span"
        num_followers_selector = "ul._aa_7 li:nth-child(2) span"
        num_following_selector = "ul._aa_7 li:nth-child(3) span"
        category_selector = "ul + ._aa_c > div:nth-child(3) div"
        details_selector = "ul + ._aa_c > div:nth-child(4)"
        web_page_selector = "ul + ._aa_c > a div"

        profile_name = scraper.get_text (profile_name_selector)
        name = scraper.get_text (name_selector)
        num_posts = scraper.get_text (num_posts_selector)
        num_followers = scraper.get_text (num_followers_selector)
        num_following = scraper.get_text (num_following_selector)
        category = scraper.get_text (category_selector)
        details = scraper.get_text (details_selector)
        web_page = scraper.get_text (web_page_selector)
        profile_link = scraper.driver.current_url

        # Save data in dictionary
        profile_data["profile_photo"] = f"{github_repo}/raw/master/imgs/{profile_photo_name.replace(' ', '%20')}"
        profile_data["profile_name"] = profile_name
        profile_data["name"] = name
        profile_data["num_posts"] = num_posts
        profile_data["num_followers"] = num_followers
        profile_data["num_following"] = num_following
        profile_data["category"] = category
        profile_data["details"] = details
        profile_data["web_page_text"] = web_page
        profile_data["web_page_link"] = f"https://{web_page}"
        profile_data["profile_link"] = profile_link

        # Get post info
        posts = []
        for post_current_num in range (1, post_num+1):

            # Generate selectors
            post_row = math.ceil (post_current_num/3)
            post_column = post_current_num - ((post_row -1) * 3)

            selector_post_base = f"article._aayp div div ._ac7v._aang:nth-child({post_row}) div:nth-child({post_column})"
            post_link_selector = f"{selector_post_base} a"
            post_img_selector = f"{selector_post_base} img"

            # Get links
            post_link = scraper.get_attrib (post_link_selector, "href")
            post_img = scraper.get_attrib (post_img_selector, "src")

            #  Download post image
            post_img_name = f"{profile} post {post_current_num}.jpg"
            try:
                download_image (post_img, post_img_name)
            except:
                continue

            # save current post data
            posts.append ({
                "image": f"{github_repo}/raw/master/imgs/{post_img_name.replace(' ', '%20')}",
                "url": post_link
            })

        # Save posts data
        profile_data["posts"] = posts
    
        # Save all profile data
        data[profile] = profile_data

    # save data in json file
    with open (json_path, "w") as file:
        file.write (json.dumps(data))

def upload_github ():
    """Do a commit and push to github, for update images and data  file
    """

    # Change folder
    current_folder = os.path.dirname(__file__)
    os.chdir (current_folder)

    # make commit and upload to github
    time_str = str(datetime.datetime.now())[:22]

    # Commit and push files
    os.system (f'git add -A')
    os.system (f'git commit -m "update {time_str}"')
    os.system (f'git push origin master')


if __name__ == "__main__":
    save_data()
    upload_github ()