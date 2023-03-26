import os
import sys
import remove_bad_pdf_files
import codecs

stdin = sys.argv


def abort_op():
    print('[ABORTING]')


target = ''
if '-P' in stdin:
    idx = stdin.index('-P') + 1
    target = stdin[idx]

    if os.path.exists(target):

        if '--show-corrupted' in stdin:
            """ Display PDF files that may be incomplete """

            remove_bad_pdf_files.show_bad_pdf(target)

        elif '--remove-corrupted' in stdin:
            """ Display PDF files that may be incomplete AND delete them """

            print('[WARNING] This will potentially delete a lot of files! Any PDF that appears to be incomplete will be deleted during this operation.')
            usr_input = input('continue (y\n)? ')
            if usr_input == 'y' or usr_input == 'Y':
                remove_bad_pdf_files.remove_bad_pdf(target)
            else:
                abort_op()

        elif '--enumerate-library':
            """ Append filenames to file for memory when skipping downloads across multiple drives/systems """

            print('')
            print(f'Enumerating: This may take a moment...')
            success_downloads = []
            if not os.path.exists('./books_saved.txt'):
                open('./books_saved.txt', 'w').close()
            with codecs.open('./books_saved.txt', 'r', encoding='utf8') as fo:
                for line in fo:
                    line = line.strip()
                    if line not in success_downloads:
                        success_downloads.append(line)
            fo.close()
            new_entries = []
            for d, s, fl in os.walk(target):
                for f in fl:
                    if f not in success_downloads:
                        new_entries.append(f)
            with codecs.open('./books_saved.txt', 'a', encoding='utf8') as fo:
                for entry in new_entries:
                    fo.write(entry + '\n')
            fo.close()
            print(f'Complete.')

print('')
