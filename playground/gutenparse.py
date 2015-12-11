#!/usr/bin/env python

import os
import sys
import random
import xml.etree.ElementTree as ET


GUTENBERG_BASE_USL = 'http://www.gutenberg.org/ebooks/'


def get_random_id():
    random.seed()
    return random.randint(1, 50512)


def file_from_id(bookid):
    return "contrib/cache/epub/{}/pg{}.rdf".format(bookid, bookid)


def get_bookdata_from_xml(root):
    ret = {
        'title': '',
        'author': '',
    }
    ns = {
        'pgterms': 'http://www.gutenberg.org/2009/pgterms/',
        'dcterms': 'http://purl.org/dc/terms/',
        'marcrel': 'http://id.loc.gov/vocabulary/relators/',
    }

    for ebook in root.findall('pgterms:ebook', ns):
        for title in ebook.findall('dcterms:title', ns):
            ret['title'] += title.text
        for edt in ebook.findall('dcterms:creator', ns):
            for agent in edt.findall('pgterms:agent', ns):
                for name in agent.findall('pgterms:name', ns):
                    ret['author'] += name.text
        if not ret['author']:
            for edt in ebook.findall('marcrel:edt', ns):
                for agent in edt.findall('pgterms:agent', ns):
                    for name in agent.findall('pgterms:name', ns):
                        ret['author'] += name.text
    if not ret['author']:
        for agent in root.findall('pgterms:agent', ns):
            for name in agent.findall('pgterms:name', ns):
                ret['author'] += name.text

    return ret


def main(argv):
    ret = 0
    loop = 0
    again = 1

    if len(argv) != 2:
        bookid = get_random_id()
    elif argv[1] == 'loop':
        loop = 1
        bookid = 1
    else:
        bookid = argv[1]

    while(again):
        again -= 1

        print "bookid=\"{}\"".format(bookid)

        rdf_file = file_from_id(bookid)
        print rdf_file
        if os.access(rdf_file, os.F_OK):
            tree = ET.parse(rdf_file)
            root = tree.getroot()
            bookdata = get_bookdata_from_xml(root)

            print "title=\"{}\"\n author=\"{}\"".format(
                bookdata['title'].encode('ascii', 'ignore'),
                bookdata['author'].encode('ascii', 'ignore')
            )

            url = GUTENBERG_BASE_USL + '{}'.format(bookid)

            print "url=\"{}\"".format(url)
        else:
            print "{} no such file or directory.".format(rdf_file)

        if(loop):
            bookid += 1
            again = 1

    sys.exit(ret)


if __name__ == '__main__':
    main(sys.argv)
