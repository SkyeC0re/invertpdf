#!/usr/bin/python3
'''
A simple script for inverting PDF files.

Usage:
python3 invertPDF.py [file/folder 1] [file/folder 2] ...

For each folder given as arguement, all PDF files inside the folder will be inverted and the inverted copies will be saved
inside the given folder, using the original file names for the inverted copies.
For all files given as input, the file is converted in a similar manner, with the pdfs now located in the
parent folder of the file. If no arguements are given, the parent folder of the script is treated as input.
'''

__author__ = 'Christoff van Zyl'
__copyright__ = '"Copyright 2021, invertPDF'
__license__ = 'GPL'

import sys
from pathlib import Path

import pikepdf
from PyPDF2 import PdfReader
from pikepdf import Page, Name


def invertPDF(in_file, out_file):
    '''
    Inverts a PDF and saves it elsewhere.

    Parameters:
    in_file: The file to invert.
    out_file: The destination of the inverted copy.
    '''
    # Setup
    blend_dict = pikepdf.Dictionary(Type=Name('/ExtGState'), BM=Name('/Exclusion'), ca=1, CA=1)
    non_blend_dict = pikepdf.Dictionary(Type=Name('/ExtGState'), ca=1, CA=1)
    xobj_dict = pikepdf.Dictionary({'/Type': Name('/XObject'), '/SubType': Name('/Form'),
                                    '/Group': {'/S': Name('/Transparency'), '/CS': Name('/DeviceRGB')}})

    num_pages = 0
    boxes = []

    # Read approximate page coordinate sizes using different library (pikepdf's mediabox functionality appears broken (pikepdf 2.12))
    pdf = PdfReader(in_file)
    num_pages = len(pdf.pages)
    for i in range(num_pages):
        box = pdf.pages[i].mediabox

        min_c = float(min(box))
        max_c = float(max(box))
        add = (max_c - min_c) * 10

        min_c -= add
        max_c += add
        boxes.append([min_c, min_c, max_c - min_c, max_c - min_c])

    with pikepdf.open(in_file) as pdf:
        for i in range(num_pages):
            page = Page(pdf.pages[i])
            # Add Dictionaries to Page
            name = page.add_resource(blend_dict, Name('/ExtGState'))
            name2 = page.add_resource(non_blend_dict, Name('/ExtGState'))
            # Create rectangles
            front_rect = pdf.make_stream(
                bytes('q \n0.9 0.9 0.9 rg\n{} gs\n{} {} {} {} re\n f\n Q'.format(name, *boxes[i]), 'utf8'), xobj_dict)
            back_rect = pdf.make_stream(
                bytes('q \n1.0 1.0 1.0 rg\n{} gs\n{} {} {} {} re\n f\n Q'.format(name2, *boxes[i]), 'utf8'))
            # Add Rectangles to page
            page.contents_add(back_rect, prepend=True)
            page.contents_add(front_rect)

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
            # add _inverted to the file name
            inverted_pdf_file = folder / (ifile.stem + '_inverted.pdf')
            invertPDF(str(ifile), str(inverted_pdf_file))
            print('Success: {}'.format(ifile.name))
        except Exception as e:
            print('Failed: {}'.format(ifile.name))
            print(e)


if __name__ == '__main__':
    # Convert all pdfs in directory
    if len(sys.argv) == 1:
        path = Path.cwd()
        files_to_invert = path.glob('*.pdf')
        invert_files_to_folder(files_to_invert, path)


    # Convert specfic PDF or PDFs in specific directory
    else:
        for i in range(1, len(sys.argv)):
            try:
                path = Path(sys.argv[i])

                if path.is_dir():
                    files_to_invert = path.glob('*.pdf')

                elif path.is_file():
                    files_to_invert = [path]
                    path = path.parent
                invert_files_to_folder(files_to_invert, path)
            except:
                print("Folder or File arguement failed: {}".format(sys.argv[i]))