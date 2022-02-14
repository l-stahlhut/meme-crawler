#!usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Laura Stahlhut
# Date: 18.12.2021

"""
Web crawler for memes on imgflip.com where users can generate and search memes.
This code scrapes meme text, author, number of views, upvotes & comments as well as URL and jpg-file of the meme.
See README.md for information on how to use the code.
"""

import argparse
import requests # gets content of requested web page
from bs4 import BeautifulSoup #web scraping library
import time
import json
import csv
import os
from os import path
import shutil


parser = argparse.ArgumentParser(description="Crawl some memes from the site imgflip.com.")
parser.add_argument("-src", "--source", required=True, help="Base URL from the first site of the meme category you'd like to crasl (independant on whether or not you want to crawl memes from the first page). Make sure to sort the memes as you wish beforehand, e.g. https://imgflip.com/meme/But-Thats-None-Of-My-Business?sort=top-365d.", type=str)
parser.add_argument("-f_p", "--first_page", default=1, help="First page to be crawled (default is page 1).", type=int)
parser.add_argument("-t_p", "--last_page", required=True, help="Last page to be crawled.", type=int)
parser.add_argument("-d", "--delay", default=2, help="Delay between page loads", type=int)
parser.add_argument('-jpg', '--write_to_json', action="store_true", help='Write fetched memes to json file.')
parser.add_argument('-csv', '--write_to_csv', action="store_true", help='Write fetched memes to json file.')
parser.add_argument("-si", '--save_images', action="store_true", help='Save all scraped images as jpg-files.')


def get_meme_data(meme):
    """
    Get meme info: Text, author, views, upvotes, comments, url
    And save that information in a dictionary.
    """
    # get meme author
    meme_info = meme.find("div", class_ = "base-info")
    meme_author = meme_info.find("div", class_ = "base-author").text[3:] #remove "by "

    # get counts for views, comments, upvotes
    meme_counts = meme_info.find("div", class_ = "base-view-count").text.split(", ")

    categories = []

    # do upvotes and/or comments exist?
    for i in meme_counts:
        category = i.split()[1]
        categories.append(category)
        meme_views = meme_counts[0].split()[0]  # number of views (always available)

        if len(categories) == 3:  #views, upvotes, comments
            meme_upvotes = meme_counts[1].split()[0]
            meme_comments = meme_counts[2].split()[0]
        elif len(categories) == 2:
            if "upvotes" in categories or "upvote" in categories: #views, upvotes
                meme_upvotes = meme_counts[1].split()[0]
                meme_comments = 0
            if "comments" in categories or "comment" in categories: # views, comments
                meme_upvotes = 0
                meme_comments = meme_counts[1].split()[0]
        elif len(categories) == 1:  # only views
            meme_upvotes = 0
            meme_comments = 0

    # get meme text and url
    meme_wrap_wrap = meme.find("div", class_ = "base-img-wrap-wrap")
    meme_wrap = meme_wrap_wrap.find("div", class_ = "base-img-wrap")
    meme_base = meme_wrap.find("a", class_ = "base-img-link")

    # NSFW memes: text and url are censored in case the NSFW option is disabled
    try:
        meme_text = meme_base.find("img", class_ = "base-img")["alt"].split("|")[1].replace("\t"," ").replace("\n"," ").strip()
    except AttributeError: # catch cases without text
        meme_text = "NA" # no text because Meme is NSFW

    try:
        meme_url = meme_base.find("img", class_="base-img")["src"][2:]
    except AttributeError:
        meme_url = "NA" # no url because Meme is NSFW

    # put info into dictionary
    meme_data = {
        "text": meme_text,
        "author": meme_author,
        "views": meme_views,
        "upvotes": meme_upvotes,
        "comments": meme_comments,
        "url": meme_url
    }
    return meme_data


def write_to_json(fetched_memes):
    """
    Writing fetched memes to json in the following format:
    Output: A JSON file with the following format:

    {
        "name": "But that's none of my business",
        "memes": [{
            "text": "YOUR NOT GUNNA LIKE THIS POST; BUT THAT'S NONE OF MY BUSINESS",
            "author": "DeadMeme31YT",
            "views": 20,588,
            "upvotes": 504,
            "comments": 27,
            "url": "i.imgflip.com/52yb3d.jpg"

        }, ...]
    }
    """
    output_filename = args.source.split("/")[-1].replace("-", "_").lower() + ".json"

    with open(output_filename, "w") as out_file:
        data = {
            "name": meme_name,
            "memes": fetched_memes
        }
        out_file.write(json.dumps(data))

def write_to_csv(fetched_memes):
    """
    Writing fetched memes to csv in the following format (tab seperated):
    text | author | views | upvotes | comments | url
    YOUR NOT GUNNA LIKE THIS POST; BUT THAT'S NONE OF MY BUSINESS | DeadMeme31YT | 20,588 | 504 | 27 | i.imgflip.com/52yb3d.jpg
    """
    output_filename = args.source.split("/")[-1].replace("-", "_").lower() + ".csv"
    keys = fetched_memes[0].keys()

    with open(output_filename, 'w', newline='') as out_file:
        dict_writer = csv.DictWriter(out_file, keys, delimiter = '\t') # tab seperated file (not comma because commas occur in meme text)
        dict_writer.writeheader()
        dict_writer.writerows(fetched_memes)

def save_images(fetched_memes):
    # check if image folder already exists
    folder_name = "images_" + meme_name.lower().replace(" ", "_") + "/"
    if path.exists(folder_name):
        print("\nFolder ", folder_name, " already exists. Please rename existing folder to create a new one.")

    else:
        # create new folder to save images in
        os.mkdir(folder_name)

        for meme in fetched_memes:
            # get (short)URL to create image name
            url_raw = meme["url"]
            if url_raw != "NA":  # URL is "NA" for censored NSFW memes
                outfile_name = url_raw.replace("i.imgflip.com/", "")

                # complete URL to download image and save it to the correct folder
                url = "https://" + url_raw
                new_path = os.path.join(folder_name, outfile_name)

                # download images
                response = requests.get(url, stream=True)
                with open(new_path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
            else: # censored NSFW memes can't be downloaded (create account to get access to those images)
                pass

        print("Images saved in folder ", folder_name)

def main():
    """
    Parse arguments, fetch memes, create output.
    """
    # parse command line arguments
    global args
    args = parser.parse_args()

    # get meme name and output file name
    global meme_name
    meme_name = args.source.split("/")[-1].replace("-", " ")

    output_filename = args.source.split("/")[-1].replace("-", "_").lower() + ".json"

    # iterate over pages, fetch memes
    fetched_memes = []

    base_URL = str(args.source) # URL of the first page, e.g. https://imgflip.com/meme/But-Thats-None-Of-My-Business?sort=top-365d

    for i in range(args.first_page, args.last_page + 1):  # from start to chosen page number

        # print progress to terminal
        print(f"Processing page {i}")

        # adjust link because first site is different from other pages:
        # page 1: https://imgflip.com/meme/But-Thats-None-Of-My-Business?sort=top-365d
        # other pages: https://imgflip.com/meme/But-Thats-None-Of-My-Business?sort=top-365d&page=2
        if i != 1:
            link = f"{base_URL}&page={i}"
        else:
            link = base_URL

        # get html text for site
        html = requests.get(link, allow_redirects=False)
        html_text = html.text

        # create beautifulsoup instance for each page
        body = BeautifulSoup(html_text, 'lxml')

        if html.status_code != 200:
            # Something went wrong (e.g. page limit)
            break

        # find individual memes on page
        memes = body.find_all("div", class_ ="base-unit clearfix")

        # get data for all memes
        for meme in memes:
            fetched_memes.append(get_meme_data(meme))

        time.sleep(args.delay)  #todo find out what that is

    print(f"\nFetched: {len(fetched_memes)} memes") # print progress to terminal

    # create output with fetched memes if flag(s) is/are set. Otherwise, print to terminal.
    if args.write_to_json:
        write_to_json(fetched_memes)
    elif args.write_to_csv:
        write_to_csv(fetched_memes)
    else:
        print("\nFetched memes: \n\n", fetched_memes)

    # save jpg files if flag is set
    if args.save_images:
        save_images(fetched_memes)

    print("\nDone!")

if __name__ == '__main__':
    main()

