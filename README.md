![](https://www.politico.com/interactives/cdn/images/badge.svg)

# django-crosswalk

[![PyPI version](https://badge.fury.io/py/django-crosswalk.svg)](https://badge.fury.io/py/django-crosswalk)

Build and query a database of arbitrary entities. Construct a complex crosswalk between unstandardized data and the standardized records you want.

[Read the docs](http://django-crosswalk.readthedocs.io/en/latest/)!

### Why this?

This package is made by journalists. We work with a lot of unstandardized datasets, and reconciling entities between them is a daily challenge.

Some methods of deduplication within large datasets can be very complex, for which there are tools like [dedupe.io](https://github.com/dedupeio/dedupe). But much more often, our record problems are less complex and can be addressed with a few simple record linkage techniques.

Django-crosswalk is an entity service that provides a few basic, but highly extensible tools to resolve entity IDs and create linked records of known aliases.

We use it to standardize IDs across datasets, to create a master crosswalk of all known aliases and as a reference library for entity metadata, augmenting libraries like [us](https://pypi.python.org/pypi/us).


### What's in it?

The project consists of two packages.

[Django-crosswalk](https://github.com/The-Politico/django-crosswalk) is a pluggable Django application that creates tables to house your entities. It also manages tokens to authenticate users who can query and modify records through a robust API.

[Django-crosswalk-client](https://github.com/The-Politico/django-crosswalk-client) is a tiny library to make interacting with the API easy to do inline in your code.

### What can *you* do with it?

Create complex databases of entities and their aliases in django-crosswalk, then use fuzzy queries to help resolve entities' identities when working with unstandardized data.

The client library lets you easily integrate django-crosswalk's record linkage techniques in your code. Use it like a middleware between your raw data and your destination database. Scrape some entities from the web, then query your crosswalk tables and normalize your IDs before saving to your db.

Django-crosswalk will give your entities a canonical UUID you can use across databases or will persist one you've already created and return it whenever you query an alias.

Improve the precision of your queries by using the things you know about an entity. Create entities within a useful "domain" category so you don't confuse unrelated entities. Use whatever arbitrary attributes of an entity to create a custom blocking index. For example, you might use the state location and industry code to reduce the number of possible matches to a query based on a company's name.

Create records of known aliases and use that data to create a training set for higher order deduplication algorithms.
