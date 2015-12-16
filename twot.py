#!/usr/bin/env python

import getopt
import os
import sys
import sqlite3
import xml.etree.ElementTree as ET

GUTENBERG_BASE_USL = 'http://www.gutenberg.org/ebooks/'
ERR_TRACE = 3
ERR_DEBUG = 2
ERR_WARNING = 1
ERR_ERROR = 0
twot_cmds = ('populate',)
opt = {}


def DEBUG(level, dbg_str):
    if opt['verbose'] >= level:
        print dbg_str


def usage():
    print "Usage:\n"


def version():
    print "Version:\n"


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


def populate():
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

        DEBUG(ERR_TRACE, "bookid=\"{}\"".format(bookid))

        rdf_file = file_from_id(bookid)
        DEBUG(ERR_TRACE, rdf_file)
        if os.access(rdf_file, os.F_OK):
            tree = ET.parse(rdf_file)
            root = tree.getroot()
            bookdata = get_bookdata_from_xml(root)
            url = GUTENBERG_BASE_USL + '{}'.format(bookid)

            DEBUG(ERR_TRACE,  "title=\"{}\"\n author=\"{}\" url=\"{}\"".format(
                bookdata['title'].encode('ascii', 'ignore'),
                bookdata['author'].encode('ascii', 'ignore'),
                url
                )
            )

            c.execute(
                """
INSERT INTO "twot_data" (gtb_id, title, author, url_gtb) VALUES (
  ?,?,?,?
)
""", (bookid, bookdata['title'], bookdata['author'], url)
            )

            DEBUG(ERR_TRACE, "url=\"{}\"".format(url))
        else:
            DEBUG(ERR_TRACE, "{} no such file or directory.".format(rdf_file))
            pass

        conn.commit()

        bookid += 1

    conn.close()

    return ret


def parse_args(argv):
    try:
        opts, args = getopt.getopt(
            argv[1:], "hv", ["help", "version"]
        )
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(1)

    conf = {
        'verbose': 0,
        'cmd': '',
    }

    for opt, arg in opts:
        if opt == '-v':
            conf['verbose'] += 1
        elif opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt == "--version":
            version()
            sys.exit(0)

    if len(args) != 1:
        usage()
        sys.exit(1)

    if not args[0] in twot_cmds:
        usage()
        sys.exit(1)
    else:
        conf['cmd'] = args[0]

    return conf


def main(argv):
    global opt
    ret = 0

    opt = parse_args(argv)

    if opt['cmd'] == 'populate':
        populate()

    sys.exit(ret)

if __name__ == '__main__':
    main(sys.argv)
