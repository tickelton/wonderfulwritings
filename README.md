TWOT
====

twot is going to be a twitter/blogging bot, that posts recommendations for
books that are in the public domain.

What does it do ?
-----------------

First a random english language book is selected from the Project
Gutenberg archive. Then the rating for that book is retrieved from amazon.com.
If a rating is available and it is better than a configured threshold, the
product description is also retrieved.
The book's title and description are then processed into a form suitable
for publishing in a blog including a link to the corresponding Gutenberg Page
and an amazon affiliate link to directly buy the book.
Finally the resulting article is published on a blog and tweet pointing to
the blog post is created.

How do you use it ?
-------------------

* create related accounts (twitter, amazon, github for blog)
* get api keys
* configure accounts and keys in twot.ini
* run twot via commandline or cron job
