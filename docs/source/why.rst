Why this?
=========

This package is made by journalists. We work with a lot of heterogenous datasets, and reconciling entities between them is a daily challenge.

Deduplication within a large dataset of campaign finance records can be a complex problem, for which there are equivalent tools like `dedupe.io <https://github.com/dedupeio/dedupe>`_. But often, our record problems are much less complex, and you'll catch us creating small crosswalks to link entities across our data.

Django-crosswalk is aimed at replacing those small crosswalks with a central system that can be easily queried and modified within the code that uses it. It's a simple library to help you create and manage databases of arbitrary entities and their known aliases.


What's in it?
-------------

The project consists of two packages.

Django-chartwerk is a pluggable Django application that creates tables to house your entities. It also manages tokens to authenticate users who can query and modify records through a robust API.

Django-chartwerk-client is a tiny library to make interacting with the API easy to do inline in your code.



What can you do with it?
------------------------

We use a few simple record linkage techniques to help you easily model and query the entities and aliases in your database.

Save your entities with arbitrary attributes that you can make fuzzy queries against or build blocking indexes with on the fly, which help break your database apart into blocks of likely matches that improve query precision.

The app also helps you maintain records of known aliases and automatically resolve queries against them to return canonical records.

You'll also get UUIDs for each entity in your database that you can use as a primary key across your data projects.
