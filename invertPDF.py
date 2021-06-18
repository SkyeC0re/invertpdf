'''
A simple script for inverting PDF files.
Requirements:
 - Python 3.6+
 - pikepdf 2.12
 - PyPDF2 1.26

Usage:
python3 invertPDF.py [file/folder 1] [file/folder 2] ...

For each folder given as arguement, all PDF files inside the folder will be inverted and the inverted copies will be saved
inside a new folder 'invertedPDFs' created inside the given folder, using the original file names for the inverted copies.
For all files given as input, the file is converted in a similar manner, with the 'invertedPDFs' folder now located in the
parent folder of the file. If no arguements are given, the parent folder of the script is treated as input.
'''

__author__ = 'Christoff van Zyl'
__copyright__ = '"Copyright 2021, invertPDF'
__license__ = 'GPL'


from pathlib import Path
import sys
import pikepdf
from PyPDF2 import PdfFileReader
from pikepdf import Page, Name



def invertPDF(in_file, out_file):
    '''
    Inverts a PDF and saves it elsewhere.

    Parameters:
    in_file: The file to invert.
    out_file: The destination of the inverted copy.
    '''
    #Setup
    boxstr = 'q \n1.0 1.0 1.0 rg\n{} gs\n{} {} {} {} re\n f\n Q'
    blend_dict = pikepdf.Dictionary(Type=Name('/ExtGState'), BM=Name('/Difference'), ca=1, CA=1)
    xobj_dict = pikepdf.Dictionary({'/Type':Name('/XObject') ,'/SubType':Name('/Form'),'/Group':{'/S':Name('/Transparency'), '/CS':Name('/DeviceRGB')}})
    do_str = '{} Do\n'

    num_pages = 0
    boxes = []

    #Read approximate page coordinate sizes using different library (pikepdf's mediabox functionality appears broken (pikepdf 2.12))
    pdf = PdfFileReader(in_file)
    num_pages = pdf.getNumPages()
    for i in range(num_pages):
        tmp = []
        box = pdf.getPage(i).mediaBox
        for val in box:
            tmp.append(float(val))
        
        x_add = (tmp[2] - tmp[0]) * 0.3
        y_add = (tmp[3] - tmp[1]) * 0.3
        tmp[0] -= x_add / 2
        tmp[2] += x_add
        tmp[1] -= y_add / 2
        tmp[3] += y_add
        boxes.append(tmp)

    with pikepdf.open(in_file) as pdf:
        for i in range(num_pages):
            page = pdf.pages[i]
            ppage = Page(page)
            #Add Blending Mode
            name = ppage.add_resource(blend_dict, Name('/ExtGState'))
            #Create XObject
            xobj = pdf.make_stream(bytes(boxstr.format(name, *boxes[i]), 'utf8'), xobj_dict)
            #Add it before (to invert page) and after content (to invert content)
            page.page_contents_add(xobj, prepend=True)
            page.page_contents_add(xobj)
            
        pdf.save(out_file)

def invert_files_to_folder(files, folder):
    '''
    Converts all given files and places their inverted copies in the given folder under the same file names.

    Parameters:
    files: Array of file names to be converted.
    folder: The folder in which to put the inverted copies.
    '''
    folder.mkdir(parents=True, exist_ok=True)
    for ifile in files:
        try:
                inverted_pdf_file = folder / ifile.name
                invertPDF(str(ifile), str(inverted_pdf_file))
                print('Success: {}'.format(ifile.name))
        except:
                print('Failed: {}'.format(ifile.name))

if __name__ == '__main__':
    #Convert all pdfs in directory
    if len(sys.argv) == 1:
        path = Path(__file__).parent
        files_to_invert = path.glob('*.pdf')
        invert_files_to_folder(files_to_invert, path / 'invertedPDFs')


    #Convert specfic PDF or PDFs in specific directory
    else:
        for i in range(1, len(sys.argv)):
            try:
                path = Path(sys.argv[i])    
            
                if path.is_dir():
                    files_to_invert = path.glob('*.pdf')
                   
                elif path.is_file():
                    files_to_invert = [path]
                    path = path.parent
                invert_files_to_folder(files_to_invert, path / 'invertedPDFs')
            except:
                    print("Folder or File arguement failed: {}".format(sys.argv[i]))