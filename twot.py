#!/usr/bin/env python

import getopt
import os
import sys
import sqlite3
import xml.etree.ElementTree as ET
import re
import httplib
import wikipedia
import amazonproduct


GUTENBERG_BASE_USL = 'http://www.gutenberg.org/ebooks/'
STARS_URL = '/gp/customer-reviews/widgets/average-customer-review/popover/ref=dpx_acr_pop_?contextId=dpx&asin={}'
ERR_TRACE = 3
ERR_DEBUG = 2
ERR_WARNING = 1
ERR_ERROR = 0
twot_cmds = (
    'populate',
    'wikipedia',
    'asin',
    'stars',
)
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


def get_wkp():
    conn = sqlite3.connect('/media/ramdisk/example.db')
    c = conn.cursor()

    c.execute('SELECT id FROM twot_data')
    ids =  c.fetchall()
    for key_id in ids:
        c.execute('SELECT id, gtb_id, title FROM twot_data WHERE id= ?',
                  (key_id[0],))
        row = c.fetchone()
        DEBUG(ERR_TRACE, "get_wkp: {}".format(
                row[2].encode('ascii', 'ignore')))

        try:
            search_res = wikipedia.search(row[2].encode('ascii', 'ignore'))
        except wikipedia.exceptions.WikipediaException:
            continue
        if search_res:
            try:
                page = wikipedia.page(search_res[0])
            except wikipedia.exceptions.DisambiguationError:
                continue
            except wikipedia.exceptions.PageError:
                continue

            summary = page.summary.encode('ascii', 'ignore')
            url = page.url
            DEBUG(ERR_TRACE,"get_wkp: summary={}, rul={}".format(
                    summary, url))
            c.execute("""
UPDATE twot_data
  SET summary = ? , url_wkp = ?
  WHERE id = ?
""", (summary, url, row[0])
            )
            conn.commit()

    conn.commit()
    conn.close()


def get_asin():
    azn_api = amazonproduct.API(locale='us')

    conn = sqlite3.connect('/media/ramdisk/example.db')
    c = conn.cursor()

    c.execute('SELECT id FROM twot_data')
    ids =  c.fetchall()
    for key_id in ids:
        c.execute('SELECT id, title FROM twot_data WHERE id= ?',
                  (key_id[0],))
        row = c.fetchone()
        DEBUG(ERR_TRACE, "get_azn: {}".format(
                row[1].encode('ascii', 'ignore')))

        try:
            results = azn_api.item_search(
                'Books',
                Title=row[1].encode('ascii', 'ignore'),
                Condition='New',
                Availability='Available',
                IncludeReviewsSummary='Yes')
        except amazonproduct.errors.NoExactMatchesFound:
            continue
        except amazonproduct.errors.AWSError:
            continue

        for item in results:
            if item.ASIN:
                # DEBUG(ERR_TRACE, "found ASIN={} for title'{}'".format(
                #     item.ASIN, item.ItemAttributes.Title))
                c.execute("""
UPDATE twot_data
  SET asin = ?, url_azn = ?
  WHERE id = ?
""", (str(item.ASIN), str(item.DetailPageURL), row[0])
                )
                conn.commit()
                break

    conn.commit()
    conn.close()


def get_stars():
    conn = sqlite3.connect('/media/ramdisk/example.db')
    c = conn.cursor()

    c.execute('SELECT id FROM twot_data')
    ids =  c.fetchall()
    for key_id in ids:
        if key_id[0] < 3:
            continue
        print key_id[0]
        c.execute('SELECT id, asin FROM twot_data WHERE id= ?',
              (key_id[0],))
        row = c.fetchone()
        if row[1] == '-':
            continue
        DEBUG(ERR_TRACE, "get_stars: {}".format(row[1]))

        http_conn = httplib.HTTPSConnection("www.amazon.com")
        http_conn.request("GET", STARS_URL.format(row[1]))
        r1 = http_conn.getresponse()
        if r1.status == 200:
            data = r1.read()
            result = re.search(r'(\d\.?\d{0,1}) out of 5 stars', data)
            stars_avg = float(result.group(1))
            result = re.search(r'See all (\d+) reviews', data)
            if not result:
                if re.search(r'See both reviews', data):
                    total_reviews = 2
            else:
                total_reviews = int(result.group(1))
            result = re.search(r'5 stars represent (\d{1,3})% of rating', data)
            if result:
                pct_5 = int(result.group(1))
            else:
                pct_5 = 0
            result = re.search(r'4 stars represent (\d{1,3})% of rating', data)
            if result:
                pct_4 = int(result.group(1))
            else:
                pct_4 = 0
            result = re.search(r'3 stars represent (\d{1,3})% of rating', data)
            if result:
                pct_3 = int(result.group(1))
            else:
                pct_3 = 0
            result = re.search(r'2 stars represent (\d{1,3})% of rating', data)
            if result:
                pct_2 = int(result.group(1))
            else:
                pct_2 = 0
            result = re.search(r'1 stars represent (\d{1,3})% of rating', data)
            if result:
                pct_1 = int(result.group(1))
            else:
                pct_1 = 0

            c.execute("""
UPDATE twot_data
  SET rating = ?, count_1 = ?, count_2 = ?, count_3 = ?,
      count_4 = ?, count_5 = ?, count_all = ?
  WHERE id = ?
""", (stars_avg, pct_1, pct_2, pct_3, pct_4, pct_5, total_reviews, row[0])
            )
            conn.commit()

    conn.commit()
    conn.close()

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
    elif opt['cmd'] == 'wikipedia':
        get_wkp()
    elif opt['cmd'] == 'asin':
        get_asin()
    elif opt['cmd'] == 'stars':
        get_stars()

    sys.exit(ret)

if __name__ == '__main__':
    main(sys.argv)
