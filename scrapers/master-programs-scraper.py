"""
Scraper for collecting up-to-date master programs 2022.

author: @firattamur
"""


import csv
import json 
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


# base url for master programs
BASE_URL = "https://www.masterstudies.com"

# folder path
PATH        = "../data-version2/master-programs/"
BACKUP_PATH = "../data-version2/master-programs/backup-while-scraping/"

# field of studies 
# this will helpful to categorize and recommend master programs to users
FIELDS = [

    "Administration-Studies",
    "Architecture-Studies",
    "Art-Studies",
    "Aviation",
    "Business-Studies",
    "Construction",
    "Cosmetology-Studies",
    "Design-Studies",
    "Economic-Studies",
    "Education",
    "Energy-Studies",
    "Engineering-Studies",
    "Environmental-Studies",
    "Fashion",
    "Food-and-Beverage-Studies",
    "General-Studies",
    "Health-Care",
    "Humanities-Studies",
    "Journalism-and-Mass-Communication",
    "Languages",
    "Law-Studies",
    "Life-Sciences",
    "Life-Skills",
    "Management-Studies",
    "Marketing-Studies",
    "Natural-Sciences",
    "Performing-Arts",
    "Professional-Studies",
    "Self-Improvement",
    "Social-Sciences",
    "Sport",
    "Sustainability-Studies",
    "Technology-Studies",
    "Tourism-and-Hospitality"

]


# total number of pages for all programs
PAGE_COUNT = 200

# columns for csv file
CSV_COLUMNS = [
                "field", "name", "university", "duration", "url",
                "language", "city", "country", "mode", "deadline",
                "pace", "tution_amount", "tution_currency"
            ]


def _collect_single_page_programs_url(url: str, verbose: bool = False) -> set:
    """

    Request a single page from website and collect list of program urls in page.

    :param url    : page url for the website
    :param verbose: print details of request

    :return   : return list of program urls in single page

    """
    programs_url : set[str] = set()

    # request the page
    page = requests.get(url, timeout=2)

    # parse page 
    soup = BeautifulSoup(page.content, "html.parser")

    # get url from page
    data = soup.findAll('div', attrs={ 'class' : 'program_title' })

    for div in data:
        links = div.findAll('a')

        for a in links:

            if a["href"] == "":
                continue

            programs_url.add(a["href"])

    return programs_url

def collect_all_programs_url(url: str, page_count: int, csv_name: str = "master-programs-url", verbose: bool = False) -> set:
    """

    Request all pages for master programs and collect url for each program.

    :param: url       : base url for the website
    :param: page_count: number of pages in website
    :param csv_name: name of .csv file to keep urls
    :param verbose: print details of request

    :return: list of program urls

    """
    save_to = f"{PATH}{csv_name}.csv"

    # write all programs details into .csv file
    with open(save_to, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(["field", "url"])

    print("Collecting Master Programs Url...")

    for field in FIELDS:

        program_urls: set[str] = set()

        print(field, end="")
        print()

        timeout_count = 0

        for program in tqdm(range(1, page_count + 1)):

            # if we have timeout 3 times than there will be no page no need to wait
            if timeout_count == 3:
                break

            # url for the single page
            page_url = f"{BASE_URL}/Masters-Degree/{field}/?page={program}"

            try:

                # get all program list in single page
                programs_in_single_page = _collect_single_page_programs_url(url = page_url)
                
                # add collected program urls to list
                program_urls.update(programs_in_single_page)

            except:
                
                # we did not get page we requested because of timeout
                # probably because page does not exist
                timeout_count += 1

                continue   

        print(f"{field} - Collected: {len(program_urls)}...")
            
        # write all programs details into .csv file
        with open(save_to, 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            for program in program_urls:
                # write multiple rows
                writer.writerow([field, program])
        
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


def collect_all_programs_detail(read_from_csv: str, csv_name: str, backup_every: int, verbose: bool = False) -> list:
    """

    Request all program urls and save all programs detail in .csv file.

    :param url     : list of program urls to collect
    :param csv_name: name of .csv file.
    :param verbose : print details of request

    :return       : return all programs details

    """

    all_programs_detail : list[list[str]] = []

    print("Collecting Master Programs Detail...")

    # path of csv file
    read_from_csv = f"{PATH}{read_from_csv}.csv"

    # row in csv file
    line_number = 0

    # write all programs details into .csv file
    with open(read_from_csv, 'r', encoding='UTF8', newline='') as f:
        
        reader = csv.reader(f)

        for row in tqdm(reader):
            
            if line_number == 0:
                line_number += 1
                continue
            
            try:

                program_field, program_url = row[0], row[1]

                # get details of the program
                program_details = _collect_single_program_details(url = program_url)

                program_details = [program_field] + program_details
            
            except:
                continue

            # append program details to all programs
            all_programs_detail.append(program_details)

            if line_number % backup_every == 0:

                backup_to = f"{BACKUP_PATH}{csv_name}-{line_number}.csv"

                if verbose:
                    print(f"Collected {line_number}")
                    print(f"Writing to {backup_to} file...")

                # write all programs details into .csv file
                with open(backup_to, 'w', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)

                    # write the header
                    writer.writerow(CSV_COLUMNS)

                    # write multiple rows
                    writer.writerows(all_programs_detail)

            line_number += 1

    csv_name = f"{PATH}{csv_name}.csv"

    # write all programs details into .csv file
    with open(csv_name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(CSV_COLUMNS)

        # write multiple rows
        writer.writerows(all_programs_detail)
    

def collect():
    """

    Collect master programs data.

    """

    # collect list of all programs
    # collect_all_programs_url(url=BASE_URL, page_count=PAGE_COUNT)

    # collect details of programs and save to .csv
    collect_all_programs_detail(read_from_csv="master-programs-url", csv_name="master-programs", backup_every=1000, verbose = True)
    

if __name__ == "__main__":

    # start scraping
    collect()









