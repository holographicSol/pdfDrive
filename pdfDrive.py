import datetime
import os
import sys
import time

import handler_chunk
import pdfDriveTool
import socket
import urllib3
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


def download(url, fname):
    _download_finished = False
    _data = bytes()

    try:
        http = urllib3.PoolManager(retries=5)
        r = http.request('GET', url, preload_content=False, headers=headers)
        while True:
            data = r.read(1024)
            if data:
                _data += data
            else:
                _download_finished = True

                open(fname, 'w').close()
                with open(fname, 'wb') as out:
                    out.write(_data)
                out.close()
                break

    except Exception as e:
        print(f'{get_dt()} {e}')
    try:
        if r:
            r.release_conn()
    except Exception as e:
        print(f'{get_dt()} {e}')
    if _download_finished is False:
        print(f'{get_dt()} Retrying:', url)
        time.sleep(5)
        download(url, fname)


def downloader(book_urls, _search_q):
    i_progress = 1
    for book_url in book_urls:
        print('_'*50)
        print(f'{get_dt()} Progress: {i_progress}/{len(book_urls)}')

        if not os.path.exists('./library/'):
            os.mkdir('./library/')
        if not os.path.exists('./library/' + _search_q):
            os.mkdir('./library/' + _search_q)

        fname = './library/' + _search_q + '/' + pdfDriveTool.make_file_name(book_url)
        if not os.path.exists(fname):
            print(f'{get_dt()} Enumerating: {book_url}')
            url = pdfDriveTool.enumerate_download_link(url=book_url)
            if url:
                print(f'{get_dt()} Enumeration result: {url}')
                download(url, fname)
            else:
                print(f'{get_dt()} URL: Unpopulated')

        else:
            print(f'{get_dt()} Skipping: {book_url}')

        i_progress += 1


""" Get Search query """
print('')
_search_q = ''
stdin = list(sys.argv)
idx = stdin.index('-k')+1
i = 0
for x in stdin:
    if i >= int(idx):
        _search_q = _search_q + ' ' + x
    i += 1
_search_q = _search_q[1:]
print(f'{get_dt()} Search:', _search_q)

""" Get Max Pages """
_max_page = pdfDriveTool.get_pages(search_q=_search_q)
print(f'{get_dt()} Pages: {_max_page}')

""" Scan Pages for book URLSs """
print(f'{get_dt()} Getting book links: (this may take a moment)')

i_page = 1
for i in range(1, int(_max_page)):
    book_urls = pdfDriveTool.get_page_links(search_q=_search_q, page=str(i_page))
    print(f'{get_dt()} Book URLs: {book_urls}')
    print(f'{get_dt()} Books: {len(book_urls)}')

    """ Download """
    print(f'{get_dt()} Starting downloads..')
    downloader(book_urls, _search_q=_search_q)
    print('')

    i_page += 1
