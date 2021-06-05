import pikepdf
from PyPDF2 import PdfFileReader
from pikepdf import Page, Name
from pathlib import Path
import pathlib
import sys


def invertPDF(in_file, out_file):
    #Setup
    boxstr = 'q \n1.0 1.0 1.0 rg\n{} gs\n{} {} {} {} re\n f\n Q'
    blend_dict = pikepdf.Dictionary(Type=Name('/ExtGState'), BM=Name('/Difference'), ca=1, CA=1, op='true', OP='true')
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

if __name__ == '__main__':
    #Convert all pdfs in directory
    if len(sys.argv) == 1:
        path = Path(__file__).resolve().parent
    #Convert specfic pdf or pdfs in specific directory
    else:
        path = Path(sys.argv[1]).resolve()        
    
    if path.is_dir():
        inverted_folder = path / "invertedPDFs"
        inverted_folder.mkdir(exist_ok=True)
        for pdf_file in path.glob('*.pdf'):
            
            inverted_pdf_file = inverted_folder / pdf_file.name
            try:
                invertPDF(str(pdf_file), str(inverted_pdf_file))
                print(pdf_file.name + " succesfully converted.")
            except:
                print(pdf_file.name + " failed to convert.")
            
    elif path.is_file():
        inverted_folder = path.parent / "invertedPDFs"
        inverted_folder.mkdir(exist_ok=True)
        try:
            inverted_pdf_file = inverted_folder / path.name
            invertPDF(str(path), str(inverted_pdf_file))
            print(path.name + " succesfully converted.")
        except:
            print(path.name + " failed to convert.")