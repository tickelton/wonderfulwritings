#!/usr/bin/env python

# http://www.amazon.com/gp/customer-reviews/widgets/average-customer-review/popover/ref=dpx_acr_pop_?contextId=dpx&asin=B000P0ZSHK

from amazonproduct import API
api = API(locale='us')

results = api.item_search(
    'Books',
    Title='More Hunting Wasps',
    Condition='New',
    Availability='Available',h
    IncludeReviewsSummary='Yes')

for item in results:
    print '%s (%s)' % (item.ItemAttributes.Title, item.ASIN)