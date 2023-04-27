"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""

import os
import sys
import time
import pdfDriveTool
import socket
import datetime
from fake_useragent import UserAgent
import colorama
import codecs
import pdfdrive_help
import grand_library_supremo
import requests
import shutil

# Notification of New Media
# Platform check (Be compatible with Termux on Android, skip Pyqt5 import)
if os.name in ('nt', 'dos'):
    try:
        from PyQt5.QtCore import QUrl
        from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
        from threading import Thread

        # Initialize Notification Player_default In Memory
        player_url_default = QUrl.fromLocalFile("./resources/sound/coin_collect.mp3")
        player_content_default = QMediaContent(player_url_default)
        player_default = QMediaPlayer()
        player_default.setMedia(player_content_default)
        player_default.setVolume(6)
        mute_default_player = True
    except:
        pass

colorama.init()
master_timeout = 86400  # 24h
ua = UserAgent()
socket.setdefaulttimeout(master_timeout)
success_downloads = []
failed_downloads = []


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


def convert_bytes(num: int) -> str:
    """ bytes for humans """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return str(num)+' '+x
        num /= 1024.0


def clear_console_line(char_limit: int):
    """ clear n chars from console """
    print(' '*char_limit, end='\r', flush=True)


def play():
    """ notification sound """
    if os.name in ('nt', 'dos'):
        player_default.play()
        time.sleep(1)


def download_file(_url: str, _filename: str, _timeout=86400, _chunk_size=8192,
                  _clear_console_line_n=50, _chunk_encoded_response=False, _min_file_size=1024,
                  _log=False, _headers='random') -> bool:
    """
    URL: Specify url.

    FILENAME: Specify the PATH/FILENAME to save the download as.

    TIMEOUT: Specify how long to wait during connection issues etc. before closing the connection. (Default 24h).

    CHUNK SIZE: Specify size of each chunk to read/write from the stream. (Default 8192).

    CLEAR CONSOLE LINE: Specify how many characters to clear from the console when displaying download progress.
                        (Download progress on one line). (Default 50 characters for small displays).

    CHUNK ENCODED RESPONSE: Bool. Must be true or false. (Default false)

    MINIMUM FILE SIZE: Specify expected/acceptable minimum file size of downloaded file. (Remove junk). (Default 1024).

    LOG: Record what has been downloaded successfully.
    """

    # use a random user agent for download stability
    if _headers == 'random':
        headers = {'User-Agent': str(ua.random)}

    # connect
    with requests.get(_url, stream=True, timeout=_timeout, headers=headers) as r:
        r.raise_for_status()

        # open a temporary file of our created filename
        with open(_filename+'.tmp', 'wb') as f:

            # iterate though chunks of the stream
            for chunk in r.iter_content(chunk_size=_chunk_size):

                # allow (if _chunk_encoded_response is False) or (if _chunk_encoded_response is True and chunk)
                _allow_continue = False
                if _chunk_encoded_response is True:
                    if chunk:
                        _allow_continue = True
                elif _chunk_encoded_response is False:
                    _allow_continue = True

                if _allow_continue is True:

                    # storage check:
                    total, used, free = shutil.disk_usage("./")
                    if free > _chunk_size+1024:

                        # write chunk to the temporary file
                        f.write(chunk)

                        # output: display download progress
                        print(' ' * _clear_console_line_n, end='\r', flush=True)
                        print(f'[DOWNLOADING] {str(convert_bytes(os.path.getsize(_filename+".tmp")))}', end='\r', flush=True)

                    else:
                        # output: out of disk space
                        print(' ' * _clear_console_line_n, end='\r', flush=True)
                        print(str(color(s='[WARNING] OUT OF DISK SPACE! Download terminated.', c='Y')), end='\r', flush=True)

                        # delete temporary file if exists
                        if os.path.exists(_filename + '.tmp'):
                            os.remove(_filename + '.tmp')
                        time.sleep(1)

                        # exit.
                        print('')
                        exit(0)

    # check: does the temporary file exists
    if os.path.exists(_filename+'.tmp'):

        # check: temporary file worth keeping? (<1024 bytes would be less than 1024 characters, reduce this if needed)
        # - sometimes file exists on a different server, this software does not intentionally follow any external links,
        # - if the file is in another place then a very small file may be downloaded because ultimately the file we
        #   wanted was not present and will then be detected and deleted.
        if os.path.getsize(_filename+'.tmp') >= _min_file_size:

            # create final download file from temporary file
            os.replace(_filename+'.tmp', _filename)

            # check: clean up the temporary file if it exists.
            if os.path.exists(_filename+'.tmp'):
                os.remove(_filename+'.tmp')

            # display download success (does not guarantee a usable file, some checks are performed before this point)
            if os.path.exists(_filename):
                print(f'{get_dt()} ' + color('[Downloaded Successfully]', c='G'))

                # add book to saved list. multi-drive/system memory (continue where you left off on another disk/sys)
                if _log is True:
                    idx_filename = _filename.rfind('/')
                    to_saved_list = _filename[idx_filename + 1:]
                    if to_saved_list not in success_downloads:
                        success_downloads.append(to_saved_list)
                        if not os.path.exists('./books_saved.txt'):
                            open('./books_saved.txt', 'w').close()
                        with codecs.open('./books_saved.txt', 'a', encoding='utf8') as file_open:
                            file_open.write(to_saved_list + '\n')
                        file_open.close()

                return True

        else:
            print(f'{get_dt()} ' + color(f'[Download Failed] File < {_min_file_size} bytes, will be removed.', c='Y'))

            # check: clean up the temporary file if it exists.
            if os.path.exists(_filename+'.tmp'):
                os.remove(_filename+'.tmp')

            return False


def download_handler(url: str, fname: str):
    global success_downloads
    global failed_downloads

    # global mute_default_player after platform check (Be compatible on Termux on Android)
    if os.name in ('nt', 'dos'):
        global mute_default_player

    # track progress
    _download_finished = False
    _data = bytes()

    try:
        # download file
        if download_file(_url=url, _filename=fname, _timeout=86400, _chunk_size=8192,
                         _clear_console_line_n=50, _chunk_encoded_response=False, _min_file_size=1024,
                         _log=True) is True:

            # notification sound after platform check (Be compatible on Termux on Android)
            if os.name in ('nt', 'dos'):
                if mute_default_player is False:
                    play_thread = Thread(target=play)
                    play_thread.start()

    except Exception as e:
        # output: any issues
        print(f'{get_dt()} [Exception.download] {e}')
        print(f'{get_dt()} ' + color('[Download Failed]', c='R'))

        # remove the file if it was created to clean up after ourselves
        if os.path.exists(fname):
            os.remove(fname)


def pre_process(_book_urls: list, _search_q: str, _i_page: str, _max_page: str, _lib_path: str):
    global success_downloads
    i_progress = 1

    for book_url in _book_urls:

        # output: header
        print('_'*28)
        print('')
        print(f'{get_dt()} {color("[Progress] ", c="LC")} {color(str(f"{i_progress}/{len(_book_urls)} ({_i_page}/{_max_page})"), c="W")}')
        print(f'{get_dt()} ' + color('[Category] ', c='LC') + color(str(_search_q), c='W'))

        # check: library directory exists
        if not os.path.exists(_lib_path + '/'):
            os.mkdir(_lib_path + '/')

        # check: library category directory exists
        if not os.path.exists(_lib_path + '/' + _search_q):
            os.mkdir(_lib_path + '/' + _search_q)

        # check: create a filename from url
        filename = pdfDriveTool.make_file_name(book_url=book_url)
        fname = _lib_path + '/' + _search_q + '/' + filename

        # output: filename
        print(f'{get_dt()} ' + color('[Book] ', c='LC') + color(str(filename), c='M'))

        # check: filename already exists
        if not os.path.exists(fname):

            # check: filename exists in books_saved.txt
            if fname not in success_downloads:

                # create download url (don't follow links to download page containing the actual download link)
                print(f'{get_dt()} ' + color('[Enumerating] ', c='LC') + color(str(book_url), c='W'))
                url = pdfDriveTool.enumerate_download_link(url=book_url)
                if url:
                    # download.
                    print(f'{get_dt()} ' + color('[Enumeration result] ', c='LC') + color(str(url), c='W'))
                    download_handler(url=url, fname=fname)
                else:
                    print(f'{get_dt()} ' + color('[URL] Unpopulated.', c='Y'))
            else:
                print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File exists in records.', c='W'))
        else:
            print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File already exists in filesystem.', c='W'))

        i_progress += 1


stdin = list(sys.argv)

if '-h' in stdin:
    pdfdrive_help.display_help()

else:
    grand_library_supremo.display_grand_library()
    time.sleep(5)

    if os.name in ('nt', 'dos'):
        if '-sfx' in stdin:
            mute_default_player = False

    """ Library Path """
    lib_path = './library/'
    if '-P' in stdin:
        idx = stdin.index('-P') + 1
        lib_path = stdin[idx]

    """ Exact Match """
    exact_match = False
    if '-e' in stdin:
        exact_match = True

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

    """ Use Download Log """
    if '--no-mem' not in stdin:
        if not os.path.exists('./books_failed.txt'):
            open('./books_failed.txt', 'w').close()
        with codecs.open('./books_failed.txt', 'r', encoding='utf8') as fo:
            for line in fo:
                line = line.strip()
                if line not in failed_downloads:
                    failed_downloads.append(line)
        fo.close()
        if not os.path.exists('./books_saved.txt'):
            open('./books_saved.txt', 'w').close()
        with codecs.open('./books_saved.txt', 'r', encoding='utf8') as fo:
            for line in fo:
                line = line.strip()
                if line not in success_downloads:
                    success_downloads.append(line)
        fo.close()

    allow_grand_library = False
    allow_grand_library_1 = True
    i = 1
    while i <= int(_max_page):
        if i >= i_page:
            print('_' * 28)
            if allow_grand_library is True:
                grand_library_supremo.display_grand_library()
            book_urls = pdfDriveTool.get_page_links(search_q=_search_q, page=str(i), exact_match=exact_match)

            """ Scan Pages for book URLSs """
            print(f'{get_dt()} ' + color('[Page] ', c='M') + color(f'{i}', c='W'))
            print(f'{get_dt()} ' + color('[Getting book links] ', c='M') + color('This may take a moment..', c='W'))
            print(f'{get_dt()} ' + color('[Book URLs] ', c='M') + str(color(str(book_urls), c='LC')))
            if book_urls is not None:
                allow_grand_library_1 = True
                print(f'{get_dt()} ' + color('[Books] ', c='M') + color(str(len(book_urls)), c='W'))

                """ Download """
                print(f'{get_dt()} ' + color('[Starting Downloads]', c='G'))
                pre_process(_book_urls=book_urls, _search_q=_search_q, _i_page=str(i), _max_page=str(_max_page),
                            _lib_path=lib_path)
                print('')
            else:
                print(f'{get_dt()} ' + color('[MAX_PAGE] ', c='M') + color(f'Possibly reached max page.', c='W'))
                i = _max_page

        else:
            print(f'{get_dt()} [Skipping Page] {i}')

        i += 1
        if allow_grand_library_1 is True:
            allow_grand_library = True
