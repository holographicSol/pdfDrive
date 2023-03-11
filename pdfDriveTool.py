"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""

import socket
import time
import requests
from bs4 import BeautifulSoup
import datetime
import fake_useragent
from fake_useragent import UserAgent
import colorama

colorama.init()
master_timeout = 120
ua = UserAgent()
socket.setdefaulttimeout(master_timeout)


def color(s, c):
    if c == 'W':
        return colorama.Style.BRIGHT + colorama.Fore.WHITE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LM':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTMAGENTA_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'M':
        return colorama.Style.BRIGHT + colorama.Fore.MAGENTA + str(s) + colorama.Style.RESET_ALL
    elif c == 'LC':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'B':
        return colorama.Style.BRIGHT + colorama.Fore.BLUE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LG':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTGREEN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'G':
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + str(s) + colorama.Style.RESET_ALL
    elif c == 'Y':
        return colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(s) + colorama.Style.RESET_ALL
    elif c == 'R':
        return colorama.Style.BRIGHT + colorama.Fore.RED + str(s) + colorama.Style.RESET_ALL


def get_dt() -> str:
    return color(str('[' + str(datetime.datetime.now()) + ']'), c='W')


def get_pages(search_q: str) -> str:
    max_page = 0
    headers = {'User-Agent': str(ua.random)}
    rHead = requests.get('https://www.pdfdrive.com/search?q=' + search_q, headers=headers, timeout=master_timeout)
    data = rHead.text
    soup = BeautifulSoup(data, "html.parser")
    for link in soup.find_all('a'):
        href = (link.get('href'))
        # print(f'{get_dt()} [HREF] {href}')  # verbose
        try:
            if '&page=' in href:
                idx = str(href).rfind('=')
                page = str(href)[idx+1:]
                # print(f'{get_dt()} [get_pages] Page: {page}')  # verbose
                if page.isdigit():
                    page = int(page)
                    if page > max_page:
                        max_page = page
        except Exception as e:
            print(f'{get_dt()} [Exception.get_pages] {e}')
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
        print(f'{get_dt()} [Exception.get_link] {e}')
        get_link(url=url)

    if len(book_urls) >= 1:
        return book_urls

    else:
        print(f'{get_dt()} [get_link] trying to obtain book URLs')
        time.sleep(5)
        get_link(url=url)


def get_page_links(search_q: str, page: str) -> list:
    url = str('https://www.pdfdrive.com/search?q=' + str(search_q).replace(' ', '+') + '&pagecount=&pubyear=&searchin=&page='+str(page))
    print(f'{get_dt()} ' + color('[Scanning page] ', c='M') + color(url, c='W'))
    book_urls = get_link(url=url)
    return book_urls


def enumerate_download_link(url: str) -> str:
    returned_url = ''
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

        if data_preview:
            data_preview = data_preview.replace('/ebook/preview?id=', '').replace('&session=', ' ')
            data_preview = data_preview.split(' ')
            data_id = data_preview[0]
            h_id = data_preview[1]
            returned_url = f'https://www.pdfdrive.com//download.pdf?id={data_id}&h={h_id}&u=cache&ext=pdf'
    except Exception as e:
        print(f'{get_dt()} [Exception.enumerate_download_link] {e}')
        time.sleep(10)
        enumerate_download_link(url=url)

    return returned_url


def make_file_name(book_url: str) -> str:
    book_url = book_url.replace('https://www.pdfdrive.com//', '')
    idx = book_url.rfind('-')
    book_url = book_url[:idx]
    book_url = book_url+'.pdf'
    return book_url
