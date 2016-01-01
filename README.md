WonderfulWritings
=================

wonderfulwritings.py (*WW*) is a utility that helps to find interesting books
to read or blog about.

What does it do ?
-----------------

The main data source of *WW* py is the [Project Gutenberg](http://www.gutenberg.org)
database. After the books contained therein are read into a SQLite DB, *WW*
tries to get relevant summaries from [Wikipedia](http://en.wikipedia.org) and
reviews and affiliate links from [Amazon](https://www.amazon.com).
The resulting database can then be queried to find interesting books and
related data.

Project status
--------------

The original idea was to use the data described above to create blog posts
recommending interesting books that also include Amazon affiliate links and
use the revenue to further improve the project and add additional data sources.
Unfortunately the data quality of the created database is rather poor at the
moment and I am lacking the time to invest in the needed improvement.
The biggest problem right now is that the review data is poorly matched to the
actual book data. That might work much better if a source other than amazon
would be used for the review data.

How do you use it ?
-------------------

* create an Amazon Product Advertising API account
* add amazon credentials to ~/.amazon-product-api
* get the [complete project gutenberg catalog](http://www.gutenberg.org/wiki/Gutenberg:Feeds)
and extract it to a directory named `contrib` in the main project directory
* install required dependencies
* run the *WW* script:
```
# wonderfulwritings.py populate
# wonderfulwritings.py wikipedia
# wonderfulwritings.py asin
# wonderfulwritings.py stars
```
* query the resulting SQLite database for whatever you are interested in

Dependencies
------------

`apt-get install libffi-dev libssl-dev`

`pip install -r requirements.txt`
