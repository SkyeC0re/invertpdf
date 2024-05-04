# invertPDF.py
A simple python3 script for inverting the colors of PDFs, whilst keeping the pdf format and vector nature of the document.

## Usage:
python3 invertPDF.py [filename1 | foldername1] [filename2 | foldername2] ...\
For each folder given as arguement, all PDF files inside the folder will be inverted and the inverted copies will be saved inside the given folder, using the original file names for the inverted copies (possibly overwriting the original file). 
If no arguments are given, the parent folder of the script is treated as input.
