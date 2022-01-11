from data.translator import translate
from bs4 import BeautifulSoup as Soup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests, hashlib

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15'}
ok_statuses = {200}
driver_path = '/Users/dsalakhov/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs'


def get_url_name(url):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code not in ok_statuses:
            return 'Ошибка в ссылке'
        soup = Soup(r.content, 'html.parser')
        if not soup:
            return 'Страница не загрузилась'
        title = soup.select('title')
        if title is None or not isinstance(title, list) or len(title) < 1:
            return 'Заголовок не найден'
        return title[0].text
    except:
        return 'Ошибка в ссылке'


def get_selenium_title(url, css_path):
    print('Driver working...')
    driver = None
    try:
        driver = webdriver.PhantomJS(executable_path=driver_path)
        # driver = webdriver.Safari()
        driver.get(url)
        title = driver.find_element_by_css_selector(css_path)
        driver.quit()
        return None if not title else title.text
    except NoSuchElementException:
        print('Elem not found')
        if driver is not None:
            driver.quit()
        return None
    except:
        return None


def get_title(url, css_path, js_required=False):
    if js_required:
        return get_selenium_title(url, css_path)
    try:
        r = requests.get(url, headers=headers)
        if r.status_code not in ok_statuses:
            return None
        #body > div:nth-child(3) > div.container > div > main > div > article:nth-child(2) > div > h2 > a
        soup = Soup(r.content, 'html.parser')
        if not soup:
            return None
        title = soup.select(css_path)
        if title is None or not isinstance(title, list) or len(title) < 1:
            return None
        return title[0].text
    except:
        return None


def get_hash(text):
    return str(hashlib.md5(str(text).encode('utf-8')).hexdigest())
