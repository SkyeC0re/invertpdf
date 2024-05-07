#!/usr/bin/python3
"""
A simple script for inverting PDF files.

Usage:
python3 invertPDF.py input.pdf [-o output.pdf]

The script will create an inverted copy of the input file and save it to the output file.
If no output file is provided, the script will overwrite the input file.
"""

__author__ = 'Christoff van Zyl'
__copyright__ = '"Copyright 2021, invertPDF'
__license__ = 'GPL'

import argparse
import sys
from pathlib import Path

import pikepdf
from PyPDF2 import PdfReader
from pikepdf import Page, Name


def invertPDF(in_file, out_file):
    """
    Inverts a PDF and saves it elsewhere.

    Parameters:
    in_file: The file to invert.
    out_file: The destination of the inverted copy.
    """
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


def invert_file_to_folder(input_file, output_file: Path):
    """
    Converts all given files and places their inverted copies in the given folder under the same file names.

    Parameters:
    files: Array of file names to be converted.
    folder: The folder in which to put the inverted copies.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if output_file.exists():
        # add _inverted to the file name
        output_file = output_file.with_name(output_file.stem + '_inverted' + output_file.suffix)
        invertPDF(str(input_file), str(output_file))
        # delete original file
        input_file.unlink()
        # rename inverted file to original file name
        output_file.rename(input_file)
    else:
        invertPDF(str(input_file), str(output_file))
    print('Success: {}'.format(input_file.name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Invert the colors of a PDF file.')

    parser.add_argument('input', type=str, help='The path to the input PDF file.')
    parser.add_argument('-o', '--output', type=str, help='The output folder.', default=None)

    args = parser.parse_args()

    input_file = Path(args.input)
    output_file = Path(args.output or args.input)
    assert input_file.exists(), "PDF file does not exist."
    invert_file_to_folder(input_file, output_file)
