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


Distribution version:

    https://drive.google.com/drive/folders/1Vs96-lEA9_DKl_GdyFbKI9yN6Bhka_0s?usp=sharing


Example:

    pdfDrive -k big pharma
