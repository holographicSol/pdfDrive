
PDFDrive Downloader

-k      Keyword    Specify a search string.
-p      Page       Specify a page to start downloading from (optional).
-max    Max        Specify max pages to download (optional).
-h      Help       Displays this help message.

Developed and written by Benjamin Jack Cullen.


Downloads all books on all pages.

Optionally starts downloading from a specified page.

Keeps track of what has already been downloaded for continuing operation accross different systems.


Downloader still requires extra handling for many things. serves the purpose for me:

Downloads saved as < 100 bytes are flagged and deleted.

Downloads > 100 bytes that save sucessfully may require extra handling and be otherwise unusable.

Enumerates download url before ever landing on the final page containing the download link that contains the
full download href as the download href takes time to populate.

example:
pdfDrive -k big pharma
