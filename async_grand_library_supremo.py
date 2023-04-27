""" Written by Benjamin Jack Cullen """

import os
import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime
import colorama
import socket
import codecs
import requests
import grand_library_supremo
import shutil
import grand_library_supremo_help
import sys

# colorama requires initialization before use
colorama.init()

# modify socket module timeout
master_timeout = 86400  # 24h
socket.setdefaulttimeout(master_timeout)

# initialize fake user agant
ua = UserAgent()

i_page = 1
_max_page = 88
exact_match = False
lib_path = './library/'
success_downloads = []
failed_downloads = []

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


def get_soup(body):
    """ return soup """
    return BeautifulSoup(body, 'html.parser')


def parse_soup_phase_one(soup):
    """ parse soup from phase one (parse for book URLs) """
    book_urls = []
    for link in soup.find_all('a'):
        href = (link.get('href'))
        if str(href).endswith('.html'):
            if 'auth/login' not in str(href):
                if 'home/setLocal' not in str(href):
                    book_link = 'https://www.pdfdrive.com/' + str(href)
                    if book_link not in book_urls:
                        book_urls.append(book_link)
    return book_urls


def parse_soup_phase_two(soup):
    """ parse soup from phase two (parse book URLs (found in phase one) for a specific tag) """
    book_urls = []
    data_preview = ''
    for link in soup.find_all('button'):
        data_preview = link.get('data-preview')
        if data_preview is not None:
            data_preview = data_preview
            break
    if data_preview:
        """ create final book download links using data_preview value """
        data_preview = data_preview.replace('/ebook/preview?id=', '').replace('&session=', ' ')
        data_preview = data_preview.split(' ')
        data_id = data_preview[0]
        h_id = data_preview[1]
        book_urls.append(f'https://www.pdfdrive.com//download.pdf?id={data_id}&h={h_id}&u=cache&ext=pdf')
    return book_urls


async def scrape_pages(url):
    """ scrape for book URLs """
    headers = {'User-Agent': str(ua.random)}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            body = await resp.text()
            soup = await asyncio.to_thread(get_soup, body)
            book_urls = await asyncio.to_thread(parse_soup_phase_one, soup)
            return book_urls


async def enumerate_links(url: str):
    """ scrape for book download links """
    headers = {'User-Agent': str(ua.random)}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            body = await resp.text(encoding=None, errors='ignore')
            soup = await asyncio.to_thread(get_soup, body)
            book_urls = await asyncio.to_thread(parse_soup_phase_two, soup)
            return book_urls


def make_file_name(book_url: str) -> str:
    """ create filenames from book URLs """
    book_url = book_url.replace('https://www.pdfdrive.com//', '')
    idx = book_url.rfind('-')
    book_url = book_url[:idx]
    book_url = book_url+'.pdf'
    return book_url


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
    global success_downloads, failed_downloads

    # use a random user agent for download stability
    if _headers == 'random':
        _headers = {'User-Agent': str(ua.random)}

    # connect
    with requests.get(_url, stream=True, timeout=_timeout, headers=_headers) as r:
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


async def main():
    global success_downloads, failed_downloads
    global lib_path, _search_q, exact_match, i_page, _max_page

    # create the first URL to scrape using query and exact match bool
    url = str('https://www.pdfdrive.com/search?q=' + str(_search_q).replace(' ', '+'))
    if exact_match is True:
        url = str('https://www.pdfdrive.com/search?q=' + str(_search_q).replace(' ', '+') + '&pagecount=&pubyear=&searchin=&em=1&page='+str(i_page))
    url = url + '&pagecount=&pubyear=&searchin=&page='

    # Phase One: Setup async scaper to get book URLs (one page at a time to prevent getting kicked from the server)
    print(f'{get_dt()} ' + color('[Phase One] ', c='LC') + f'Gathering initial links...')
    for current_page in range(i_page, _max_page):
        tasks = []
        t0 = time.perf_counter()
        url = url+str(current_page)
        task = asyncio.create_task(scrape_pages(url))
        tasks.append(task)
        results = await asyncio.gather(*tasks)
        for result in results:
            if result is None:
                del result
        results[:] = [item for sublist in results for item in sublist if item is not None]
        print(f'{get_dt()} ' + color('[Results] ', c='LC') + f'{len(results)}')
        print(f'{get_dt()} ' + color('[Phase One Time] ', c='LC') + f'{time.perf_counter()-t0}')

        print('')

        # Phase Two: Setup async scaper to get book download links for each book on the current page
        print(f'{get_dt()} ' + color('[Phase Two] ', c='LC') + f'Enumerating Links...')
        t0 = time.perf_counter()
        tasks = []
        for result in results:
            task = asyncio.create_task(enumerate_links(result))
            tasks.append(task)
        enumerated_results = await asyncio.gather(*tasks)
        enumerated_results[:] = [item for sublist in enumerated_results for item in sublist if item is not None]
        print(f'{get_dt()} ' + color('[Enumerated Results] ', c='LC') + f'{len(enumerated_results)}')
        print(f'{get_dt()} ' + color('[Phase Two Time] ', c='LC') + f'{time.perf_counter()-t0}')

        # Check: Ensure results == enumerated_results so that filenames from URLs and download links should align
        if len(results) == len(enumerated_results):

            # Synchronously (for now) attempt to download each book on the current page.
            i_progress = 0
            for enumerated_result in enumerated_results:
                print('_' * 28)
                print('')
                print(f'{get_dt()} {color("[Progress] ", c="LC")} {color(str(f"{i_progress+1}/{len(enumerated_results)} ({current_page}/{_max_page})"), c="W")}')
                print(f'{get_dt()} ' + color('[Category] ', c='LC') + color(str(_search_q), c='W'))

                # Check: Library category directory exists
                if not os.path.exists(lib_path + '/' + _search_q):
                    os.makedirs(lib_path + '/' + _search_q, exist_ok=True)

                # Make filename from URL
                filename = make_file_name(book_url=results[i_progress])
                fname = lib_path + '/' + _search_q + '/' + filename

                # Output: Filename and download link
                print(f'{get_dt()} ' + color('[Book] ', c='LC') + color(str(filename), c='M'))
                print(f'{get_dt()} ' + color('[URL] ', c='LC') + color(str(enumerated_result), c='M'))

                if not os.path.exists(fname):

                    # Check: Filename exists in books_saved.txt
                    if fname not in success_downloads:
                        try:
                            # Download file
                            if download_file(_url=enumerated_result, _filename=fname, _timeout=86400, _chunk_size=8192,
                                             _clear_console_line_n=50, _chunk_encoded_response=False, _min_file_size=1024,
                                             _log=True) is True:

                                # Notification sound after platform check (Be compatible on Termux on Android)
                                if os.name in ('nt', 'dos'):
                                    if mute_default_player is False:
                                        play_thread = Thread(target=play)
                                        play_thread.start()

                        except Exception as e:

                            # Output: any issues
                            print(f'{get_dt()} [Exception.download] {e}')
                            print(f'{get_dt()} ' + color('[Download Failed]', c='R'))

                            # Remove the file if it was created to clean up after ourselves
                            if os.path.exists(fname):
                                os.remove(fname)
                    else:
                        print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File exists in records.', c='W'))
                else:
                    print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File already exists in filesystem.', c='W'))

                i_progress += 1

        else:
            print(f'{get_dt()} ' + color('[WARNING] ', c='Y') + color('Skipping page due to list misalignment.', c='W'))
            time.sleep(3)

        grand_library_supremo.display_grand_library()


# Get STDIN and parse
stdin = list(sys.argv)
if '-h' in stdin:
    grand_library_supremo_help.display_help()
else:
    grand_library_supremo.display_grand_library()

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
    if '-max' in stdin:
        idx = stdin.index('-max') + 1
        _max_page = int(stdin[idx])

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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
