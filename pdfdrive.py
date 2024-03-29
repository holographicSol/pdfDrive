""" Written by Benjamin Jack Cullen """
import dataclasses
import os
import sys
import time
import shutil
import datetime

import bs4
import colorama
import codecs
import asyncio
import aiohttp
import aiofiles
import aiofiles.os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dataclasses import dataclass
import pdfdrive_help

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

# Colorama requires initialization before use
colorama.init()


# return headers with a random user agent
def user_agent():
    ua = UserAgent()
    return {'User-Agent': str(ua.random)}


# create a dataclass for performance increase (instead of plugging everything into function arguments)
@dataclass(slots=True)
class DownloadArgs:
    verbose: bool
    url: list
    filename: str
    filepath: str
    chunk_size: int
    clear_n_chars: int
    min_file_size: int
    log: bool
    success_downloads: list
    failed_downloads: list
    ds_bytes: bool


# set master timeout
master_timeout = 86400  # 24h

# set scraper timeout/connection-issue retry time intervals
timeout_retry = 2
connection_error_retry = 10

# configure options for scraping
scrape_timeout = aiohttp.ClientTimeout(
    total=None,  # default value is 5 minutes, set to `None` for unlimited timeout
    sock_connect=master_timeout,  # How long to wait before an open socket allowed to connect
    sock_read=master_timeout  # How long to wait with no data being read before timing out
)
client_args = dict(
    trust_env=True,
    timeout=scrape_timeout
)

# configure options for downloading files
download_timeout = aiohttp.ClientTimeout(
    total=None,  # default value is 5 minutes, set to `None` for unlimited timeout
    sock_connect=master_timeout,  # How long to wait before an open socket allowed to connect
    sock_read=master_timeout  # How long to wait with no data being read before timing out
)
client_args_download = dict(
    trust_env=True,
    timeout=download_timeout
)


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


def play():
    """ notification sound """
    if os.name in ('nt', 'dos'):
        player_default.play()
        time.sleep(1)


def make_file_name(_book_url: str) -> str:
    """ create filenames from book URLs """
    book_url = _book_url.replace('https://www.pdfdrive.com//', '')
    idx_book_url = book_url.rfind('-')
    book_url = book_url[:idx_book_url]
    book_name = book_url+'.pdf'
    return book_name


def out_of_disk_space(_chunk_size: int) -> bool:
    total, used, free = shutil.disk_usage("./")
    if free > _chunk_size + 1024:
        return False
    else:
        return True


async def download_file(dyn_download_args: dataclasses.dataclass) -> bool:

    """
    This function is currently designed to run synchronously while also having asynchronous features.
    Make use of async read/write and aiohhttp while also not needing to make this function non-blocking -
    (This function runs one instance at a time to prevent being kicked). """

    _chunk_size = dyn_download_args.chunk_size

    async with aiohttp.ClientSession(headers=user_agent(), **client_args_download) as session:
        async with session.get(dyn_download_args.url[1]) as resp:
            if dyn_download_args.verbose is True:
                print(f'{get_dt()} ' + color('[Response] ', c='Y') + color(str(resp.status), c='LC'))
            if resp.status == 200:

                # keep track of how many bytes have been downloaded
                _sz = int(0)

                # open file to write the bytes into
                async with aiofiles.open(dyn_download_args.filepath+'.tmp', mode='wb') as handle:

                    # iterate over chunks of bytes in the response
                    async for chunk in resp.content.iter_chunked(_chunk_size):

                        # storage check:
                        if await asyncio.to_thread(out_of_disk_space, _chunk_size=dyn_download_args.chunk_size) is False:

                            # write chunk to the temporary file
                            await handle.write(chunk)

                            # output: display download progress
                            _sz += int(len(chunk))
                            print(' ' * dyn_download_args.clear_n_chars, end='\r', flush=True)
                            if dyn_download_args.ds_bytes is False:
                                print(f'[DOWNLOADING] {str(convert_bytes(_sz))}', end='\r', flush=True)
                            else:
                                print(f'[DOWNLOADING] {str(_sz)} bytes', end='\r', flush=True)
                        else:
                            # output: out of disk space
                            print(' ' * dyn_download_args.clear_n_chars, end='\r', flush=True)
                            print(str(color(s='[WARNING] OUT OF DISK SPACE! Download terminated.', c='Y')), end='\r', flush=True)

                            # delete temporary file if exists
                            if os.path.exists(dyn_download_args.filepath + '.tmp'):
                                await handle.close()
                                await aiofiles.os.remove(dyn_download_args.filepath + '.tmp')
                            # exit.
                            print('\n\n')
                            exit(0)
                await handle.close()

    if os.path.exists(dyn_download_args.filepath+'.tmp'):

        # check: temporary file worth keeping? (<1024 bytes would be less than 1024 characters, reduce this if needed)
        # - sometimes file exists on a different server, this software does not intentionally follow any external links,
        # - if the file is in another place then a very small file may be downloaded because ultimately the file we
        #   wanted was not present and will then be detected and deleted.
        if os.path.getsize(dyn_download_args.filepath+'.tmp') >= dyn_download_args.min_file_size:
            if dyn_download_args.verbose is True:
                print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Attempting to replace {dyn_download_args.filepath}.tmp', c='LC'))

            # create final download file from temporary file
            await aiofiles.os.replace(dyn_download_args.filepath+'.tmp', dyn_download_args.filepath)

            if dyn_download_args.verbose is True:
                print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Created {dyn_download_args.filepath}', c='LC'))

            # check: clean up the temporary file if it exists.
            if os.path.exists(dyn_download_args.filepath+'.tmp'):
                await aiofiles.os.remove(dyn_download_args.filepath + '.tmp')

            # display download success (does not guarantee a usable file, some checks are performed before this point)
            if os.path.exists(dyn_download_args.filepath):

                if dyn_download_args.verbose is True:
                    print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Replaced {dyn_download_args.filepath}.tmp successfully', c='LC'))

                print(f'{get_dt()} ' + color('[Downloaded Successfully]', c='G'))

                # add book to saved list. multi-drive/system memory (continue where you left off on another disk/sys)
                if dyn_download_args.log is True:
                    if dyn_download_args.filename not in success_downloads:
                        success_downloads.append(dyn_download_args.filename)
                        async with aiofiles.open('./books_saved.txt', mode='a+', encoding='utf8') as handle:
                            await handle.write(dyn_download_args.filename + '\n')
                        await handle.close()

                    # read file and check if new entry exists
                    if dyn_download_args.verbose is True:
                        async with aiofiles.open('./books_saved.txt', mode='r', encoding='utf8') as handle:
                            text = await handle.read()
                        await handle.close()
                        lines = text.split('\n')
                        if dyn_download_args.filename in lines:
                            print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Successfully appended {dyn_download_args.filename} to books_saved.txt', c='LC'))
                        else:
                            print(f'{get_dt()} ' + color('[File] ', c='R') + color(f'Failed to append {dyn_download_args.filename} to books_saved.txt', c='LC'))

                return True

            else:
                if dyn_download_args.verbose is True:
                    print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Issue replacing {dyn_download_args.filepath}.tmp', c='LC'))

        else:
            print(f'{get_dt()} ' + color(f'[Download Failed] ', c='R') + str('External link may be required to download this file.'))

            # add books base url to failed only if file < 1024. (external link filter)
            if dyn_download_args.log is True:
                if dyn_download_args.url[0] not in failed_downloads:
                    if dyn_download_args.verbose is True:
                        print(f'{get_dt()} ' + color('[Log] ', c='Y') + color(f'Logging {dyn_download_args.url[0]} as failed (possibly external link)', c='LC'))
                    failed_downloads.append(dyn_download_args.url[0])
                    async with aiofiles.open('./books_failed.txt', mode='a+', encoding='utf8') as handle:
                        await handle.write(str(dyn_download_args.url[0]) + '\n')
                    await handle.close()

                # read file and check if new entry exists
                if dyn_download_args.verbose is True:
                    async with aiofiles.open('./books_failed.txt', mode='r', encoding='utf8') as handle:
                        text = await handle.read()
                    await handle.close()
                    lines = text.split('\n')
                    if dyn_download_args.url[0] in lines:
                        print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Successfully appended {dyn_download_args.url[0]} to books_failed.txt', c='LC'))
                    else:
                        print(f'{get_dt()} ' + color('[File] ', c='R') + color(f'Failed to append {dyn_download_args.url[0]} to books_failed.txt', c='LC'))

            # check: clean up the temporary file if it exists.
            if os.path.exists(dyn_download_args.filename+'.tmp'):
                os.remove(dyn_download_args.filename+'.tmp')

            # check: path still exists
            if dyn_download_args.verbose is True:
                if not os.path.exists(dyn_download_args.filename+'.tmp'):
                    print(f'{get_dt()} ' + color('[File] ', c='Y') + color(f'Successfully removed {dyn_download_args.filepath}', c='LC'))
                else:
                    print(f'{get_dt()} ' + color('[File] ', c='R') + color(f'Failed to remove {dyn_download_args.filepath}', c='LC'))

            return False


def get_soup(_body: str) -> bs4.BeautifulSoup:
    """ return soup """
    return BeautifulSoup(_body, 'html.parser')


def pass_domain_check(_book_urls: list, _level: int) -> bool:
    pass_bool = True
    for book_url in _book_urls:
        if _level is int(1):
            if not str(book_url).startswith('https://www.pdfdrive.com/'):
                pass_bool = False
                break
        elif _level is int(2):
            if not str(book_url[0]).startswith('https://www.pdfdrive.com/') or not str(book_url[1]).startswith('https://www.pdfdrive.com/'):
                pass_bool = False
                break
    return pass_bool


def remove_unacceptable_domains(_book_urls: list, _level: int) -> list:
    new_list = []
    for book_url in _book_urls:
        if _level is int(1):
            if str(book_url).startswith('https://www.pdfdrive.com/'):
                new_list.append(book_url)
        elif _level is int(2):
            if str(book_url[0]).startswith('https://www.pdfdrive.com/') and str(book_url[1]).startswith('https://www.pdfdrive.com/'):
                new_list.append(book_url)
    return new_list


def parse_soup_phase_one(_soup: bs4.BeautifulSoup) -> list:
    """ parse soup from phase one (parse for book URLs) """
    book_urls = []
    for link in _soup.find_all('a'):
        href = (link.get('href'))
        if str(href).endswith('.html'):
            if 'auth/login' not in str(href):
                if 'home/setLocal' not in str(href):
                    book_link = 'https://www.pdfdrive.com/' + str(href)
                    if book_link not in book_urls:
                        book_urls.append(book_link)
    return book_urls


def parse_soup_phase_two(_soup: bs4.BeautifulSoup) -> str:
    """ parse soup from phase two (parse book URLs (found in phase one) for a specific tag) """
    data_preview = ''
    for link in _soup.find_all('button'):
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
        return f'https://www.pdfdrive.com//download.pdf?id={data_id}&h={h_id}&u=cache&ext=pdf'


async def scrape_pages(url: str) -> list:
    """ scrape for book URLs """
    book_urls = []
    try:
        _headers = user_agent()
        async with aiohttp.ClientSession(headers=_headers, **client_args) as session:
            async with session.get(url) as resp:
                _body = await resp.text(encoding=None, errors='ignore')
                _soup = await asyncio.to_thread(get_soup, _body=_body)
                book_urls = await asyncio.to_thread(parse_soup_phase_one, _soup=_soup)
    except asyncio.exceptions.TimeoutError:
        print(f'{get_dt()} ' + color(f'[TIMEOUT] Initial scraper timeout. Retrying in {timeout_retry} seconds.', c='Y'))
        await asyncio.sleep(timeout_retry)
        await scrape_pages(url)

    except aiohttp.ClientConnectorError:
        print(f'{get_dt()} ' + color(f'[CONNECTION ERROR] Initial scraper connection error. Retrying in {connection_error_retry} seconds.', c='Y'))
        await asyncio.sleep(timeout_retry)
        await enumerate_links(url)
    return book_urls


async def enumerate_links(url: str) -> list:
    """ scrape for book download links """
    book_urls = []
    try:
        _headers = user_agent()
        async with aiohttp.ClientSession(headers=_headers, **client_args) as session:
            async with session.get(url) as resp:
                _body = await resp.text(encoding=None, errors='ignore')
                _soup = await asyncio.to_thread(get_soup, _body=_body)
                if _soup:
                    data = await asyncio.to_thread(parse_soup_phase_two, _soup=_soup)
                    # append together for list alignment later (when creating filenames for current download link)
                    book_urls.append([url, data])

    except asyncio.exceptions.TimeoutError:
        print(f'{get_dt()} ' + color(f'[TIMEOUT] Enumeration timeout. Retrying in {timeout_retry} seconds.', c='Y'))
        await asyncio.sleep(timeout_retry)
        await enumerate_links(url)

    except aiohttp.ClientConnectorError:
        print(f'{get_dt()} ' + color(f'[CONNECTION ERROR] Enumeration connection error. Retrying in {connection_error_retry} seconds.', c='Y'))
        await asyncio.sleep(timeout_retry)
        await enumerate_links(url)
    return book_urls


async def main(_i_page=1, _max_page=88, _exact_match=False, _search_q='', _lib_path='./library/',
               _success_downloads=None, _failed_downloads=None, _ds_bytes=False, _verbose=False,
               _allow_external=False):

    # Phase One: Setup async scaper to get book URLs (one page at a time to prevent getting kicked from the server)
    if _success_downloads is None:
        _success_downloads = []
    for current_page in range(i_page, _max_page):

        # create URL to scrape using query and exact match bool
        url = str('https://www.pdfdrive.com/search?q=' + str(_search_q).replace(' ', '+'))
        if exact_match is True:
            url = str('https://www.pdfdrive.com/search?q=' + str(_search_q).replace(' ', '+') + '&pagecount=&pubyear=&searchin=&em=1&page=' + str(i_page))
        url = url + '&pagecount=&pubyear=&searchin=&page='
        url = url+str(current_page)

        print(f'{get_dt()} ' + color('[Search] ', c='LC') + color(search_q, c='W'))
        print(f'{get_dt()} ' + color('[Page] ', c='LC') + f'Page: {current_page}')
        print(f'{get_dt()} ' + color('[Scanning] ', c='LC') + f'{url}')
        print(f'{get_dt()} ' + color('[Phase One] ', c='LC') + f'Gathering initial links...')

        tasks = []
        t0 = time.perf_counter()
        task = asyncio.create_task(scrape_pages(url))
        tasks.append(task)
        results = await asyncio.gather(*tasks)
        if _verbose is True:
            print(f'{get_dt()} ' + color('[Results] ', c='Y') + color(str(results), c='LC'))
        for result in results:
            if result is None:
                del result
        results[:] = [item for sublist in results for item in sublist if item is not None]
        if _verbose is True:
            print(f'{get_dt()} ' + color('[Results Formatted] ', c='Y') + color(str(results), c='LC'))

        # Domain checks: Domain should always be pdfdrive.com because of the way URLs are generated, however, make sure
        # quickly in case code is changed later in the parsers and also because then we can turn follow external links
        # on/off later if we like to optionally increase download yield.
        if _allow_external is False:
            if pass_domain_check(_book_urls=list(results), _level=int(1)) is False:
                print(f'{get_dt()} ' + color('[Domain Check] ', c='R') + color('Domain checks failed. One or more URLs not not match the accepted domain name.', c='R'))
                results = remove_unacceptable_domains(_book_urls=list(results), _level=int(1))
                print(f'{get_dt()} ' + color('[Domain Check] ', c='Y') + color('Attempting to remove external links.', c='Y'))
                print(f'{get_dt()} ' + color('[Results] ', c='Y') + color(str(results), c='LC'))
            if pass_domain_check(_book_urls=list(results), _level=int(1)) is True:
                print(f'{get_dt()} ' + color('[Domain Check] ', c='Y') + color('Domain checks passed.', c='G'))
            else:
                print(f'{get_dt()} ' + color('[Domain Check] ', c='R') + color('Problem removing external links.', c='R'))
                print('')
                break

        # Displays Zero if none found
        print(f'{get_dt()} ' + color('[Results] ', c='Y') + f'{len(results)}')
        print(f'{get_dt()} ' + color('[Phase One Time] ', c='LC') + f'{time.perf_counter()-t0}')

        if len(results) == int(0):
            print(f'{get_dt()} ' + color('[Max Page] ', c='LC') + f'No results were found on page {current_page}. Exiting.')
            print('\n\n')
            break

        # Phase Two: Setup async scaper to get book download links for each book on the current page
        print(f'{get_dt()} ' + color('[Phase Two] ', c='LC') + f'Enumerating Links...')
        t0 = time.perf_counter()
        tasks = []
        for result in results:
            task = asyncio.create_task(enumerate_links(result))
            tasks.append(task)
        enumerated_results = await asyncio.gather(*tasks)
        if _verbose is True:
            print(f'{get_dt()} ' + color('[Enumerated Results] ', c='Y') + color(str(enumerated_results), c='LC'))
        enumerated_results[:] = [item for sublist in enumerated_results for item in sublist if item is not None]
        if _verbose is True:
            print(f'{get_dt()} ' + color('[Enumerated Results Formatted] ', c='Y') + color(str(enumerated_results), c='LC'))
        print(f'{get_dt()} ' + color('[Enumerated Results] ', c='LC') + f'{len(enumerated_results)}')
        print(f'{get_dt()} ' + color('[Phase Two Time] ', c='LC') + f'{time.perf_counter()-t0}')

        # Domain checks: Domain should always be pdfdrive.com because of the way URLs are generated, however, make sure
        # quickly in case code is changed later in the parsers and also because then we can turn follow external links
        # on/off later if we like to optionally increase download yield.
        if _allow_external is False:
            if pass_domain_check(_book_urls=list(enumerated_results), _level=2) is False:
                print(f'{get_dt()} ' + color('[Domain Check] ', c='R') + color('Domain checks failed. One or more URLs not not match the accepted domain name.', c='R'))
                enumerated_results = remove_unacceptable_domains(_book_urls=list(enumerated_results), _level=2)
                print(f'{get_dt()} ' + color('[Domain Check] ', c='Y') + color('Attempting to remove external links.', c='Y'))
                print(f'{get_dt()} ' + color('[Enumerated Results] ', c='Y') + color(str(enumerated_results), c='LC'))
            if pass_domain_check(_book_urls=list(enumerated_results), _level=2) is True:
                print(f'{get_dt()} ' + color('[Domain Check] ', c='Y') + color('Domain checks passed.', c='G'))
            else:
                print(f'{get_dt()} ' + color('[Domain Check] ', c='R') + color('Problem removing external links.', c='R'))
                print('')
                break

        # Keep track of current page
        i_progress = 0

        # Synchronously (for now) attempt to download each book on the current page.
        for enumerated_result in enumerated_results:
            print('_' * 28)
            print('')
            print(f'{get_dt()} {color("[Progress] ", c="LC")} {color(str(f"{i_progress+1}/{len(enumerated_results)} ({current_page}/{_max_page})"), c="W")}')
            print(f'{get_dt()} ' + color('[Category] ', c='LC') + color(str(_search_q), c='W'))
            if _verbose is True:
                print(f'{get_dt()} ' + color('[Handling Enumerated Result] ', c='Y') + color(str(enumerated_result), c='LC'))

            if enumerated_result[0] is not None and enumerated_result[1] is not None:

                # Check: Library category directory exists
                if not os.path.exists(lib_path + '/' + _search_q):
                    os.makedirs(lib_path + '/' + _search_q, exist_ok=True)

                # Make filename from URL
                filename = make_file_name(_book_url=enumerated_result[0])
                filepath = lib_path + '/' + _search_q + '/' + filename

                # Output: Filename and download link
                print(f'{get_dt()} ' + color('[Book] ', c='LC') + color(str(filename), c='W'))
                print(f'{get_dt()} ' + color('[URL] ', c='LC') + color(str(enumerated_result[1]), c='W'))

                # Check: Filename exists in filesystem save location
                if not os.path.exists(filepath):

                    # Check: Filename exists in books_saved.txt
                    if filename not in success_downloads:

                        # Check: Base URL not in failed downloads (failed downloads are specifically < 1024b files)
                        if enumerated_result[0] not in failed_downloads:
                            try:
                                # Download file
                                dyn_download_args = DownloadArgs(verbose=_verbose,
                                                                 url=enumerated_result,
                                                                 filename=filename,
                                                                 filepath=filepath,
                                                                 chunk_size=8192,
                                                                 clear_n_chars=50,
                                                                 min_file_size=1024,
                                                                 log=True,
                                                                 success_downloads=_success_downloads,
                                                                 failed_downloads=_failed_downloads,
                                                                 ds_bytes=_ds_bytes)

                                dl_tasks = []
                                dl_task = asyncio.create_task(download_file(dyn_download_args))
                                dl_tasks.append(dl_task)
                                dl = await asyncio.gather(*dl_tasks)

                                if dl[0] is True:

                                    # Notification sound after platform check (Be compatible on Termux on Android)
                                    if os.name in ('nt', 'dos'):
                                        if mute_default_player is False:
                                            play_thread = Thread(target=play)
                                            play_thread.start()

                            except Exception as e:
                                # Output: any issues
                                print(f'{get_dt()} ' + color(f'[Exception.download] {e}', c='R'))
                                print(f'{get_dt()} ' + color('[Download Failed]', c='R'))

                                # Remove the file if it was created to clean up after ourselves
                                if os.path.exists(filepath):
                                    os.remove(filepath)
                                # check: clean up the temporary file if it exists.
                                if os.path.exists(filepath + '.tmp'):
                                    os.remove(filepath + '.tmp')
                        else:
                            print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File exists in failed downloads, may require an external link to download.', c='W'))
                    else:
                        print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File exists in records.', c='W'))
                else:
                    print(f'{get_dt()} ' + color('[Skipping] ', c='G') + color('File already exists in filesystem.', c='W'))

            i_progress += 1

        print('')
        print('')
        print('[   PDF Drive Downloader   ]')
        print('')


# Get STDIN and parse
stdin = list(sys.argv)
if '-h' in stdin:
    pdfdrive_help.display_help()
else:
    print('')
    print('')
    print('[   PDF Drive Downloader   ]')
    print('')

    verbose = False
    if '-v' in stdin:
        verbose = True

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
    search_q = ''
    idx = stdin.index('-k')+1
    i = 0
    for x in stdin:
        if i >= int(idx):
            search_q = search_q + ' ' + x
        i += 1
    search_q = search_q[1:]

    """ Max Pages """
    max_page = 88
    if '-max' in stdin:
        idx = stdin.index('-max') + 1
        max_page = int(stdin[idx])

    """ Display Download Progress In Bytes """
    ds_bytes = False
    if '-bytes' in stdin:
        ds_bytes = True

    """ Use Download Log """
    success_downloads = []
    failed_downloads = []
    if '--no-mem' not in stdin:
        # saved downloads
        if not os.path.exists('./books_saved.txt'):
            open('./books_saved.txt', 'w').close()
        with codecs.open('./books_saved.txt', 'r', encoding='utf8') as fo:
            for line in fo:
                line = line.strip()
                if line not in success_downloads:
                    success_downloads.append(line)
        # failed downloads
        if not os.path.exists('./books_failed.txt'):
            open('./books_failed.txt', 'w').close()
        with codecs.open('./books_failed.txt', 'r', encoding='utf8') as fo:
            for line in fo:
                line = line.strip()
                if line not in failed_downloads:
                    failed_downloads.append(line)
        fo.close()

    """ Allow external links to be followed """
    allow_external = False

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(_i_page=i_page, _max_page=max_page, _exact_match=exact_match, _search_q=search_q,
                                 _lib_path=lib_path, _success_downloads=success_downloads,
                                 _failed_downloads=failed_downloads, _ds_bytes=ds_bytes, _verbose=verbose,
                                 _allow_external=allow_external))
