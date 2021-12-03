"""
Scraper for collecting up-to-date city quality of living index 2022.

author: @firattamur
"""

import csv
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


# base url for master programs
BASE_URL = "https://www.numbeo.com/quality-of-life"

# folder path
PATH        = "../data-version2/raw/cities"
BACKUP_PATH = "../data-version2/raw/cities/backup-while-scraping"

CSV_COLUMNS = [

    "country",

    "Purchasing Power Index",
    "Purchasing Power Index Category",

    "Safety Index",
    "Safety Index Category",

    "Health Care Index",
    "Health Care Index Category",
    
    "Climate Index",
    "Climate Index Category",
    
    "Cost of Living Index",
    "Cost of Living Index Category",
    
    "Property Price to Income Ratio",
    "Property Price to Income Ratio Category",
    
    "Traffic Commute Time Index",
    "Traffic Commute Time Index Category",
    
    "Pollution Index",
    "Pollution Index Category",
    
    "Quality of Life Index",
    "Quality of Life Index Category",

]


def collect_country_urls(url: str) -> dict:
    """

    Collect countries url from the main page. 

    :param url: url for the main page.

    :return   : a set contains countries url.

    """

    countries : dict[str, str] = dict()

    # request the page
    page = requests.get(url)

    # parse page 
    soup = BeautifulSoup(page.content, "html.parser")

    # get url from page
    tables = soup.findAll('table', attrs={ 'class' : 'related_links' })

    for table in tables:

        urls = table.findAll('a')

        for url in urls:
            
            if url["href"] != "":

                # add name and url of the country
                countries[url.text] = f"{BASE_URL}/{url['href']}"

    return countries


def collect_city_urls(url: str, name: str) -> dict:
    """

    Collect cities from the specified country url.

    :param url : url for the country.
    :param name: name of the country.

    :return   : a set contains cities url.

    """

    # return city name and url
    cities : dict[str, str] = dict()

    # request the page
    page = requests.get(url)

    # parse page 
    soup = BeautifulSoup(page.content, "html.parser")

    # get url from page
    selects = soup.findAll('select', attrs={ 'id' : 'city' })

    # cities in a select tag
    for select in selects:

        options = select.findAll('option')

        for option in options:
            
            if option["value"] != "":
                
                # save city
                cities[option['value']] = f"{BASE_URL}/in/{option['value'].replace(' ', '-')}-{name}"
                cities[f"{option['value']}-2"] = f"{BASE_URL}/in/{option['value'].replace(' ', '-')}"

    return cities


def collect_quality_indexes(url: str) -> dict:
    """

    Collect quality of indexes for specified url.

    :param url: url for the city or country index page.

    :return: list of quality indexes

    """

    # quality index name and the values of the index
    quality_indexes : dict[str, list] = dict()

    # request the page
    page = requests.get(url)

    # parse page 
    soup = BeautifulSoup(page.content, "html.parser")

    # get url from page
    tables = soup.findAll('table')

    # quality of indexes table
    quality_table = tables[2]

    # get rows of table
    rows = quality_table.findAll('tr')

    for index, row in enumerate(rows):
        
        cols = row.findAll('td')

        if len(cols) == 1:
            continue

        # get name of index
        index_name  = cols[0].text.strip()
        index_value = cols[1].text.strip()
        index_group = cols[2].text.strip()

        if index == len(rows) - 1:
            quality_indexes[index_name[2:-1]] = [index_value, index_group]
        else:
            quality_indexes[index_name]       = [index_value, index_group]

    return quality_indexes


def collect_countries_and_cities_quality_indexes():
    """

    Collect country list and their quality indexes.
    
    :param csv_name: name of the csv file

    :return : return list of countries to collect city data

    """

    # country index in a list
    country_indexes_rows : list = list()

    # write all programs details into .csv file
    with open(f"{PATH}/city-quality-of-indexes.csv", 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(["city"] + CSV_COLUMNS)

    # get list of countries name and url
    country_urls = collect_country_urls(url=BASE_URL)

    # for each country get quality indexes
    for country in tqdm(country_urls.keys()):

        try:

            country_row : list = list()

            country_indexes = collect_quality_indexes(url=country_urls[country])

            country_row.extend(country_indexes["Purchasing Power Index"])
            country_row.extend(country_indexes["Safety Index"])
            country_row.extend(country_indexes["Health Care Index"])
            country_row.extend(country_indexes["Climate Index"])
            country_row.extend(country_indexes["Cost of Living Index"])
            country_row.extend(country_indexes["Property Price to Income Ratio"])
            country_row.extend(country_indexes["Traffic Commute Time Index"])
            country_row.extend(country_indexes["Pollution Index"])
            country_row.extend(country_indexes["Quality of Life Index"])

            country_indexes_rows.append([country] + country_row)

            city_indexes_rows    : list = list()

            # get city of country and collect city quality of indexes
            cities = collect_city_urls(url=country_urls[country], name=country)

            for city in tqdm(cities.keys()):

                city_row : list = list()

                try:

                    city_indexes = collect_quality_indexes(url=cities[city])

                    city_row.extend(city_indexes["Purchasing Power Index"])
                    city_row.extend(city_indexes["Safety Index"])
                    city_row.extend(city_indexes["Health Care Index"])
                    city_row.extend(city_indexes["Climate Index"])
                    city_row.extend(city_indexes["Cost of Living Index"])
                    city_row.extend(city_indexes["Property Price to Income Ratio"])
                    city_row.extend(city_indexes["Traffic Commute Time Index"])
                    city_row.extend(city_indexes["Pollution Index"])
                    city_row.extend(city_indexes["Quality of Life Index"])

                    if "-2" in city:
                        city_indexes_rows.append([city.strip("-2")] + [country] + city_row)
                    else:
                        city_indexes_rows.append([city] + [country] + city_row)

                except:

                    continue

            # write all programs details into .csv file
            with open(f"{PATH}/city-quality-of-indexes.csv", 'a', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)

                # write multiple rows
                writer.writerows(city_indexes_rows)
                        
        except:
            continue


    # write all programs details into .csv file
    with open(f"{PATH}/country-quality-of-indexes.csv", 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(CSV_COLUMNS)

        # write multiple rows
        writer.writerows(country_indexes_rows)


def collect():
    """

    Collect quality of index data for countries and cities.

    """

    collect_countries_and_cities_quality_indexes()

if __name__ == "__main__":

    # start scraping
    collect()
