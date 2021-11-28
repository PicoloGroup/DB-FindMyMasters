"""
Scraper for collecting up-to-date master programs 2022.

@firattamur
"""

import requests
from bs4 import BeautifulSoup


# base url for master programs
BASE_URL = "https://www.masterstudies.com/Masters-Degree/Programs/?page="

# total number of pages for all programs
PAGE_COUNT = 1201


def collect_program_urls_from_single_page(url: str, verbose: bool = False) -> list:
    """
    Request a single page from website all collect list of program urls.

    :param url    : page url for the website
    :param verbose: print result of request

    :return   : return list of program urls in single page

    """


def collect_program_urls(url: str, page_count: int) -> list:
    """

    Request all pages for master programs and collect url for each program.

    :param: url       : base url for the website
    :param: page_count: number of pages in website

    :return: list of program urls

    """

    program_urls: list[str] = []

    return program_urls


def collect_program_details()


if __name__ == "__main__":
    
    programs = collect_program_urls(url=BASE_URL, page_count=PAGE_COUNT)











