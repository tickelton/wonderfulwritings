#/usr/bin/env python

import sys
import random
import xml.etree.ElementTree as ET

# TODO:
#   o random number 1 - 50512
#   o get title
#   o get author
#   o get gutenberg link (BASEURL + "pgterms:ebook rdf:about")

GUTENBERG_BASE_USL = 'http://www.gutenberg.org/ebooks/'

def get_random_id():
    random.seed()
    return random.randint(1, 50512)

def file_from_id(id):
    return "contrib/cache/epub/{}/pg{}.rdf".format(id, id)

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
            ret['title'] +=  title.text
        for edt in ebook.findall('marcrel:edt', ns):
            for agent in edt.findall('pgterms:agent', ns):
                for name in agent.findall('pgterms:name', ns):
                    print "foo"
                    print name.text
                    ret['author'] += name.text

    return ret

def main():
    ret = 0

    id = get_random_id()

    print "id=\"{}\"".format(id)

    file = file_from_id(id)

    tree = ET.parse(file)
    root = tree.getroot()
    bookdata = get_bookdata_from_xml(root)

    print bookdata
    #print "title=\"{}\"\n author=\"{}\"".format(bookdata['title'], bookdata{'author'})

    url = GUTENBERG_BASE_USL + '{}'.format(id)

    print "url=\"{}\"".format(url)

    sys.exit(ret)




if __name__ == '__main__':
    main()