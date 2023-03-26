    PDFDrive Downloader
    
    -k      Keyword    Specify a search string.
    -p      Page       Specify a page to start downloading from (optional). -p 1
    -max    Max        Specify a page to end downloading (optional). -max 3     
    -h      Help       Displays this help message.
    
    Developed and written by Benjamin Jack Cullen.



Features:

    Downloads all books on all pages.
    
    Optionally starts downloading from a specified page.
    
    Keeps track of what has already been downloaded for continuing operation accross different systems.



Notes:

    Downloader still requires extra handling for many things. serves the purpose for me:
    
    Downloads saved as < 100 bytes are flagged and deleted.
    
    Downloads > 100 bytes that save sucessfully may require extra handling and be otherwise unusable.
    
    Enumerates download url before ever landing on the final page containing the download link that contains the
    full download href as the download href takes time to populate.

    Any argument other than search query (-k) should be stated before -k as anything after -k will will treated as a query. 


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
