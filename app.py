# Scrap and Visualize Data
# Data Source: https://yokatlas.yok.gov.tr/lisans-bolum.php?b=10024
#
# For all the universities in Turkey that has Computer Engineering undergraduate program,
# visualize the following for year 2017:
# 1- Use boxplot to visualize quote ("kontenjan") wrt. region of universities
# 2- Use scatterplot to visualize the relation btw. average net math questions in YGS and lowest student rank.
#    Find r square for this relation.
#
# Implementation Steps:
# + 1- Scrap the data from the source.
# + 2- Improve the data scraping
# > +Get clear URL's for each university
# > +Get Quota for Specific University
# > +Get University's City
# > +Get Quota & City for All Universities'
#
# 3- Use boxplot
#
# 4- Use scatterplot
# > Relate Universitys' City with Region
# > Use scatterplot
#
# 5- Wrap-up & Upload the project
#


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

import json
import re

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl .use('agg') # agg backend is to create plot as a .png file

# Website to be scraped
website_homepage = "https://yokatlas.yok.gov.tr/"

# List of all the universities in Turkey that has Computer Engineering undergraduate program
source = "https://yokatlas.yok.gov.tr/lisans-bolum.php?b=10024"

# To be used in the loop as a variable to keep URL for each university
university_url_list = []

university_list = []  # to keep list of universities


class University:
    def __init__(self):
        self.name = ""
        self.program_code = ""  # There are multiple pages with same name, they differ in the program code
        self.url = ""
        self.city = ""
        self.quota = 0  # "kontenjan"
        self.region = ""  # region in Turkey

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


if __name__ == '__main__':
    # 1- Scrap the data from the source.
    raw_html = simple_get(source)
    #print(len(raw_html))

    # 2- Improve the data scraping
    # Now that we got the raw_html, we need to select and extract the data needed.
    # For that, we will use BeautifulSoup.
    try:
        html = BeautifulSoup(raw_html, 'html.parser')
    except:
        print("Parse error (1)")

    # Here we can list URL's of each university's own page
    # When we will be able to fetch one university's quotas, this will be used to fetch all universities' quotas.
    try:
        for h4 in html.select('h4'):
            # print(h4.a['href'])
            university_url_list.append(h4.a['href'])
    except:
        print("Fetching error (1)")

    print("Fetching university url list is completed")

    # remove the (unnecessary) last element
    university_url_list.remove('netler-tablo.php?b=10024')
    #print(university_url_list)

    # Each item is in the form: lisans.php?y=<id> For example lisans.php?y=106510077
    # We need to extract only the ID part
    for i in range(len(university_url_list)):
        print("Looping through the university url list")
        university = University()

        url = re.findall(r'\d+', university_url_list[i])
        university_url_list[i] = url

        print("Extracting the university url is completed", "(total ", i, "/", len(university_url_list), ")")

        # Fetch Data for All Universities, Create University class objects and Store them in university_list.
        print("Fetching 10 university for plotting purposes!")
        for i in range(10):
            #for i in range(len(university_url_list)):
            url_as_string = ''.join(university_url_list[i])
            university.url = url_as_string
            # Let's get University's City information in their homepage
            # Example URL: https://yokatlas.yok.gov.tr/2017/lisans.php?y=106510077
            university_profile_url = website_homepage + "2017/lisans.php?y=" + url_as_string
            #print(university_profile_url)

            profile_page_html = simple_get(university_profile_url)

            try:
                profile_page_parsed = BeautifulSoup(profile_page_html, 'html.parser')
            except:
                print("Parse error (2)")

            # Get Name and City Attributes
            try:
                # <div class="panel" style="margin:0px;background-color:#646464;">
                for div in profile_page_parsed.findAll('div', {"style": "margin:0px;background-color:#646464;"}):
                    name_and_city = div.h3.get_text()  # example: ABDULLAH GÜL ÜNİVERSİTESİ (KAYSERİ)
                    name = re.search(r'(.*?)\(', name_and_city).group(1)  # ABDULLAH GÜL ÜNİVERSİTESİ
                    city = re.search(r'\((.*?)\)', name_and_city).group(1)  # KAYSERİ
                    university.name = name
                    university.city = city
                    #print(city)
            except:
                print("Fetching error (2)")

            print("Fetching Name & City for id ", i, " is completed", "(total ", i, "/", len(university_url_list), ")")


            # Get Program Name
            try:
                # <div class="panel" style="margin:0px;background-color:#646464;">
                for h2 in profile_page_parsed.findAll('h2', {"class": "panel-title pull-left"}):
                        # example: ANKARA ÜNİVERSİTESİ - Bilgisayar Mühendisliği (101110581) | YÖK Lisans Atlası
                        text = h2.get_text()
                        if 'Program' in text:
                            program_code = re.findall(r'\d+', text)
                            program_code_as_string = ''.join(program_code)
                            university.program_code = program_code_as_string
                            # print(university.program_code)
            except:
                print("Fetching error (3)")

            print("Fetching Program Code for id ", i, "is completed", "(total ", i, "/", len(university_url_list), ")")


            # From this point on, let's try to fetch one university's quota's.
            quota_request_url = website_homepage + "2017/content/lisans-dynamic/1000_2.php?y=" + url_as_string
            #print(quota_request_url)

            quota_page_html = simple_get(quota_request_url)
            try:
                quota_page_parsed = BeautifulSoup(quota_page_html, 'html.parser')
                #print(BeautifulSoup.prettify(quota_page_parsed))
            except:
                print("Parse error (3)")

            try:
                for td in quota_page_parsed.findAll('td', {"class": "tdr text-center"}):
                    quota = td.get_text()
                    university.quota = quota
                #print(quota)
            except:
                print("Fetching error (4)")

            print("Fetching Quota for id ", i, " is completed")

            university_list.append(university)
            #print(university.city, " ", university.quota)

        print("Fetching completed.")

        # To create a Boxplot, we need to classify universities based on their regions.
        

        # # Create Boxplot
        # print("Creating Boxplot...")
        #
        # # box_plot_data = []
        # #
        # # for i in range(len(university_list)):
        # #     box_plot_data.append(university_list[i].quota)
        #
        # value1 = [82, 76, 24, 40, 67, 62, 75, 78, 71, 32, 98, 89, 78, 67, 72, 82, 87, 66, 56, 52]
        # value2 = [62, 5, 91, 25, 36, 32, 96, 95, 3, 90, 95, 32, 27, 55, 100, 15, 71, 11, 37, 21]
        # value3 = [23, 89, 12, 78, 72, 89, 25, 69, 68, 86, 19, 49, 15, 16, 16, 75, 65, 31, 25, 52]
        # value4 = [59, 73, 70, 16, 81, 61, 88, 98, 10, 87, 29, 72, 16, 23, 72, 88, 78, 99, 75, 30]
        #
        # box_plot_data = [value1, value2, value3, value4]
        #
        # # Create a figure instance
        # fig = plt.figure(1, figsize=(15, 10))
        #
        # # Create an axes instance
        # ax = fig.add_subplot(111)
        #
        # # Create the boxplot
        # bp = ax.boxplot(box_plot_data)
        #
        # # Save the figure
        # fig.savefig('fig1.png', bbox_inches='tight')