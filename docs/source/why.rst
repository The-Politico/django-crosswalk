Why this?
=========

This package is made by journalists. We work with a lot of heterogenous datasets, and reconciling entities between them is a daily challenge.

Some methods of deduplication within large datasets can be quite complex, for which there are tools like `dedupe.io <https://github.com/dedupeio/dedupe>`_. But often, our record problems are much less complex, and you'll catch us creating small crosswalk tables or code to identify entities across multiple datasets or to handle basic typographical differences in entity names.

Django-crosswalk is aimed at replacing those small crosswalks with a central entity service that uses a few basic entity resolution techniques. It's a simple library to help you create and manage databases of entities and their known aliases and easily use them in your code to standardize records.


What's in it?
-------------

The project consists of two packages.

`Django-crosswalk <https://github.com/The-Politico/django-crosswalk>`_ is a pluggable Django application that creates tables to house your entities. It also manages tokens to authenticate users who can query and modify records through a robust API.

`Django-crosswalk-client <https://github.com/The-Politico/django-crosswalk-client>`_ is a tiny library to make interacting with the API easy to do inline in your code.



What can you do with it?
------------------------

Create complex databases of entities and their aliases in django-crosswalk. Then use fuzzy queries to help resolve entities' identities when scraping data from the web or using other unstandardized sources.

The client library lets you easily integrate django-crosswalk's record linkage techniques in your code. Use it like a middleware between your original data and your destination database. Scrape some entities from a website, then query your crosswalk tables and normalize your IDs before saving to your db.

Django-crosswalk will give your entities a canonical ID you can use across databases or will persist your own and return it whenever you query an alias.

Improve the precision of your queries by using the things you know about an entity. Create entities within a useful domain so you don't confuse unrelated entities. Use whatever entity attributes you have to create a custom blocking index. For example, to resolve corporate entities, you might use the state location and industry code to reduce the number of possible matches to a query based on the company's name.

Create records of known aliases and use that data to create a training set for higher order deduplication algorithms.
