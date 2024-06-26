#!/usr/bin/python3
'''
A simple script for inverting the color of PDF files.
'''

__author__ = 'Christoff van Zyl'
__copyright__ = '"Copyright 2021, invertPDF'
__license__ = 'GPL'

from pathlib import Path
import pikepdf
from PyPDF2 import PdfReader
from pikepdf import Page, Name
import pikepdf


def invertPDF(in_file, out_file, inv_ratio: float = 1.0, scribble_page_density: int = 0):
    '''
    Inverts a PDF and saves it elsewhere.

    Parameters:
    in_file: The file to invert.
    out_file: The destination of the inverted copy.
    '''
    # Setup
    blend_dict = pikepdf.Dictionary(
        Type=Name('/ExtGState'), BM=Name('/Exclusion'), ca=1, CA=1)
    non_blend_dict = pikepdf.Dictionary(Type=Name('/ExtGState'), ca=1, CA=1)
    xobj_dict = pikepdf.Dictionary({'/Type': Name('/XObject'), '/SubType': Name(
        '/Form'), '/Group': {'/S': Name('/Transparency'), '/CS': Name('/DeviceRGB')}})

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
        for i in reversed(range(num_pages)):

            page = Page(pdf.pages[i])
            if inv_ratio > 0.0:
                # Add Dictionaries to Page
                name = page.add_resource(blend_dict, Name('/ExtGState'))
                name2 = page.add_resource(non_blend_dict, Name('/ExtGState'))
                # Create rectangles
                front_rect = pdf.make_stream(bytes(
                    'q \n{0:.2} {0:.2} {0:.2} rg\n{1} gs\n{2} {3} {4} {5} re\n f\n Q'.format(inv_ratio, name, *boxes[i]), 'utf8'), xobj_dict)
                back_rect = pdf.make_stream(bytes(
                    'q \n1.0 1.0 1.0 rg\n{} gs\n{} {} {} {} re\n f\n Q'.format(name2, *boxes[i]), 'utf8'))
                # Add Rectangles to page
                page.contents_add(back_rect, prepend=True)
                page.contents_add(front_rect)

            if scribble_page_density <= 0:
                continue

            for _ in range(scribble_page_density):
                scribble_page = pikepdf.Page(
                    pikepdf.Dictionary(Type=Name.Page))
                scribble_page.mediabox = page.mediabox
                scribble_page.artbox = page.artbox
                scribble_page.cropbox = page.cropbox
                scribble_page.bleedbox = page.bleedbox
                scribble_page.trimbox = page.trimbox
                pdf.pages.insert(i+1, scribble_page)
                if inv_ratio > 0.0:
                    name = scribble_page.add_resource(
                        blend_dict, Name('/ExtGState'))
                    name2 = scribble_page.add_resource(
                        non_blend_dict, Name('/ExtGState'))
                    # Create rectangles
                    front_rect = pdf.make_stream(bytes(
                        'q \n{0:.2} {0:.2} {0:.2} rg\n{1} gs\n{2} {3} {4} {5} re\n f\n Q'.format(inv_ratio, name, *boxes[i]), 'utf8'), xobj_dict)
                    back_rect = pdf.make_stream(bytes(
                        'q \n1.0 1.0 1.0 rg\n{} gs\n{} {} {} {} re\n f\n Q'.format(name2, *boxes[i]), 'utf8'))
                    scribble_page.contents_add(back_rect, prepend=True)
                    scribble_page.contents_add(front_rect)

        pdf.save(out_file)


def invert_files_to_folder(files, folder, inv_ratio: float = 1.0, scribble_page_density: int = 0):
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
            invertPDF(str(ifile), str(inverted_pdf_file),
                      inv_ratio, scribble_page_density)
            print('Success: {}'.format(ifile.name))
        except Exception as e:
            print('Failed: {}'.format(ifile.name))
            print(e)


if __name__ == '__main__':
    import argparse
    cli = argparse.ArgumentParser(
        prog='InvertPDF',
        description='Invert the color of PDFs at a file level.'
    )

    cli.add_argument(
        'in_paths',
        nargs='*',
        help=(
            'Input files or folders to convert for. If no paths are specified, defaults'
            ' to the current working directory.'
        ),
        type=Path,
        default=[Path.cwd()]
    )

    cli.add_argument(
        '--global-out-path',
        help=(
            'Output path to place the inverted PDFs in. If not present, all'
            ' inverted PDFs will be stored in the same location as their respective original'
            ' file with and appended with `_inverted`.'),
        type=Path
    )

    cli.add_argument(
        '--local-out-path',
        help='Use a dedicated relative inverted path when `global-out-path` is not specified.',
        type=Path
    )

    cli.add_argument(
        '--inv-ratio',
        help=(
            'Inversion ratio between 0 and 1. 0 corresponds no inversion and 1 corresponds to a true color inversion.'
            ' By default this is 0.9 to produce inversions that are easier on the eyes.'
        ),
        type=float,
        default=0.9
    )

    cli.add_argument(
        '--scribble-page-density',
        help=(
            'Add N empty pages after every page in the original PDF.'
            ' Useful when using the PDF with software that allows writing on the PDF.'
        ),
        type=int,
        default=0
    )

    cli_args = cli.parse_args()

    gop: Path = cli_args.global_out_path
    lop: Path = cli_args.local_out_path
    if lop and lop.is_absolute():
        print(f'Error: Local output path: {lop} is not a relative directory')
        exit(1)

    inv_ratio = max(min(cli_args.inv_ratio, 1.0), 0.0)

    for path in cli_args.in_paths:
        if path.is_dir():
            files_to_invert = path.glob('*.pdf')
            out_path = path

        elif path.is_file():
            files_to_invert = [path]
            out_path = path.parent
        else:
            print(f'Warning: {path} is not a directory or a file, skipping')

        if gop:
            out_path = gop
        elif lop:
            out_path = out_path.joinpath(lop)

        invert_files_to_folder(files_to_invert, out_path,
                               inv_ratio, cli_args.scribble_page_density)
