    PDFDrive Downloader
    
    -k         Keyword       Specify a search string.
    -e         Exact Match   Enable a strict results filter. Default is off.
    -p         Page          Specify a page to start downloading from (optional). -p 1
    -P         Path          Specify save path (optional).
    -max       Max           Specify a page to end downloading (optional). -max 3
    --no-mem   No Memory     Do not use books_saved.txt when ascertaining if file will be downloaded.
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

Windows:

    In Powershell/CMD:
    1. git clone https://github.com/holographicSol/pdfDrive
    2. cd ./pdfDrive
    3. ./requirements.bat
    4. python ./pdfDrive.py -h

Termux for low-power/portability operation:

    In Termux application:
    1. git clone https://github.com/holographicSol/pdfDrive
    2. cd ./pdfDrive
    3. ./requirements.sh
    4. python ./pdfDrive.py -h


Linux:

    * Use steps from Termux ^.


Simple Example:

    pdfDrive -k big pharma

Set a start page to save time:

    pdfDrive -p 2 -k big pharma

Set start page and library path:

    pdfDrive -p 2 -P "D:\Books" -k encyclopedia

Set start page, library path and use exact match argument for a more strict results filter:

    pdfDrive -p 2 -P "D:\Books" -e -k encyclopedia

Download with amnesia to previously downloaded files (a file exists check will still be performed):

    pdfDrive --no-mem -p 2 -P "D:\Books" -e -k encyclopedia
