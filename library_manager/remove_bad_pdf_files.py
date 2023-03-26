import os
import time
from PyPDF2 import PdfReader


def isFullPdf(f):
    end_content = ''
    start_content = ''
    size = os.path.getsize(f)
    if size < 1024: return False
    with open(f, 'rb') as fin:
        fin.seek(0, 0)
        start_content = fin.read(1024)
        start_content = start_content.decode("ascii", 'ignore')
        fin.seek(-1024, 2)
        end_content = fin.read()
        end_content = end_content.decode("ascii", 'ignore')
    start_flag = False
    if start_content.count('%PDF') > 0:
        start_flag = True
    if end_content.count('%%EOF') and start_flag > 0:
        return True
    eof = bytes([0])
    eof = eof.decode("ascii")
    if end_content.endswith(eof) and start_flag:
        return True
    return False


def remove_bad_pdf(path):
    bad = []
    for d, s, fl in os.walk(path):
        for f in fl:
            if f.endswith('.pdf'):
                fp = os.path.join(d, f)
                try:
                    if isFullPdf(f=fp) is False:
                        print(f'[BAD] {fp}')
                        bad.append(fp)
                        os.remove(fp)
                except Exception as e:
                    print(f'[BAD] {fp}')
                    bad.append(fp)
    print(f'BAD: {len(bad)}')


def show_bad_pdf(path):
    bad = []
    for d, s, fl in os.walk(path):
        for f in fl:
            if f.endswith('.pdf'):
                fp = os.path.join(d, f)
                try:
                    if isFullPdf(f=fp) is False:
                        print(f'[BAD] {fp}')
                        bad.append(fp)
                except Exception as e:
                    print(f'[BAD] {fp}')
                    bad.append(fp)
    print(f'BAD: {len(bad)}')
