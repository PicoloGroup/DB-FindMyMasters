"""
Scraper for collecting up-to-date master programs 2022.

author: @firattamur
"""


import csv
import time
import json
import shutil
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


# base url for master programs
BASE_URL = "https://www.masterstudies.com/Masters-Degree/Programs/?page="

# folder path
PATH = "../data-version2/master-programs"
BACKUP_PATH = "../data-version2/master-programs/backup-while-scraping/"

# total number of pages for all programs
PAGE_COUNT = 700

# columns for csv file
CSV_COLUMNS = [
                "name", "university", "duration", "url",
                "language", "city", "country", "mode", "deadline",
                "pace", "tution_amount", "tution_currency"
            ]


def _collect_single_page_programs_url(url: str, verbose: bool = False) -> list:
    """

    Request a single page from website and collect list of program urls in page.

    :param url    : page url for the website
    :param verbose: print details of request

    :return   : return list of program urls in single page

    """
    programs_url : list[str] = []

    # request the page
    page = requests.get(url)

    # parse page 
    soup = BeautifulSoup(page.content, "html.parser")

    # get url from page
    data = soup.findAll('div', attrs={ 'class' : 'program_title' })

    for div in data:
        links = div.findAll('a')

        for a in links:
            programs_url.append(a["href"])

    return programs_url

def collect_all_programs_url(url: str, page_count: int, verbose: bool = False) -> list:
    """

    Request all pages for master programs and collect url for each program.

    :param: url       : base url for the website
    :param: page_count: number of pages in website
    :param verbose: print details of request

    :return: list of program urls

    """

    program_urls: list[str] = []

    for program in tqdm(range(1, page_count + 1)):

        # url for the single page
        page_url = BASE_URL + str(program)

        try:
            # get all program list in single page
            programs_in_single_page = _collect_single_page_programs_url(url = page_url)
            
            # add collected program urls to list
            program_urls.extend(programs_in_single_page)

            # in case of url request protection
            time.sleep(0.5)
        except:
            continue

    return program_urls


def _collect_single_program_details(url: str, verbose: bool = False) -> dict:
    """

    Request a single master program url from website collect details.

    :param url    : master program url for the website
    :param verbose: print details of request

    :return       : return details of program

    """

    program_details : list[str] = []

    # request the page
    page = requests.get(url)

    # parse page 
    soup = BeautifulSoup(page.content, "html.parser")

    # get url from page
    data = soup.findAll('locations')[0]

    # description details in html in a json
    soup_description = BeautifulSoup(json.loads(data[":default-language"])["description_html"], "html.parser")

    try:
        # get program details
        program = json.loads(data[":program"])

        program_details.append(program["name"])
    except:
        program_details.append("null")
 
    try:
        # university name
        program_details.append(data[":school"].strip('"'))
    except:
        program_details.append("null")

    try:
        # duration 
        program_details.append(data[":duration"].strip('"'))
    except:
        program_details.append("null")

    # program url
    try:
        program_details.append(soup_description.findAll('a')[0]["href"])
    except:
        program_details.append("null")

    # language
    try:
        program_details.append(data[":teaching-languages"])
    except:
        program_details.append("null")

    # location
    try:
        # get location json object to access city and country
        locations = json.loads(data[":program-locations"])[0]

        # city
        program_details.append(locations["city"])

        # country
        program_details.append(locations["country"])
    except:
        # city
        program_details.append("null")

        # countrys
        program_details.append("null")
        
    try:
        # mode
        program_details.append(data[":mode"])

    except:
        program_details.append("null")

    try:
        # deadline
        program_details.append(data[":deadline"])
    except:
        program_details.append("null")

    # pace
    try:
        program_details.append(data[":pace"])
    except:
        program_details.append("null")

    # tution
    try:
        # get location json object to access city and country
        price_info = json.loads(data[":price"])
        
        # amount
        if price_info["price_orig"]["amount"] is not None:
            program_details.append(price_info["price_orig"]["amount"])
        else:
            raise ValueError()

        # currency
        program_details.append(price_info["price_orig"]["currency"])

    except:
        program_details.append("null")

        program_details.append("null")

    return program_details    


def collect_all_programs_detail(program_urls: list, csv_name: str, backup_every: int, verbose: bool = False) -> list:
    """

    Request all program urls and save all programs detail in .csv file.

    :param url     : list of program urls to collect
    :param csv_name: name of .csv file.
    :param verbose : print details of request

    :return       : return all programs details

    """

    all_programs_detail : list[list[str]] = []

    index = 1

    for program_url in tqdm(program_urls):

        try:

            # get details of the program
            program_details = _collect_single_program_details(url = program_url)
        
        except:
            continue

        # append program details to all programs
        all_programs_detail.append(program_details)

        if index % backup_every == 0:

            backup_to = f"{BACKUP_PATH}{csv_name}-{index}.csv"

            if verbose:
                print(f"Collected {index}")
                print(f"Writing to {backup_to} file...")

            # write all programs details into .csv file
            with open(backup_to, 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)

                # write the header
                writer.writerow(CSV_COLUMNS)

                # write multiple rows
                writer.writerows(all_programs_detail)

        index += 1
    

def collect():
    """

    Collect master programs data.

    """

    # collect list of all programs
    program_urls = collect_all_programs_url(url=BASE_URL, page_count=PAGE_COUNT)

    # collect details of programs and save to .csv
    collect_all_programs_detail(program_urls=program_urls, csv_name="master-programs", backup_every=1000, verbose = True)
    

if __name__ == "__main__":

    # start scraping
    collect()









