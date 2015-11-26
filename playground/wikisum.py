#!/usr/bin/env python

import wikipedia


search_res = wikipedia.search("Fair Margaret")
if search_res:
    summary = wikipedia.summary(search_res[0])

print summary