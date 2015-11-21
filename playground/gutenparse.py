#!/usr/bin/env python

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
        for edt in ebook.findall('marcrel:edt', ns):
            # TODO: author's names can also be contained in other sections
            for agent in edt.findall('pgterms:agent', ns):
                for name in agent.findall('pgterms:name', ns):
                    ret['author'] += name.text

    return ret


def main():
    ret = 0

    bookid = get_random_id()

    print "bookid=\"{}\"".format(bookid)

    rdf_file = file_from_id(bookid)

    tree = ET.parse(rdf_file)
    root = tree.getroot()
    bookdata = get_bookdata_from_xml(root)

    print "title=\"{}\"\n author=\"{}\"".format(
        bookdata['title'], bookdata['author']
    )

    url = GUTENBERG_BASE_USL + '{}'.format(bookid)

    print "url=\"{}\"".format(url)

    sys.exit(ret)


if __name__ == '__main__':
    main()
