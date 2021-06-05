# invertPDF.py
A simple python3 script for inverting the colors of PDFs, whilst keeping the pdf format and structure of the document.\
Requirements:
* Python  3.6+
* pikepdf 2.12
* PyPDF2  1.26

## Usage:
python3 invertPDF.py [filename | foldername]\
If a folder is given as arguement (no arguement defaults to selecting the parent folder in which the script resides), the script selects all pdf files inside
the folder and saves the inverted copies of these PDFs inside a new folder: 'invertedPDFs', using the original file names. Similar behaviour is achieved by giving a file as arguement, except only that single file will be converted.

