"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""
import time
import socket
import requests
from bs4 import BeautifulSoup
import datetime

socket.setdefaulttimeout(10)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                  '73.0.3683.103 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/'
              'signed-exchange;v=b3',
    'Accept-Encoding': 'text/plain',
    'Accept-Language': 'en-US,en;q=0.9'
    }


def get_dt():
    return str(f'[{str(datetime.datetime.now())}]')


def get_pages(search_q: str):
    max_page = 0
    rHead = requests.get('https://www.pdfdrive.com/search?q=' + search_q)
    data = rHead.text
    soup = BeautifulSoup(data, "html.parser")
    for link in soup.find_all('a'):
        href = (link.get('href'))
        if 'searchin=&page=' in href:
            page = int(str(href).replace(f'search?q={search_q}&pagecount=&pubyear=&searchin=&page=', ''))
            if page > max_page:
                max_page = page
        elif f'/search?q={search_q}&page=' in href:
            page = int(str(href).replace(f'/search?q={search_q}&page=', ''))
            if page > max_page:
                max_page = page
    return str(max_page)


def get_link(url):
    book_urls = []
    try:
        rHead = requests.get(url, headers=headers, timeout=5)
        data = rHead.text
        soup = BeautifulSoup(data, "html.parser")
        for link in soup.find_all('a'):
            href = (link.get('href'))
            if str(href).endswith('.html'):
                book_link = 'https://www.pdfdrive.com/' + str(href)
                if book_link not in book_urls:
                    book_urls.append(book_link)
    except Exception as e:
        print(f'{get_dt()} {e}')
        get_link(url)
    return book_urls


def get_page_links(search_q: str, max_page: str):
    book_urls = []
    i_page = 1
    for i in range(i_page, int(max_page)):
        url = 'https://www.pdfdrive.com/search?q=' + str(search_q).replace(' ', '+') + '&pagecount=&pubyear=&searchin=&page='+str(i_page)
        print(f'{get_dt()} Scanning page: {url}')
        book_urls.append(get_link(url))
        time.sleep(1)
        i_page += 1
    return book_urls


def enumerate_download_link(url):
    try:
        rHead = requests.get(url)
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
        print(f'{get_dt()} {e}')
        enumerate_download_link(url)

    return url


def make_file_name(book_url):
    return book_url.replace('https://www.pdfdrive.com//', '').replace('.html', '.pdf')
