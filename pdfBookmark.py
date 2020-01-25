#! /usr/bin/env python
# coding='utf-8'
"""
PDF文档书签制作
Author: zhiying
URL: www.zhouzying.cn
Data: 2020.01.17
Description: Build bookmarks for pdf documents  automatically with pdfBookmark.
"""
# for Ubuntu 18.04.3 LTS you can try those commands to install pymupdf on your computer.
# sudo -H pip3 install --upgrade pip
# sudo -H python3.6 -m pip install -U pymupdf
import fitz
import re
import argparse
import time


def read_file(path):
    with open(path, 'rt') as f:
        for line in f.readlines():
            # print(line.split(' '))
            # ignore blank line
            if len(line.strip()) > 0:
                # strip the space behind the page-number
                yield line.strip()
            else:
                continue


def parse_file(line):
    regex = re.compile(r'(.*?)(\s*)(\d+$)')
    try:
        result = regex.search(line)
        title = result.group(1).strip()
        page_number = int(result.group(3).strip())
        # 中文目录
        """
        目录格式
        BookmarkBegin
        BookmarkTitle: title
        BookmarkLevel: 1
        BookmarkPageNumber: 1
        """
        if '第' in line and '章' in line:
            book_mark_level = 1
        elif '附录' in line:
            book_mark_level = 1
        elif '参考文献' in line:
            book_mark_level = 1
        else:
            book_mark_level = 2
        return title, book_mark_level, page_number

    except:
        with open('./pdfBookmark_error_log.txt', 'a', encoding='utf-8') as log:
            log.write('{}: This line may be have wrong: {}'.format(time.asctime(), line))
            log.close()


# check the completeness of a pdf catalog
def check_bookmark(doc):
    toc = doc.getToC()
    i = 0
    for item in toc:
        if str(item[1]).isdigit():
            break
        else:
            i += 1

    return toc[:i]


def main():

    parser = argparse.ArgumentParser(description='Build bookmarks for pdf documents automatically.',
                                     epilog='for bugs please submit issuses at https://github.com'
                                            '/zyingzhou/pdfBookmark.', prog='pdfBookmark')

    parser.add_argument('-f', '--pdf', dest='pdf', help='the path of pdf file you want to import bookmark in')

    parser.add_argument('-c', '--catalog', dest='catalog', help='the path of the bookmark')

    parser.add_argument('-s', '--offset', dest='offset', type=int, default=0, help='pdf document page offset compared '
                                                                                   'with the bookmark your provide')

    parser.add_argument('-o', '--output', dest='output', help='specify path to save output pdf file')

    parser.add_argument('-i', '--ignore', dest='ignore', default=1, type=int, help='the value is 1 if ignore the old '
                                                                                   'catalog, otherwise 0')

    args = parser.parse_args()

    if args.pdf is not None and args.catalog is not None and args.output is not None:
        print('beginning adding bookmarks into pdf files')
        file_path = str(args.pdf)
        file_name = str(file_path).split('/')[-1].split('.')[0]
        bookmark_path = str(args.catalog)
        offset = args.offset
        output_file = str(args.output) + '/' + file_name + '_已添加目录.pdf'
        doc = fitz.open(file_path)
        catalog = []
        if args.ignore == 0:
            if len(check_bookmark(doc)) != 0:
                items = check_bookmark(doc)
                catalog += items

        for line in read_file(bookmark_path):
            title, book_mark_level, page_number = parse_file(line)
            catalog.append([book_mark_level, title, page_number + offset])
        doc.setToC(catalog)
        doc.save(output_file)
        print('Adding bookmarks successfully.')

    elif args.pdf is None:
        print('please use -f flag to specify the path of pdf file you want to import bookmark in.')

    elif args.catalog is None:
        print('please use -c flag to specify the path of the bookmark.')

    elif args.output is None:
        print('please use -o flag to specify the path to save output pdf file')

    else:
        print('please check runtime environment!')


if __name__ == "__main__":
    main()
