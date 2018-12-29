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

# List of all the universities in Turkey that has Computer Engineering undergraduate program
source = "https://yokatlas.yok.gov.tr/lisans-bolum.php?b=10024"

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

    try:
        for h4 in html.select('h4'):
            print(h4.a['href'])  # might be improved to select among h4 titles, to exclude the last one
    except:
        print("Fetching error")

