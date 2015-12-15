#!/usr/bin/env python

import os
import sys
import sqlite3
import xml.etree.ElementTree as ET

GUTENBERG_BASE_USL = 'http://www.gutenberg.org/ebooks/'


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
            for edt in ebook.findall('marcrel:adp', ns):
                for agent in edt.findall('pgterms:agent', ns):
                    for name in agent.findall('pgterms:name', ns):
                        ret['author'] += name.text
    if not ret['author']:
        for agent in root.findall('pgterms:agent', ns):
            for name in agent.findall('pgterms:name', ns):
                ret['author'] += name.text

    return ret


def get_gutenberg_ids():
    (_, dirnames, _) = os.walk('contrib/cache/epub/').next()
    return dirnames


def get_max_id(ids):
    maxid = 0

    for bookid in ids:
        if int(bookid) > maxid:
            maxid = int(bookid)

    return maxid


def main(argv):
    ret = 0
    bookid = 1

    gtb_ids = get_gutenberg_ids()
    max_id = get_max_id(gtb_ids)

    conn = sqlite3.connect('/media/ramdisk/example.db')

    c = conn.cursor()

    while True:
        if bookid > max_id:
            break
        if not "{}".format(bookid) in gtb_ids:
            bookid += 1
            continue

        # print "bookid=\"{}\"".format(bookid)

        rdf_file = file_from_id(bookid)
        # print rdf_file
        if os.access(rdf_file, os.F_OK):
            tree = ET.parse(rdf_file)
            root = tree.getroot()
            bookdata = get_bookdata_from_xml(root)

            # print "title=\"{}\"\n author=\"{}\"".format(
            #     bookdata['title'].encode('ascii', 'ignore'),
            #     bookdata['author'].encode('ascii', 'ignore')
            # )

            c.execute(
                """
INSERT INTO "twot_data" (gtb_id, title, author) VALUES (
  ?,?,?
)
""", (bookid, bookdata['title'], bookdata['author'])
            )

            url = GUTENBERG_BASE_USL + '{}'.format(bookid)

            # print "url=\"{}\"".format(url)
        else:
            pass
            # print "{} no such file or directory.".format(rdf_file)

        conn.commit()

        bookid += 1

    conn.close()

    sys.exit(ret)


if __name__ == '__main__':
    main(sys.argv)
