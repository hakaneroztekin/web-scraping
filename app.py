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
# 1- Scrap the data from the source.
# 2- Improve the data scraping
# 3- Use boxplot
# 4- Use scatterplot
# 5- Wrap-up & Upload the project
#


from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

import json
import re

# Website to be scraped
website_homepage = "https://yokatlas.yok.gov.tr/"

# List of all the universities in Turkey that has Computer Engineering undergraduate program
source = "https://yokatlas.yok.gov.tr/lisans-bolum.php?b=10024"

# To be used in the loop as a variable to keep URL for each university
university_url_list = []
quota_found = 0

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
    html = BeautifulSoup(raw_html, 'html.parser')

    # Here we can list URL's of each university's own page
    # When we will be able to fetch one university's quotas, this will be used to fetch all universities' quotas.
    try:
        for h4 in html.select('h4'):
            # print(h4.a['href'])
            university_url_list.append(h4.a['href'])
    except:
        print("Fetching error")

    # remove the (unnecessary) last element
    university_url_list.remove('netler-tablo.php?b=10024')
    #print(university_url_list)

    # Each item is in the form: lisans.php?y=<id> For example lisans.php?y=106510077
    # We need to extract only the ID part
    for i in range(len(university_url_list)):
        url = re.findall(r'\d+', university_url_list[i])
        university_url_list[i] = url

    url_as_string = ''.join(university_url_list[0])

    # From this point on, let's try to fetch one university's quota's.
    quota_request_url = website_homepage + "2017/content/lisans-dynamic/1000_2.php?y=" + url_as_string
    #print(quota_request_url)

    quota_page_html = simple_get(quota_request_url)
    quota_page_parsed = BeautifulSoup(quota_page_html, 'html.parser')
    #print(BeautifulSoup.prettify(quota_page_parsed))

    try:
        for td in quota_page_parsed.findAll('td', {"class": "tdr text-center"}):
            quota = td.get_text()

        #print(quota)

    except:
        print("Fetching error")

