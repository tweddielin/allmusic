import json, csv, requests, requests_cache
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd
from tqdm import tqdm
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def get_allgenre():
    #driver = webdriver.Chrome('/Users/Eddie/Documents/album_review/allmusic_scrape/chromedriver')
    driver = webdriver.PhantomJS()
    driver.get('http://www.allmusic.com/advanced-search')
    genres = driver.find_element_by_class_name('genres')
    #genres.find_element_by_tag_name('input').send_keys(target_genre)
    page = driver.page_source
    driver.quit()
    soup = bs(page, "lxml")
    genre_list = []
    #for row in soup.findAll('li',{'style': 'display: list-item;'}):
    for row in soup.find('div',{'class':'options'}).findAll('li'):
        genre_dict = {}
        try:
            genre_dict['genre'] = " ".join(row.text.split())
        except KeyError:
            genre_dict['genre'] = target_genre.lower()

        try:
            genre_dict['genre_id'] = row['data-parent']
        except KeyError:
            genre_dict['genre_id'] = None

        try:
            genre_dict['subgenre_id'] = row.find('input')['id']
        except KeyError:
            genre_dict['subgenre_id'] = None

        genre_list.append(genre_dict)

    genre_df = pd.DataFrame(genre_list)
    genre_df.to_csv('data/genres.csv')
    return  genre_df

def scrape_albums(genre_name, genre_id):
    req = requests.Session()
    requests_cache.install_cache('allmusic')
    headers = {'referer':'http://www.allmusic.com/advanced-search','user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'}
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap['phantomjs.page.settings.userAgent'] = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87')
    #payload = {'filters[]': 'subgenreid:MA0000002451', 'sort': ''}
    #link = 'http://www.allmusic.com/advanced-search/results/{0}'

    albums = []
    albums_mood = []
    albums_url = []
    artists = []
    artists_url = []
    rating = []
    years = []
    item_ids = []
    page_no = 0
    album_num = 0
    print('Start Scraping {} ...'.format(genre_name))
    payload = {'filters[]': genre_id, 'sort': ''}
    link = 'http://www.allmusic.com/advanced-search/results/{0}'

    while True:
        print('page no', page_no)
        site = req.post(link.format(str(page_no) if page_no>0 else ''), data=payload, headers=headers).text
        if 'desktop-results' not in site:
            print('nothing for page number', page_no)
            break
        if 'http://www.allmusic.com/album/' not in site:
            print('nothing for page number',page_no)
            break
        page_no += 1
        table = site.split('<tbody>')[1].split('/tbody>')[0]
        for row in tqdm(table.split('<tr>')[1:]):
            album = row.split('"title">',1)[1].split('">',1)[1].split('</a',1)[0]
            albums.append(album)
            album_url = row.split('"title">',1)[1].split('">',1)[0].split('<a ')[1].split('="',1)[1]
            albums_url.append(album_url)
            while True:
                try:
                    client = webdriver.PhantomJS(desired_capabilities=dcap)
                    client.get(album_url)
                    page = client.page_source
                    client.quit()
                    break
                except:
                    print('Re-connect to {}'.format(album_url))
                    time.sleep(1)

            soup = bs(page, "lxml")
            # Moods
            moods = []
            try:
                for mood in soup.findAll('section', {"class": "moods"})[0].find_all('a'):
                    moods.append(mood.text)
            except:
                moods.append('None')
            albums_mood.append(moods)

            # Year
            try:
                year = row.split('class="year">')[1].split('</td',1)[0].strip()
                years.append(year)
            except:
                print(album)
                years.append('None')

            # Artist
            try:
                artist = row.split('artist">')[1].split('</td',1)[0].strip().split('">', 1)[1].split('</a', 1)[0]
                artists.append(artist)
            except:
                print(album, year)
                artists.append('Various Artists')

            # Artist URL
            try:
                artist_url = row.split('artist">')[1].split('</td',1)[0].strip().split('">', 1)[0].split('<a ', 1)[1].split('="',1)[1]
                artists_url.append(artist_url)
            except:
                print(album, year)
                artists_url.append('None')

            time.sleep(1)
            album_num += 1

        print('Done')

    print('{0} albums under {1}'.format(album_num, genre_name))
    df = pd.DataFrame({'album': albums,
                       'artist': artists,
                       'year': years,
                       'album_mood': albums_mood,
                       'album_url': albums_url,
                       'artist_url': artists_url})

    file_name = "_".join(genre_name.lower().split())
    df.to_csv('data/{}.csv'.format(file_name))
    print('Done. Saved to data/{}.csv'.format(file_name))
