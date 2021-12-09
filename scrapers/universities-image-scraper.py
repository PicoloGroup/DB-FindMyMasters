"""
Scraper for collecting up-to-date image urls for universities.

author: @firattamur
"""


import csv
import json 
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


# folder path
PATH        = "../data-version2/raw/universities/"
BACKUP_PATH = "../data-version2/raw/master-programs/backup-while-scraping/"

# total number of pages for all programs
PAGE_COUNT = 200

# columns for csv file
CSV_COLUMNS = ["name", "image_url"]


def _collect_single_university_image_url(url: str, verbose: bool = False) -> tuple:
    """

    Request a single page from website and collect university image url.

    :param url    : page url for the website
    :param verbose: print details of request

    :return   : university name and image url

    """
    image_url : str = ""

    # request the page
    page = requests.get(url, timeout=2)

    # parse page 
    soup = BeautifulSoup(page.content, "html.parser")

    # get url from page
    data = soup.findAll('div', attrs={ 'class' : 'logo' })

    for div in data:

        urls = div.findAll('img', attrs={ 'class' : 'mt-sm-2'})

        for url in urls:
            
            if url["src"] is not None:
                university= url["alt"]
                image_url = url["src"]

    return tuple([university, image_url])

def collect_all_university_image_urls(read_from_csv: str, csv_name: str) -> None:
    """

    Request all pages for master programs and collect image url of university

    :param read_from_csv: name of the CSV file keep master program urls
    :param csv_name     : name of .csv file to keep image urls
    :param verbose      : print details of request

    :return: list of program urls

    """
    csv_name = f"{PATH}{csv_name}.csv"
    read_from_csv = f"{PATH}{read_from_csv}.csv"
    image_urls : dict[str, str] = {}

    print("Collecting University Image Urls...")
    # write all programs details into .csv file
    with open(read_from_csv, 'r', encoding='UTF8', newline='') as f:
        reader = csv.reader(f)

        index = 0
        # read master programs
        for line in reader:

            index += 1
            
            try:

                university, image_url = _collect_single_university_image_url(url=line[1])

                if image_url != '':
                    image_urls[university] = image_url

                if index % 100 == 0:
                    print(f"Collected {index}. Image Urls Count: {len(image_urls)}")

            except:

                continue

    university_image_urls: list = []

    # write university name and url to single list
    for university in image_urls.keys():
        university_image_urls.append([university, image_urls[university]])

    # write all programs details into .csv file
    with open(csv_name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(CSV_COLUMNS)

        # write multiple rows
        writer.writerows(university_image_urls)
    

def collect():
    """

    Collect master programs data.

    """

    # collect list of all programs
    # _collect_single_university_image_url(url="https://www.masterstudies.com/MS-Supply-Chain-Logistics-and-Innovations/France/EM-Normandie/")

    # collect details of programs and save to .csv
    collect_all_university_image_urls(read_from_csv="master-programs-url", csv_name="universities-image-urls")
    

if __name__ == "__main__":

    # start scraping
    collect()









