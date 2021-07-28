import pandas as pd       # dataframe library

# Standard website libraries
import advertools as a    # parse sitemaps
import bs4                # html parsing
import requests           # python http requests


def generate_sitemap(num_sites):
    """ Parses the list of urls from a sitemap.xml.gz file, filtering for those urls that contain "\trail\" in the path.

    Args:
        num_sites: an integer representing the number of sites to parse, non-inclusive (e.g. passing in a sites value of
        1 will only parse site 0, where a sites value of 3 would parse sites 0, 1 and 2)

    Returns:
        d: a dictionary object
    """
    temp_df = pd.DataFrame()
    url_list = list()

    for i in range(0, num_sites):
        site_url = 'https://www.hikingproject.com/sitemap' + str(i) + '.xml.gz'
        temp_df = a.sitemap_to_df(site_url)
        temp_df = temp_df[temp_df["loc"].str.contains('\/trail\/')]["loc"]

        # only add the url to the list, not the index number from the dataframe
        for label, content in temp_df.items():
            url_list.append(content)

    return url_list


def scrape_page(site_url):
    """ Scrapes a given page for the desired fields.

    Args:
        site_url: the FQDN of the url to scrape

    Returns:
        d: a dictionary object that includes the following trail stats: site_url, trail_name, stars, difficulty, dist,
        trail_type, elev_high, elev_low, elev_gain, elev_lost, avg_grade, max_grade, dogs, features, gps_cords
    """
    page = requests.get(site_url)
    soup = bs4.BeautifulSoup(page.content, 'html.parser')

    # checks to make sure page exists
    if page.status_code == 200:
        trail_name = soup.find(id='trail-title').text.strip()
        difficulty = soup.find(class_='difficulty-text').text.strip()

        stats = soup.find(id='trail-stats-bar')
        stat_block = stats.find('div', class_='stat-block ml-2 mr-1 mt-1').text.strip().split('\n\n\n')
        dist = stat_block[0]
        trail_type = stat_block[2]
        stat_block2 = stats.find('div', class_='stat-block mx-1 mt-1').text.strip().split('\n\n')
        elev_high = (stat_block2[0]+stat_block2[2]).strip()
        elev_low = (stat_block2[3]+stat_block2[5]).strip()
        stat_block3 = stats.find('div', class_='stat-block mx-1 mt-1').nextSibling.nextSibling.text.strip().split('\n\n')
        elev_gain = (stat_block3[0]+stat_block2[2]).strip()
        elev_lost = (stat_block3[3]+stat_block2[5]).strip()
        stat_block4 = stats.find('div', class_='stat-block ml-1 mt-1').text.strip().split('\n')
        avg_grade = stat_block4[1].strip().replace("(", "").replace(")", "")
        max_grade = stat_block4[4].strip().replace("(", "").replace(")", "")

        # create dictionary with trail stats and return
        trail_stats = {'url': site_url, 'Name': trail_name, 'Difficulty': difficulty, 'Distance': dist, 'Type': trail_type,
                       'High Elev': elev_high, 'Low Elev': elev_low, 'Elev Gained': elev_gain, 'Elev Lost': elev_lost,
                       'Avg Grade': avg_grade, 'Max Grade': max_grade}

        return trail_stats
    else:
        return None


if __name__ == '__main__':
    """ The main function of the program.

    Args: none
    Returns: none
    """
    urls = list()
    df = pd.DataFrame(columns=['url', 'Name', 'Popularity', 'Difficulty', 'Distance', 'Type', 'High Elev', 'Low Elev',
                               'Elev Gained', 'Elev Lost', 'Avg Grade', 'Max Grade', 'Dogs', 'Features', 'GPS'])

    while True:
        val = input("\nMenu:\n"
                    "1: Scrape Sitemap\n"
                    "2: Print Sitemap Dataframe\n"
                    "3: Scrape Site\n"
                    "4: Export to CSV\n"
                    "5: Exit\n"
                    "Selection: ")
        if val == '1':
            val = input("\nNumber of sites to scrape (up to 100):  ")
            urls = generate_sitemap(int(val))
        elif val == '2':
            print(urls)
        elif val == '3':
            count = 0
            for url in urls:
                d = scrape_page(url)
                print('#' + str(count) + ' - Page scraped: ' + url)
                if d is not None:
                    df = df.append(d, ignore_index=True)
                count += 1
        elif val == '4':
            df.to_csv('data/tmp_trail_data.csv', index=False)
        elif val == '5':
            exit()
