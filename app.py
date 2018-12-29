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
# + 3- Use boxplot
#
# 4- Use scatterplot
#
# 5- Wrap-up & Upload the project
#

import re
from contextlib import closing

import matplotlib.pyplot as plt
import statsmodels.api as sm
from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

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

# For Scatter Plot
avg_mat_net_list = []
lowest_student_rank_list = []

class University:
    def __init__(self):
        self.name = ""
        self.program_code = ""  # There are multiple pages with same name, they differ in the program code
        self.url = ""
        self.city = ""
        self.quota = ""  # "kontenjan"
        self.region = ""  # region in Turkey

        # Note that, Lowest Student Rank is not available for almost all the universities for 2017.
        # Because we have to relate avg_maths with lowest_student_rank, the relation will fail.
        # Instead, to show the relation and scatterplot with quality, data for 2018 will be used.
        self.avg_math_2018 = 0
        self.lowest_student_rank = 0

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

def make_float(s):
    s = s.strip()
    float_s = float(s.replace(',', '.'))
    return float(float_s) if float_s else 0  # return as integer, and return 0 if blank


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
    print("Looping through the university url list")
    for i in range(len(university_url_list)):


        url = re.findall(r'\d+', university_url_list[i])
        university_url_list[i] = url

    print("Extracting the university url is completed", "(total ", i, "/", len(university_url_list)-1, ")")

        # Fetch Data for All Universities, Create University class objects and Store them in university_list.

    #print("Fetching the first 50 university for plotting purposes!")
    for i in range(len(university_url_list)):
        university = University()

        # Data For Scatter Plot
        math_avg = ""
        lowest_student_rank = ""

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

        print("Fetching Name & City for id ", i, " is completed", "( total ", i, "/", len(university_url_list)-1, ")")

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

        print("Fetching Program Code for id ", i, "is completed", "( total ", i, "/", len(university_url_list)-1, ")")

        # Get Average Net Math Questions in YGS 2017
        # Note that, Lowest Student Rank is not available for almost all the universities for 2017.
        # Because we have to relate avg_maths with lowest_student_rank, the relation will fail.
        # Instead, to show the relation and scatterplot with quality, data for 2018 will be used.
        avg_ygs_nets_request_url = website_homepage + "content/lisans-dynamic/1210a.php?y=" + url_as_string
        # Fetch URL Example: https://yokatlas.yok.gov.tr/content/lisans-dynamic/1210a.php?y=106910294

        avg_ygs_nets_page_html = simple_get(avg_ygs_nets_request_url)
        try:
            avg_ygs_nets_page_parsed = BeautifulSoup(avg_ygs_nets_page_html, 'html.parser')
        except:
            print("Parse error (3)")


        try:
            td_table = avg_ygs_nets_page_parsed.findAll('td')

            for index in range(len(td_table)):
                if td_table[index].get_text() == "TYT Matematik (40 soruda)":
                    math_avg = td_table[index+1].get_text()
                    #print(math_avg, university.name, avg_ygs_nets_request_url)
                    university.avg_math_2018 = math_avg

        except:
            print("Fetching error (3)")

        print("Fetching Avg Math Nets for id ", i, "is completed", "( total ", i, "/", len(university_url_list)-1, ")")

        # Get Lowest Student Rank for TYT in 2018
        # Note that, Lowest Student Rank is not available for almost all the universities for 2017.
        # Because we have to relate avg_maths with lowest_student_rank, the relation will fail.
        # Instead, to show the relation and scatterplot with quality, data for 2018 will be used.
        # Fetch URL Example: https://yokatlas.yok.gov.tr/content/lisans-dynamic/1230.php?y=106910294
        lowest_student_rank_request_url = website_homepage + "content/lisans-dynamic/1230.php?y=" + url_as_string
        # print(quota_request_url)

        lowest_student_rank_page = simple_get(lowest_student_rank_request_url)
        try:
            lowest_student_rank_page_parsed = BeautifulSoup(lowest_student_rank_page, 'html.parser')
        except:
            print("Parse error (4)")

        try:
            td_table = lowest_student_rank_page_parsed.findAll('td')
            lowest_student_rank = td_table[len(td_table)-2].get_text().strip()
            #print(lowest_student_rank)
            university.lowest_student_rank = lowest_student_rank


        except:
            print("Fetching error (4)")

        print("Fetching Lowest Student Rank for id ", i, "is completed", "( total ", i, "/", len(university_url_list)-1, ")")

        # Store Data for Scatter Plot

        try:
            #print(university.avg_math_2018, university.lowest_student_rank)
            math_avg_float = make_float(university.avg_math_2018)
            lowest_student_rank_int = make_int(university.lowest_student_rank)
            # check both for to ensure if they both are parsed successfully
            if math_avg_float is not 0 and lowest_student_rank_int is not 0:
                avg_mat_net_list.append(math_avg_float)
                lowest_student_rank_list.append(lowest_student_rank_int)

        except:
            print("Scatter Plot Data Initialization Error")

        # Get Quotas
        quota_request_url = website_homepage + "2017/content/lisans-dynamic/1000_2.php?y=" + url_as_string
        #print(quota_request_url)

        quota_page_html = simple_get(quota_request_url)
        try:
            quota_page_parsed = BeautifulSoup(quota_page_html, 'html.parser')
            #print(BeautifulSoup.prettify(quota_page_parsed))
        except:
            print("Parse error (5)")

        try:
            for td in quota_page_parsed.findAll('td', {"class": "tdr text-center"}):
                quota = td.get_text()
                university.quota = quota
            #print(quota)
        except:
            print("Fetching error (5)")

        print("Fetching Quota for id ", i, " is completed", "( total ", i, "/", len(university_url_list)-1, ")")
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
                    labels=['Akdeniz', 'Dogu A.', 'Ege', 'Guneydogu A.',
                            'Ic A.', 'Marmara', 'Karadeniz'])
        plt.xlabel('Regions')
        plt.ylabel('Quotas')
        plt.show()
        print("Data is plotted as boxplot, exiting")
    except:
        print("Boxplot failed")


    # Scatter Plot

    print("Creating ScatterPlot...")

    results = sm.OLS(lowest_student_rank_list, sm.add_constant(avg_mat_net_list)).fit()

    print("mat size:", len(avg_mat_net_list),
          "rank size:", len(lowest_student_rank))

    plt.scatter(avg_mat_net_list, lowest_student_rank_list)

    #plt.plot(avg_mat_net_list, b + m * avg_mat_net_list, '-')

    # X_plot = np.linspace(0, 1, 100)
    # plt.plot(X_plot, X_plot * results.params[0] + results.params[1])

    plt.xlabel('Average Math Net')
    plt.ylabel('Lowest Student Rank')
    plt.show()

    r_squared = results.rsquared
    print("R squared = ", r_squared)

    print("Data is plotted as ScatterPlot, exiting")



