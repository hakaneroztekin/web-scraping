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

#mpl .use('agg') # agg backend is to create plot as a .png file

# Website to be scraped
website_homepage = "https://yokatlas.yok.gov.tr/"

# List of all the universities in Turkey that has Computer Engineering undergraduate program
source = "https://yokatlas.yok.gov.tr/lisans-bolum.php?b=10024"

# To be used in the loop as a variable to keep URL for each university
university_url_list = []

university_list = []  # to keep list of universities

# Regions and Universities In That Regions
bolge_akdeniz_list = []
bolge_dogu_anadolu_list = []
bolge_ege_list = []
bolge_guneydogu_anadolu_list = []
bolge_ic_anadolu_list = []
bolge_marmara_list = []
bolge_karadeniz_list = []
all_regions = []

# Universities In The Regions
universities_in_akdeniz = []
universities_in_dogu_anadolu = []
universities_in_ege = []
universities_in_guneydogu_anadolu = []
universities_in_ic_anadolu = []
universities_in_marmara = []
universities_in_karadeniz = []
all_universities = []

quotas_for_akdeniz = []
quotas_for_dogu_anadolu = []
quotas_for_ege = []
quotas_for_guneydogu_anadolu = []
quotas_for_ic_anadolu = []
quotas_for_marmara = []
quotas_for_karadeniz = []

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

def initialize_all_universities():
    global all_universities, universities_in_akdeniz, universities_in_dogu_anadolu, universities_in_ege
    global universities_in_guneydogu_anadolu, universities_in_ic_anadolu, universities_in_marmara, universities_in_karadeniz

    all_universities.append(universities_in_akdeniz)
    all_universities.append(universities_in_dogu_anadolu)
    all_universities.append(universities_in_ege)
    all_universities.append(universities_in_guneydogu_anadolu)
    all_universities.append(universities_in_ic_anadolu)
    all_universities.append(universities_in_marmara)
    all_universities.append(universities_in_karadeniz)


def initialize_regions():
    global bolge_akdeniz, bolge_akdeniz_list
    bolge_akdeniz = "Adana, Antalya, Burdur, Hatay, Isparta,  Kahramanmaraş, Mersin, Osmaniye"
    bolge_akdeniz_list = convert_to_list(bolge_akdeniz)
    all_regions.append(bolge_akdeniz_list)

    global bolge_dogu_anadolu, bolge_dogu_anadolu_list
    bolge_dogu_anadolu = "Ağrı, Ardahan, Bingöl, Bitlis, Elazığ, Erzincan, Erzurum, Hakkari, Iğdır, Kars, Malatya, Muş, Tunceli, Van"
    bolge_dogu_anadolu_list = convert_to_list(bolge_dogu_anadolu)
    all_regions.append(bolge_dogu_anadolu_list)

    global bolge_ege, bolge_ege_list
    bolge_ege = "Afyonkarahisar, Aydın, Denizli, İzmir, Kütahya, Manisa, Muğla, Uşak"
    bolge_ege_list = convert_to_list(bolge_ege)
    all_regions.append(bolge_ege_list)

    global bolge_guneydogu_anadolu, bolge_guneydogu_anadolu_list
    bolge_guneydogu_anadolu= "Adıyaman, Batman, Diyarbakır, Gaziantep, Mardin, Siirt, Şanlıurfa, Şırnak, Kilis"
    bolge_guneydogu_anadolu_list = convert_to_list(bolge_guneydogu_anadolu)
    all_regions.append(bolge_guneydogu_anadolu_list)

    global bolge_ic_anadolu, bolge_ic_anadolu_list
    bolge_ic_anadolu = "Aksaray, Ankara, Çankırı, Eskişehir, Karaman, Kayseri, Kırıkkale, Kırşehir, Konya, Nevşehir, Niğde, Sivas, Yozgat"
    bolge_ic_anadolu_list = convert_to_list(bolge_ic_anadolu)
    all_regions.append(bolge_ic_anadolu_list)

    global bolge_marmara, bolge_marmara_list
    bolge_marmara = "Balıkesir, Bilecik, Bursa, Çanakkale, Edirne, İstanbul, Kırklareli, Kocaeli, Sakarya, Tekirdağ, Yalova"
    bolge_marmara_list = convert_to_list(bolge_marmara)
    all_regions.append(bolge_marmara_list)

    global bolge_karadeniz, bolge_karadeniz_list
    bolge_karadeniz = "Amasya, Artvin, Bartın, Bayburt, Bolu, Çorum, Düzce, Giresun, Gümüşhane, Karabük, Kastamonu, Ordu, Rize, Samsun, Sinop, Tokat, Trabzon, Zonguldak"
    bolge_karadeniz_list = convert_to_list(bolge_karadeniz)
    all_regions.append(bolge_karadeniz_list)



def convert_to_list(string):
    result = [x.strip() for x in string.split(',')]
    return result


def add_to_region(university):
    # iterate through all the cities in all the regions
    for index in range(len(all_regions)):
        for j in range(len(all_regions[index])):
            #print(region[i])
            if re.search(university.city, all_regions[index][j], re.IGNORECASE):  # ignore case sensitivity and search for the match
                # indexes in all_regions and all_universities are the same for same regions
                # so we can directly use the same index to add the university to that region
                all_universities[index].append(university)
                #print("added")

def make_int(s):
    s = s.strip()
    list_of_decimals_in_s = re.findall(r'\d+', s)
    decimals_as_string = ''.join(list_of_decimals_in_s)
    return int(decimals_as_string) if decimals_as_string else 0  # return as integer, and return 0 if blank

def initialize_quotas():
    print("Initializing quotas for the regions")

    for i in range(len(universities_in_akdeniz)):
        quota = make_int(universities_in_akdeniz[i].quota)
        if quota is not 0:
            quotas_for_akdeniz.append(int(universities_in_akdeniz[i].quota))

    for i in range(len(universities_in_dogu_anadolu)):
        quota = make_int(universities_in_dogu_anadolu[i].quota)
        if quota is not 0:
            quotas_for_dogu_anadolu.append(int(universities_in_dogu_anadolu[i].quota))

    for i in range(len(universities_in_ege)):
        quota = make_int(universities_in_ege[i].quota)
        if quota is not 0:
            quotas_for_ege.append(int(universities_in_ege[i].quota))

    for i in range(len(universities_in_guneydogu_anadolu)):
        quota = make_int(universities_in_guneydogu_anadolu[i].quota)
        if quota is not 0:
            quotas_for_guneydogu_anadolu.append(int(universities_in_guneydogu_anadolu[i].quota))

    for i in range(len(universities_in_ic_anadolu)):
        quota = make_int(universities_in_ic_anadolu[i].quota)
        if quota is not 0:
            quotas_for_ic_anadolu.append(int(universities_in_ic_anadolu[i].quota))

    for i in range(len(universities_in_marmara)):
        quota = make_int(universities_in_marmara[i].quota)
        if quota is not 0:
            quotas_for_marmara.append(int(universities_in_marmara[i].quota))

    for i in range(len(universities_in_karadeniz)):
        quota = make_int(universities_in_karadeniz[i].quota)
        if quota is not 0:
            quotas_for_karadeniz.append(int(universities_in_karadeniz[i].quota))

    print("Initializing quotas for the regions completed")


if __name__ == '__main__':

    # To create a Boxplot, we need to classify universities based on their regions.
    # Before that, let's fill the regions list
    initialize_regions()

    # Just append university lists based on regions to all_universities list
    initialize_all_universities()

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

        url = re.findall(r'\d+', university_url_list[i])
        university_url_list[i] = url

        print("Extracting the university url is completed", "(total ", i, "/", len(university_url_list), ")")

        # Fetch Data for All Universities, Create University class objects and Store them in university_list.
        #print("Fetching the first 20 university for plotting purposes!")

    for i in range(len(university_url_list)):
        university = University()

        #for i in range(len(university_url_list)):
        url_as_string = ''.join(university_url_list[i])
        university.url = url_as_string
        # Let's get University's City information in their homepage
        # Example URL: https://yokatlas.yok.gov.tr/2017/lisans.php?y=106510077
        university_profile_url = website_homepage + "lisans.php?y=" + url_as_string
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

        print("Fetching Name & City for id ", i, " is completed", "( total ", i, "/", len(university_url_list), ")")


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

        print("Fetching Program Code for id ", i, "is completed", "( total ", i, "/", len(university_url_list), ")")


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

        print("Fetching Quota for id ", i, " is completed", "( total ", i, "/", len(university_url_list), ")")
        print("###########################################")

        university_list.append(university)

        # Match University Cities with Regions and Create Lists of Universities Based On Their Region
        add_to_region(university)


    print("Fetching completed.")



    # Create Boxplot
    print("Creating Boxplot...")

    # Strip City Information from Universities in the Region Lists
    initialize_quotas()


    box_plot_data = [quotas_for_akdeniz,
                     quotas_for_dogu_anadolu,
                     quotas_for_ege,
                     quotas_for_guneydogu_anadolu,
                     quotas_for_ic_anadolu,
                     quotas_for_marmara,
                     quotas_for_karadeniz]


    print("Boxplotting the data.")
    try:
        plt.boxplot(box_plot_data,
                    patch_artist=True,
                    labels=['Akdeniz', 'Dogu Anadolu', 'Ege', 'Guneydogu Anadolu',
                            'Ic Anadolu', 'Marmara', 'Karadeniz'])
        plt.show()
        print("Data is plotted as boxplot, exiting")
    except:
        print("Boxplotting failed")
    # Save the figure
    # fig.savefig('fig1.png', bbox_inches='tight')