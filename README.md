This software may be temporarily or permenantly deprecated:

The target website may have just been updated to block this kind of thing. Upon inspection it appears
PDFDrive is now trying to force users to enable notifications in the browser before being able to
download, then once you have enabled notifications you will be spammed with crapware trying to 
get you to install crapware. Do not enable notiications for PDFDrive, its a scam.

You may use my new library genesis downloader: https://github.com/holographicSol/libGenv2
    

Grand Library Supremo (PDF Drive Downloader):

    [   PDF Drive Downloader   ]
    
    -k         Keyword       Specify a search string.
    -e         Exact Match   Enable a strict results filter. Default is off.
    -p         Page          Specify a page to start downloading from (optional). -p 1
    -P         Path          Specify save path (optional).
    -max       Max           Specify a page to end downloading (optional). -max 3
    --no-mem   No Memory     Do not use books_saved.txt when ascertaining if file will be downloaded.
    -v         Verbosity     Increase verbosity.
    -h         Help          Displays this help message.
    
    Developed and written by Benjamin Jack Cullen.



Features:

    Downloads all books on all pages.
    
    Optionally starts downloading from a specified page.
    
    Keeps track of what has already been downloaded for continuing operation accross different systems.



Notes:

    Keeps track of what has been downloaded so that downloading can continue efficiently accross multiple drives/systems when
    backing-up/sharing the books_saved.txt file accross multiple instances of pdfDrive.

    A light library manager is provided as this new version of pdfdrive is not backwards compatible in regards to the books_saved.txt.
    You can use library manager to create a new books_saved.txt that is compatible with this new version of pdfdrive. (--enumerate-library)
    Also library manager can remove PDF files that may have been too large to download successfully using the presious version.
    If you have been using the previous version(s) of pdfdrive then please:
        1. library_manager --remove-corrupted
        2. library_manager --enumerate-library
        3. copy the new books_saved.txt to pdfDrive loacation.

    Any argument other than search query (-k) should be stated before -k as anything after -k will will treated as a query.

    Speed Increase:
    Some operations are now async however I would not like to async everything just yet in case we get blocked/timedout
    which will slow us down.


Windows:

    In Powershell/CMD:
    1. git clone https://github.com/holographicSol/pdfDrive
    2. cd ./pdfDrive
    3. ./requirements.bat
    4. python ./pdfdrive.py -h

Termux for low-power/portability operation:

    Note: Reccomend rotating device horizontally for optimum viewing experience.
    In Termux application:
    1. git clone https://github.com/holographicSol/pdfDrive
    2. cd ./pdfDrive
    3. ./requirements.sh
    4. python ./pdfdrive.py -h


Executable:

    https://drive.google.com/drive/folders/1Vs96-lEA9_DKl_GdyFbKI9yN6Bhka_0s?usp=share_link


Linux:

    * Use steps from Termux ^.


Simple Example:

    pdfdrive -k big pharma

Set a start page to save time:

    pdfdrive -p 2 -k big pharma

Set start page and library path:

    pdfdrive -p 2 -P "D:\Books" -k encyclopedia

Set start page, library path and use exact match argument for a more strict results filter:

    pdfdrive -p 2 -P "D:\Books" -e -k encyclopedia

Download with amnesia to previously downloaded files (a file exists check will still be performed):

    pdfdrive --no-mem -p 2 -P "D:\Books" -e -k encyclopedia

Extra Note:

    As of 28/04/23 books_saved.txt and or books_failed.txt may not be backwards compatible and should
    be deleted if experiencing encoding errors because of the new way this software handles those files.
    Any issues feel free to submit bugs.
    For new features feel free to ask.
    Download the data and enjoy.

Developers:

    Logic:

    Step 1: Async phase one and phase two per page. (Per page limit to not get kicked from the server).

    Step 2: Download synchronously (dont get kicked) while using async read/write modules because they
    are faster at it even if synchronously applied.

    Step 3: Back to step 1 for each page.
