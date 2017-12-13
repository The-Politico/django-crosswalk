Concepts
========

Django-crosswalk is a basic library to help you create arbitrary databases of entities and their aliases.

We use a few simple record linkage techniques to help you easily model and query your entity database.

First, we introduce blocking indices, which help break your database apart into likely matches and improve your query precision. Second, we allow you to make fuzzy queries against an arbitrary attribute of an entity to find the closest matching entity in a block.

Domains
-------

Simply put, a domain is an arbitrary category your entities belong to. For example, you may have a domain of :code:`states`, which includes entities that are U.S. states.

Every entity you create **must belong** to one domain.

Domains may be nested with a parent-child heirarchy. For example, :code:`states` may be a parent to :code:`counties`.

A domain is the highest level blocking index in django-crosswalk. These indices help greatly increase the precision of queries. For example, restricting your query to our :code:`states` domain makes sure you won't match Texas County, Missouri when you mean to match Texas state.


Entities
--------

Entities can be whatever you need them to be: people, places, organizations or even ideas. The only strict requirements in django-crosswalk are that an entity has one or more identifying string attributes and that it belong to a domain.

On creation, each entity in django-crosswalk is given a :code:`uuid` attribute that you can use to match with records in other databases. You can also create entities with your own uuids.

Relationships
`````````````

Entities can be related to each other in a couple ways. An entity may be an *alias* for another entity or may be *superseded* by another entity. We make the distinction between the two based on whether the entity referenced is in the same domain.

By convention, an entity that is related to another entity in the same domain is an **alias**. For example, :code:`William Clinton` is an alias for :code:`Bill Clinton`, both within the domain of :code:`politicians`. At the database level, :code:`William Clinton` is foreign keyed to :code:`Bill Clinton` indicating that :code:`Bill Clinton` is the canonical representation of the entity within the :code:`politicians` domain.

Let's say we also had a more general domain of :code:`people`. We could say :code:`Bill Clinton` the politician is superseded by :code:`Bill Clinton` the person and represent that relationship with a foreign key. This is often exactly how we model entities that belong to multiple domains.

These are conventions and are not enforced at the database level. So it's up to you to use them in a way that suits your data. On the model, every entity has a foreign key for aliasing and superseding, which you can use to chain canonical references. Django-crosswalk will traverse that chain to the highest canonical entity when returning query results.

Attributes
----------

Django-crosswalk allows you to add arbitrary attributes to entities to help identify them uniquely. For example, a state may have attributes like :code:`postal_code`, :code:`ap_abbreviation`, :code:`fips` and :code:`region` as well as :code:`name`.

After you've created them, you can use attributes to create additional blocking indexes, i.e., a subset, to make your queries very precise. For example, you can search for a state within a specific :code:`region`.

.. warning::

  Nested attributes are not allowed in django-crosswalk. Django-crosswalk is focused solely on entity resolution and record linkage, not in being a complete resource of all information about your entities. Complex data should be kept in other databases.

  There are some reserved attribute names. Django-crosswalk will throw a validation error if you try to use them: :code:`entity`, :code:`created`, :code:`match_score`, :code:`uuid`, :code:`aliased`, :code:`superseding`.
