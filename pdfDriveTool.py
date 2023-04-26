"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""

import socket
import time
import requests
from bs4 import BeautifulSoup
import datetime
from fake_useragent import UserAgent
import colorama

colorama.init()
master_timeout = 120
# master_timeout = 86400  # 24h
ua = UserAgent()
socket.setdefaulttimeout(master_timeout)


def color(s: str, c: str) -> str:
    """ color print """
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
    """ formatted datetime string for tagging output """
    return color(str('[' + str(datetime.datetime.now()) + ']'), c='W')


def get_pages(search_q: str) -> str:

    max_page = 0

    # crawl the page for pages
    headers = {'User-Agent': str(ua.random)}
    rHead = requests.get('https://www.pdfdrive.com/search?q=' + search_q, headers=headers, timeout=master_timeout)
    data = rHead.text
    soup = BeautifulSoup(data, "html.parser")

    # parse the html soup for references to page
    for link in soup.find_all('a'):
        href = (link.get('href'))
        try:
            if '&page=' in href:
                idx = str(href).rfind('=')
                page = str(href)[idx+1:]
                if page.isdigit():
                    page = int(page)

                    # max_page equals page if page is greater than previously known max_page
                    if page > max_page:
                        max_page = page

        except Exception as e:
            print(f'{get_dt()} [Exception.get_pages] {e}')
            max_page = 1

    return str(max_page)


def get_link(url: str) -> list:

    book_urls = []

    try:
        # crawl the search page
        headers = {'User-Agent': str(ua.random)}
        rHead = requests.get(url, headers=headers, timeout=master_timeout)
        data = rHead.text
        soup = BeautifulSoup(data, "html.parser")

        # parse the html soup for book links
        for link in soup.find_all('a'):
            href = (link.get('href'))
            if str(href).endswith('.html'):
                if 'auth/login' not in str(href):
                    if 'home/setLocal' not in str(href):
                        book_link = 'https://www.pdfdrive.com/' + str(href)
                        if book_link not in book_urls:

                            # add book link(s) to list
                            book_urls.append(book_link)

    except Exception as e:
        print(f'{get_dt()} [Exception.get_link] {e}')
        # try again
        get_link(url=url)

    if len(book_urls) >= 1:
        # return the list of book links
        return book_urls

    else:
        print(f'{get_dt()} [get_link] trying to obtain book URLs')
        time.sleep(5)
        # try again
        get_link(url=url)


def get_page_links(search_q: str, page: str, exact_match: bool) -> list:

    # create url
    url = str('https://www.pdfdrive.com/search?q=' + str(search_q).replace(' ', '+') + '&pagecount=&pubyear=&searchin=&page='+str(page))

    # create url with exact match condition in the url
    if exact_match is True:
        url = str('https://www.pdfdrive.com/search?q=' + str(search_q).replace(' ', '+') + '&pagecount=&pubyear=&searchin=&em=1&page='+str(page))#

    # output: created url
    print(f'{get_dt()} ' + color('[Scanning page] ', c='M') + color(url, c='W'))

    # run get links function
    book_urls = get_link(url=url)

    return book_urls


def enumerate_download_link(url: str) -> str:

    returned_url = ''

    try:
        # crawl the page
        headers = {'User-Agent': str(ua.random)}
        rHead = requests.get(url, headers=headers, timeout=master_timeout)
        data = rHead.text
        soup = BeautifulSoup(data, "html.parser")

        # parse the soup for a specific html tag that we can use to create the final download link before having seen
        # the final download link (pdf-drive currently has a time wait on the final download page, no need to wait)
        data_preview = ''
        for link in soup.find_all('button'):
            data_preview = link.get('data-preview')
            if data_preview is not None:
                data_preview = data_preview
                break

        # generate final download link
        if data_preview:
            data_preview = data_preview.replace('/ebook/preview?id=', '').replace('&session=', ' ')
            data_preview = data_preview.split(' ')
            data_id = data_preview[0]
            h_id = data_preview[1]
            returned_url = f'https://www.pdfdrive.com//download.pdf?id={data_id}&h={h_id}&u=cache&ext=pdf'

    except Exception as e:
        print(f'{get_dt()} [Exception.enumerate_download_link] {e}')
        time.sleep(10)
        # try again
        enumerate_download_link(url=url)

    return returned_url


def make_file_name(book_url: str) -> str:

    # remove pdf drive tag from url (-pdfdrive), and remove domain name (https://www.pdfdrive.com//)
    book_url = book_url.replace('https://www.pdfdrive.com//', '')
    idx = book_url.rfind('-')
    book_url = book_url[:idx]
    book_url = book_url+'.pdf'
    return book_url
