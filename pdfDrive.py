"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""

import os
import sys
import time
import pdfDriveTool
import socket
import urllib3
import datetime
from fake_useragent import UserAgent
import colorama
import codecs
import pdfdrive_help
import pyprogress

colorama.init()
master_timeout = 120
ua = UserAgent()
socket.setdefaulttimeout(master_timeout)
retry_max = 1
success_downloads = []
failed_downloads = []


def color(s, c):
    if c == 'LC':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'G':
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + str(s) + colorama.Style.RESET_ALL
    elif c == 'R':
        return colorama.Style.BRIGHT + colorama.Fore.RED + str(s) + colorama.Style.RESET_ALL
    elif c == 'Y':
        return colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(s) + colorama.Style.RESET_ALL


def get_dt():
    return str(f'[{str(datetime.datetime.now())}]')


def download(url: str, fname: str):
    global retry_max
    global success_downloads
    global failed_downloads
    _download_finished = False
    _data = bytes()
    try:
        http = urllib3.PoolManager(retries=5)
        headers = {'User-Agent': str(ua.random)}
        r = http.request('GET', url, preload_content=False, headers=headers, timeout=master_timeout)
        while True:
            pyprogress.display_progress_unknown(str_progress='[DOWNLOADING] ', progress_list=pyprogress.arrow_a,
                                                color='CYAN')
            data = r.read(1024)
            if data:
                _data += data
            else:
                _download_finished = True
                break
    except Exception as e:
        print(f'{get_dt()} [Exception.download] {e}')
    try:
        if r:
            r.release_conn()
    except Exception as e:
        print(f'{get_dt()} [Exception.download.r.release] {e}')

    if _download_finished is False:
        if retry_max > 0:
            retry_max -= 1
            print(f'{get_dt()} ' + color('Retrying.', c='Y'))
            download(url=url, fname=fname)
    else:
        codecs.open(fname, 'w', encoding='utf8').close()
        with open(fname, 'wb') as out:
            out.write(_data)
        out.close()

    if os.path.exists(fname):
        if os.path.getsize(fname) > 100:
            print(f'{get_dt()} ' + color('[Downloaded Successfully]', c='G'))
            with codecs.open('./books_saved.txt', 'a+', encoding='utf8') as fo:
                fo.write(fname+'\n')
            fo.close()
        else:
            print(f'{get_dt()} ' + color('[Download Failed] File less than 100 bytes.', c='R'))
            if fname not in failed_downloads:
                with codecs.open('./books_failed.txt', 'a+', encoding='utf8') as fo:
                    fo.write(fname+'\n')
                fo.close()
                failed_downloads.append(fname)
            os.remove(fname)
    else:
        print(f'{get_dt()} ' + color('[Download Failed] File did not save.', c='R'))
        if fname not in failed_downloads:
            with codecs.open('./books_failed.txt', 'a+', encoding='utf8') as fo:
                fo.write(fname + '\n')
            fo.close()
            failed_downloads.append(fname)


def downloader(_book_urls: list, _search_q: str, _i_page: str, _max_page: str):
    global retry_max
    global success_downloads
    i_progress = 1
    for book_url in _book_urls:
        retry_max = 3
        print('_'*50)
        print('')
        print(f'{get_dt()} [Progress] {i_progress}/{len(_book_urls)} ({_i_page}/{_max_page})')
        print(f'{get_dt()} [Category] {_search_q}')
        if not os.path.exists('./library/'):
            os.mkdir('./library/')
        if not os.path.exists('./library/' + _search_q):
            os.mkdir('./library/' + _search_q)

        fname = './library/' + _search_q + '/' + pdfDriveTool.make_file_name(book_url=book_url)
        print(f'{get_dt()} [Book] {fname}')
        if not os.path.exists(fname):
            if fname not in success_downloads:
                print(f'{get_dt()} [Enumerating] {book_url}')
                url = pdfDriveTool.enumerate_download_link(url=book_url)
                if url:
                    print(f'{get_dt()} [Enumeration result] {url}')
                    download(url=url, fname=fname)
                else:
                    print(f'{get_dt()} ' + color('[URL] Unpopulated.', c='Y'))
            else:
                print(f'{get_dt()} ' + color('[Skipping] (File exists in records): ', c='Y') + str(book_url))
        else:
            print(f'{get_dt()} ' + color('[Skipping] (File already exists): ', c='Y') + str(book_url))

        i_progress += 1


stdin = list(sys.argv)

if '-h' in stdin:
    pdfdrive_help.display_help()

else:
    print('')
    """ Page """
    i_page = 1
    if '-p' in stdin:
        idx = stdin.index('-p') + 1
        i_page = int(stdin[idx])

    """ Query """
    _search_q = ''
    idx = stdin.index('-k')+1
    i = 0
    for x in stdin:
        if i >= int(idx):
            _search_q = _search_q + ' ' + x
        i += 1
    _search_q = _search_q[1:]
    print(f'{get_dt()} [Search]', _search_q)

    """ Max Pages """
    _max_page = 1
    if '-max' in stdin:
        idx = stdin.index('-max') + 1
        _max_page = int(stdin[idx])
    else:
        _max_page = pdfDriveTool.get_pages(search_q=_search_q)
    print(f'{get_dt()} [Pages] {_max_page}')

    """ Scan Pages for book URLSs """
    print(f'{get_dt()} [Getting book links] This may take a moment..')

    with codecs.open('./books_failed.txt', 'r+', encoding='utf8') as fo:
        for line in fo:
            line = line.strip()
            if line not in failed_downloads:
                failed_downloads.append(line)
    fo.close()

    with codecs.open('./books_saved.txt', 'r+', encoding='utf8') as fo:
        for line in fo:
            line = line.strip()
            if line not in success_downloads:
                success_downloads.append(line)
    fo.close()

    for i in range(1, int(_max_page)):
        if i_page >= i:
            book_urls = pdfDriveTool.get_page_links(search_q=_search_q, page=str(i_page))
            print(f'{get_dt()} [Book URLs] ' + str(color(book_urls, c='LC')))
            print(f'{get_dt()} [Books] {len(book_urls)}')

            """ Download """
            print(f'{get_dt()} [Starting Download]')
            downloader(_book_urls=book_urls, _search_q=_search_q, _i_page=str(i_page), _max_page=str(_max_page))
            print('')
        else:
            print(f'{get_dt()} [Skipping Page] {i_page}')

        i_page += 1
