import os
from pathlib import Path
from filecmp import cmp


def find_duplicate_files(target: Path, recursive=False) -> list:
    duplicate_files = []
    files = []
    if recursive is False:
        files = sorted(os.listdir(target))
    elif recursive is True:
        for d, s, fl in os.walk(target):
            for f in fl:
                fp = os.path.join(d, f)
                files.append(fp)
    for file_x in files:
        if_dupl = False
        for class_ in duplicate_files:
            if_dupl = cmp(
                target / file_x,
                target / class_[0],
                shallow=False
            )
            if if_dupl:
                class_.append(file_x)
                break
        if not if_dupl:
            duplicate_files.append([file_x])
    filtered_files = []
    for duplicate in duplicate_files:
        if int(len(duplicate)) >= 2:
            filtered_files.append(duplicate)
    return filtered_files

