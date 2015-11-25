#!/usr/bin/env python

# http://www.amazon.com/gp/customer-reviews/widgets/average-customer-review/popover/ref=dpx_acr_pop_?contextId=dpx&asin=B000P0ZSHK

import re
import httplib
from amazonproduct import API

STARS_URL = '/gp/customer-reviews/widgets/average-customer-review/popover/ref=dpx_acr_pop_?contextId=dpx&asin={}'

api = API(locale='us')

results = api.item_search(
    'Books',
    Title='More Hunting Wasps',
    Condition='New',
    Availability='Available',
    IncludeReviewsSummary='Yes')

for item in results:
    if item.ASIN:
        print '%s (%s)' % (item.ItemAttributes.Title, item.ASIN)
        conn = httplib.HTTPSConnection("www.amazon.com")
        conn.request("GET", STARS_URL.format(item.ASIN))
        r1 = conn.getresponse()
        print r1.status
        data1 = r1.read()
        foo = re.search(r'(\d\.?\d{0,1}) out of 5 stars', data1)
        print "{} stars".format(foo.group(1))
        foo = re.search(r'See all (\d+) reviews', data1)
        print "{} reviews".format(foo.group(1))
        break