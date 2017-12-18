Concepts
========


Domains
-------

A domain is an arbitrary category your entities belong to. For example, you may have a domain of :code:`states`, which includes entities that are U.S. states.

Every entity you create **must belong** to one domain.

Domains may be nested with a parent-child heirarchy. For example, :code:`states` may be a parent to :code:`counties`.

A domain is the highest level blocking index in django-crosswalk. These indexes help greatly increase the precision of queries. For example, restricting your query to our :code:`states` domain makes sure you won't match Texas County, Missouri when you mean to match Texas state.

-------------------------------

Entities
--------

Entities can be whatever you need them to be: people, places, organizations or even ideas. The only strict requirements in django-crosswalk are that an entity has one or more identifying string attributes and that it belong to a domain.

On creation, each entity in django-crosswalk is given a :code:`uuid` attribute that you can use to match with records in other databases. You can also create entities with your own uuids.

Entity relationships
````````````````````

Entities can be related to each other in a couple of ways. An entity may be an **alias** for another entity or may be **superseded** by another entity. We make the distinction between the two based on whether the entity referenced is in the same domain.

By convention, an entity that is related to another entity in the same domain is an **alias**. For example, :code:`George Bush, Jr.` could be an alias for :code:`George W. Bush`, both within the domain of :code:`politicians`.

On the model, :code:`George Bush, Jr.` is foreign keyed to :code:`George W. Bush`, which indicates that :code:`George W. Bush` is the canonical representation of the entity within the :code:`politicians` domain.

Let's say we also had a domain for :code:`presidents`. We could say :code:`George W. Bush` the politician is superseded by :code:`George W. Bush` the president and represent that relationship with a foreign key. This is often exactly how we model entities that belong to multiple domains.

These are conventions and are not enforced at the database level. So it's up to you to use them in a way that suits your data. Please note, however, deleting an entity will also delete all of its aliases but not delete entites it supersedes.

On the :code:`Entity` model, every object has a foreign key for both aliasing and superseding, which you can use to chain canonical references. Django-crosswalk will traverse that chain to the highest canonical alias entity when returning query results. It will not traverse superseding relationships.

-------------------------------

Attributes
----------

Entities are defined by their attributes. Django-crosswalk allows you to add any arbitrary attribute to an entity. For example, a state may have attributes like :code:`postal_code`, :code:`ap_abbreviation`, :code:`fips` and :code:`region` as well as :code:`name`.

Attributes are stored in a single JSONField on the :code:`Entity` model.

After you've created them, you can use attributes to create additional blocking indexes -- i.e., a block of entities filtered by a set of attributes -- to make your queries more precise. For example, you can query a state within a specific :code:`region`.

.. warning::

  An entity's attributes must be unique together within a domain.

  Nested attributes are not allowed. Django-crosswalk is focused solely on entity resolution and record linkage, not in being a complete resource of all information about your entities. Complex data should be kept in other databases, probably linked by the UUID.

  In general, we recommend snake-casing attribute names, though this is not enforced.

  There are some reserved attribute names. Django-crosswalk will throw a validation error if you try to use them:

  - :code:`alias_for`
  - :code:`aliased`
  - :code:`attributes`
  - :code:`created`
  - :code:`domain`
  - :code:`entity`
  - :code:`match_score`
  - :code:`superseded_by`
  - :code:`uuid`


-------------------------------

Scorers
-------

Scorers are functions that compare strings and are used when querying entities. Django-crosswalk comes with four scorers, all from the `fuzzywuzzy <https://github.com/seatgeek/fuzzywuzzy>`_ package.

All scorer functions have the same signature. They must accept a query string (:code:`query_value`) and a list of strings to compare (:code:`block_values`). They must return a tuple that contains a matched string from :code:`block_values` and a normalized match score.
