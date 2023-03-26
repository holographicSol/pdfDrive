import os
import sys
import codecs
from pathlib import Path
import library_manager_help
import remove_bad_pdf_files
import remove_duplicates

stdin = sys.argv
print('')


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

        elif '--enumerate-library' in stdin:
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

        elif '--remove-duplicates' in stdin:
            recursive = False
            if '-R' in stdin:
                recursive = True
            print('-- enumerating: this may take a moment')
            duplicates = remove_duplicates.find_duplicate_files(target=Path(target), recursive=recursive)
            if duplicates:
                i_count = 0
                i_duplicates = 0
                filtered_duplicates = []
                for duplicate in duplicates:
                    print(f'[DUPLICATE_files] {len(duplicate)} {duplicate[0]}')
                    for sub_duplicate in duplicate:
                        i_count += 1
                        if str(sub_duplicate).strip() != str(duplicate[0]).strip():
                            print(f'    {sub_duplicate}')
                            i_duplicates += 1
                            filtered_duplicates.append(sub_duplicate)
                    i_count += 1
                    if i_count == 100:
                        i_count = 0
                        input('--- more ---')
                print('')
                print('[WARNING] This will potentially delete a lot of files! Please be sure before continuing.')
                print(f'[DUPLICATES] {len(filtered_duplicates)}')
                usr_input = input('continue (y\\n)? ')
                if usr_input == 'y' or usr_input == 'Y':
                    for duplicate in filtered_duplicates:
                        print(f'-- removing {duplicate}')
                        try:
                            os.remove(duplicate)
                        except Exception as e:
                            print(e)
            else:
                abort_op()
    else:
        print(f'[INVALID] Path: {target}')

print('')
