"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""

import socket
import time

import requests
from bs4 import BeautifulSoup
import datetime
from fake_useragent import UserAgent

master_timeout = 120
ua = UserAgent()
socket.setdefaulttimeout(master_timeout)


def get_dt() -> str:
    return str(f'[{str(datetime.datetime.now())}]')


def get_pages(search_q: str) -> str:
    max_page = 0
    headers = {'User-Agent': str(ua.random)}
    rHead = requests.get('https://www.pdfdrive.com/search?q=' + search_q, headers=headers, timeout=master_timeout)
    data = rHead.text
    soup = BeautifulSoup(data, "html.parser")
    for link in soup.find_all('a'):
        href = (link.get('href'))
        print(href)
        try:
            if 'searchin=&page=' in href:
                page = int(str(href).replace(f'search?q={search_q}&pagecount=&pubyear=&searchin=&page=', ''))
                if page > max_page:
                    max_page = page
            elif f'/search?q={search_q}&page=' in href:
                page = int(str(href).replace(f'/search?q={search_q}&page=', ''))
                if page > max_page:
                    max_page = page
        except Exception as e:
            print(f'{get_dt()} {e}')
            max_page = 1
    return str(max_page)


def get_link(url: str) -> list:
    book_urls = []
    try:
        headers = {'User-Agent': str(ua.random)}
        rHead = requests.get(url, headers=headers, timeout=master_timeout)
        data = rHead.text
        soup = BeautifulSoup(data, "html.parser")
        for link in soup.find_all('a'):
            href = (link.get('href'))
            if str(href).endswith('.html'):
                if 'auth/login' not in str(href):
                    if 'home/setLocal' not in str(href):
                        book_link = 'https://www.pdfdrive.com/' + str(href)
                        if book_link not in book_urls:
                            book_urls.append(book_link)
    except Exception as e:
        print(f'{get_dt()} [get_link] {e}')
        get_link(url=url)

    if not len(book_urls) >= 1:
        print(f'{get_dt()} [get_link] trying to obtain book URLs')
        time.sleep(5)
        get_link(url=url)

    else:
        return book_urls


def get_page_links(search_q: str, page: str) -> list:
    url = str('https://www.pdfdrive.com/search?q=' + str(search_q).replace(' ', '+') + '&pagecount=&pubyear=&searchin=&page='+str(page))
    print(f'{get_dt()} Scanning page: {url}')
    book_urls = get_link(url=url)
    return book_urls


def enumerate_download_link(url: str) -> str:
    try:
        headers = {'User-Agent': str(ua.random)}
        rHead = requests.get(url, headers=headers, timeout=master_timeout)
        data = rHead.text
        soup = BeautifulSoup(data, "html.parser")
        data_preview = ''
        for link in soup.find_all('button'):
            data_preview = link.get('data-preview')
            if data_preview is not None:
                data_preview = data_preview
                break
        url = ''
        if data_preview:
            data_preview = data_preview.replace('/ebook/preview?id=', '').replace('&session=', ' ')
            data_preview = data_preview.split(' ')
            data_id = data_preview[0]
            h_id = data_preview[1]
            url = f'https://www.pdfdrive.com//download.pdf?id={data_id}&h={h_id}&u=cache&ext=pdf'
    except Exception as e:
        print(f'{get_dt()} [enumerate_download_link] {e}')
        enumerate_download_link(url=url)

    return url


def make_file_name(book_url: str) -> str:
    return book_url.replace('https://www.pdfdrive.com//', '').replace('.html', '.pdf')
