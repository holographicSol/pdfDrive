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


def get_dt():
    return color(str('[' + str(datetime.datetime.now()) + ']'), c='W')


def download(url: str, fname: str):
    global retry_max
    global success_downloads
    global failed_downloads
    _download_finished = False
    _data = bytes()
    progress_mode = color('[DOWNLOADING] ', c='W')
    try:
        http = urllib3.PoolManager(retries=5)
        headers = {'User-Agent': str(ua.random)}
        r = http.request('GET', url, preload_content=False, headers=headers, timeout=master_timeout)
        while True:
            pyprogress.display_progress_unknown(str_progress=progress_mode, progress_list=pyprogress.arrow_a_12,
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
        print('_'*28)
        print('')
        print(f'{get_dt()} ' + color('[Progress] ', c='LC') + color(str(f'{i_progress}/{len(_book_urls)} ({_i_page}/{_max_page})'), c='W'))
        print(f'{get_dt()} ' + color('[Category] ', c='LC') + color(str(_search_q), c='W'))
        if not os.path.exists('./library/'):
            os.mkdir('./library/')
        if not os.path.exists('./library/' + _search_q):
            os.mkdir('./library/' + _search_q)

        filename = pdfDriveTool.make_file_name(book_url=book_url)
        fname = './library/' + _search_q + '/' + filename
        print(f'{get_dt()} ' + color('[Book] ', c='LC') + color(str(filename), c='M'))
        if not os.path.exists(fname):
            if fname not in success_downloads:

                print(f'{get_dt()} ' + color('[Enumerating] ', c='LC') + color(str(book_url), c='W'))
                url = pdfDriveTool.enumerate_download_link(url=book_url)
                if url:

                    print(f'{get_dt()} ' + color('[Enumeration result] ', c='LC') + color(str(url), c='W'))
                    download(url=url, fname=fname)
                else:
                    print(f'{get_dt()} ' + color('[URL] Unpopulated.', c='Y'))
                    print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File exists in records.', c='W'))
        else:
            print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File already exists in filesystem.', c='W'))

        i_progress += 1


stdin = list(sys.argv)

if '-h' in stdin:
    pdfdrive_help.display_help()

else:
    print('')
    print('_' * 28)
    print('')
    print(color('   [PDFDrive Downloader]', c='W'))
    print('_' * 28)
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
    print(f'{get_dt()} ' + color('[Search] ', c='LC') + color(_search_q, c='W'))

    """ Max Pages """
    _max_page = 1
    if '-max' in stdin:
        idx = stdin.index('-max') + 1
        _max_page = int(stdin[idx])
    else:
        _max_page = pdfDriveTool.get_pages(search_q=_search_q)
    print(f'{get_dt()} ' + color('[Pages] ', c='LC') + color(_max_page, c='W'))

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
            print('_' * 28)
            print('')
            book_urls = pdfDriveTool.get_page_links(search_q=_search_q, page=str(i_page))
            """ Scan Pages for book URLSs """
            print(f'{get_dt()} ' + color('[Page] ', c='M') + color(f'{i_page}', c='W'))
            print(f'{get_dt()} ' + color('[Getting book links] ', c='M') + color('This may take a moment..', c='W'))
            print(f'{get_dt()} ' + color('[Book URLs] ', c='M') + str(color(str(book_urls), c='LC')))
            if book_urls is not None:
                print(f'{get_dt()} ' + color('[Books] ', c='M') + color(str(len(book_urls)), c='W'))

                """ Download """
                print(f'{get_dt()} ' + color('[Starting Downloads]', 'G'))
                downloader(_book_urls=book_urls, _search_q=_search_q, _i_page=str(i_page), _max_page=str(_max_page))
                print('')
            else:
                if i_page >= 1:
                    i_page -= 1
        else:
            print(f'{get_dt()} [Skipping Page] {i_page}')

        i_page += 1
