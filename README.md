# invertPDF.py
A simple python3 script for inverting the colors of PDFs, whilst keeping the pdf format and vector nature of the document.

## Usage

Basic usage:

```bash
python invertPDF.py [path1] [path2] [path3] ...
```

where every `path` is either a directory or a file. Every file and file inside a folder path will have an inverted copy created
at its location with an added `_inverted.pdf` suffix. See

```bash
python invertPDF.py -h
```

for advanced usage.
