# invertPDF.py
A simple python3 script for inverting the colors of PDFs, whilst keeping the pdf format and vector nature of the document.

## Usage:
python3 invertPDF.py [filename1 | foldername1] [filename2 | foldername2] ...\
For each folder given as arguement, all PDF files inside the folder will be inverted and the inverted copies will be saved
inside a new folder 'invertedPDFs' created inside the given folder, using the original file names for the inverted copies.
For all files given as input, the file is converted in a similar manner, with the 'invertedPDFs' folder now located in the
parent folder of the file. If no arguements are given, the parent folder of the script is treated as input.

