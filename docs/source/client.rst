Using the client
================

The django-crosswalk client lets you interact with your crosswalk database much like you would any standard library, albeit through an API.

Generally, we recommend you **don't** interact with django-crosswalk's API directly, but use the methods built into the client, which have more verbose validation and error messages and are well tested.

-------------------------------

Install
-------

The client is maintained as a separate package, which you can install via pip.

::

  $ pip install django-crosswalk-client

-------------------------------

Client configuration
--------------------


Creating a client instance
''''''''''''''''''''''''''

Create a client instance by passing your API token and the URL to the root of your hosted django-crosswalk API.

.. code-block:: python

  from crosswalk_client import Client

  # Your API token, created in Django admin
  token = '<TOKEN>'
  # Address of django-crosswalk's API
  service = 'https://mysite.com/crosswalk/api/'

  client = Client(token, service)

You can also instantiate a client with defaults.

.. code-block:: python

  client = Client(
      token,
      service,
      domain=None, # default
      scorer='fuzzywuzzy.default_process', # default
      threshold=80, # default
  )


Set the default domain
''''''''''''''''''''''

In order to query, create or edit entities, you must specify a domain. You can set a default anytime using a Domain object slug:

.. code-block:: python

  client.set_domain('states')


Set the default scorer
''''''''''''''''''''''

The string module path to a scorer function in :code:`crosswalk.scorers`.

.. code-block:: python

  client.set_scorer('fuzzywuzzy.token_sort_ratio_process')


Set the default threshold
'''''''''''''''''''''''''

The default threshold is used when creating entities based on a match score. For all default scorers, the match score should be an integer between 0 - 100.

.. code-block:: python

  client.set_threshold(90)

-------------------------------

Client domain methods
---------------------


Create a domain
'''''''''''''''

.. code-block:: python

    domain = client.create_domain('states')

    domain.name
    # states


Update a domain
'''''''''''''''

.. code-block:: python

    # Use the domain's slug!
    client.update_domain('states', {"parent": "countries"})


Delete a domain
'''''''''''''''

.. code-block:: python

    client.delete_domain('states')


Get a domain
''''''''''''

.. code-block:: python

    domain = client.get_domain("states")

    domain.slug
    # states

Get all domains
'''''''''''''''

.. code-block:: python

    domains = client.get_domains()

    domains[0].slug
    # states

-------------------------------

Client entity methods
---------------------


Create some entities
''''''''''''''''''''

Create a list of shallow dictionaries for each entity you'd like to create. This method uses Django's :code:`bulk_create` method.

.. code-block:: python

    import us

    states = [
        {
            "name": state.name,
            "fips": state.fips,
            "postal_code": state.abbr,
        } for state in us.states.STATES
    ]

    entities = client.bulk_create(states, domain='states')


Get entities in a domain
''''''''''''''''''''''''

.. code-block:: python

    entities = client.get_entities(domain="states")

    entities[0].name
    # Alabama

Pass a dictionary of block attributes to filter entities in the domain.

.. code-block:: python

    entities = client.get_entities(
      domain="states",
      block_attrs={"postal_code": "KS"}
    )

    entities[0].name
    # Kansas


Find the entity that best matches a fuzzy query
'''''''''''''''''''''''''''''''''''''''''''''''

Pass a dictionary with the attribute you'd like to query with a fuzzy string.

.. code-block:: python

    entity = client.best_match({"name": "Kalifornia"}, domain="states")

    entity.name
    # California

Pass a dictionary of block attributes to filter your entities before querying with a fuzzy string.

.. code-block:: python

    entity = client.best_match(
      {"name": "Arkansas"},
      block_attrs={"postal_code": "KS"}
    )

    entity.name
    # Kansas

.. note::

  If the best match for your query is an alias of another entity, this method will return the canonical entity with :code:`entity.aliased = True`. To ignore aliased entities, set :code:`return_canonical=False` and the method will return the best match for your query, regardless of whether it is an alias for another entity.

  .. code-block:: python

    client.best_match(
      {"name": "Misouri"},
      return_canonical=False
    )


Find a match or create a new entity
'''''''''''''''''''''''''''''''''''

You can create a new entity if one isn't found above a match threshold returned by your scorer.

.. code-block:: python

  entity = client.best_match_or_create({"name": "Narnia"})

  entity.created
  # True

  # Or set a custom threshold instead of using the default
  entity = client.best_match_or_create(
      {"name": "Narnia"},
      threshold=80,
  )

.. note::

  If the best match for your query is an alias of another entity and is above your match threshold, this method will return the canonical entity with :code:`entity.aliased = True`. To ignore aliased entities, set :code:`return_canonical=False`.

  .. code-block:: python

    client.best_match_or_create(
        {"name": "Misouri"},
        return_canonical=False,
    )


Pass a dictionary of block attributes to filter match candidates.

.. code-block:: python

    entity = client.best_match_or_create(
        {"name": "Narnia"},
        block_attrs={"postal_code": "NA"},
    )


If a sufficient match is not found, you can pass a dictionary of attributes to create your entity with. These will be combined with your query when creating a new entity.

.. code-block:: python

    import uuid

    id = uuid.uuid4().hex

    entity = client.best_match_or_create(
        {"name": "Xanadu"},
        create_attrs={"uuid": id},
    )

    entity.name
    # Xanadu
    entity.uuid == id
    # True
    entity.created
    # True


Create an alias or create a new entity
''''''''''''''''''''''''''''''''''''''

Create an alias if an entity above a certain match score threshold is found or create a new entity.

.. code-block:: python

    client.set_domain('states')

    entity = client.alias_or_create({"name": "Kalifornia"}, threshold=85)

    entity.name
    # California
    entity.aliased
    # True

    entity = client.alias_or_create(
      {"name": "Alderaan"},
      create_attrs={"galaxy": "Far, far away"}
      threshold=90
    )

    entity.name
    # Alderaan
    entity.aliased
    # False

.. note::

  If the best match for your query is an alias of another entity, this method will return the canonical entity with :code:`entity.aliased = True`. To ignore aliased entities, set :code:`return_canonical=False` and the method will return the best match for your query, regardless of whether it is an alias for another entity.

  .. code-block:: python

    client.alias_or_create(
      {"name": "Missouri"},
      return_canonical=False
    )


Update an entity by ID
''''''''''''''''''''''

.. code-block:: python

    entity = client.best_match({"name": "Kansas"})
    entity = client.update_by_id(
        entity.uuid,
        {"capital": "Topeka"}
    )

    entity.capital
    # Topeka


Update a matched entity
'''''''''''''''''''''''


.. code-block:: python

    entity = client.update_match(
        {"name": "Missouri"},
        update_attrs={"capital": "Jefferson City"},
        domain="states"
    )

    entity.capital
    # Jefferson City

    entity = client.update_match(
        {"name": "Texas", "postal_code": "TX"},
        update_attrs={"capital": "Austin"},
        domain="states"
    )

    entity.capital
    # Jefferson City

.. note::

    If your block attributes return more than one matched entity to be updated, an :code:`UnspecificUpdateRequestError` will be raised and no entities will be updated.



Delete an entity by ID
''''''''''''''''''''''

.. code-block:: python

    entity = client.best_match({"name": "New York"})
    deleted = client.delete_by_id(entity.uuid)

    deleted
    # True


Delete a matched entity
'''''''''''''''''''''''

.. code-block:: python

    deleted = client.delete_match({"name": "Xanadu"})

    deleted
    # True

    deleted = client.delete_match({"name": "Narnia", "postal_code": "NA"})

    deleted
    # True

.. note::

    If your block attributes return more than one matched entity to be deleted, an :code:`UnspecificDeleteRequestError` will be raised and no entities will be deleted.

----------------------------

Domain object methods
---------------------

Update a domain
'''''''''''''''

.. code-block:: python

    domain = client.get_domain('states')

    domain.update({"parent": "countries"})

Set a parent domain
'''''''''''''''''''

.. code-block:: python

    parent_domain = client.get_domain('countries')
    domain = client.get_domain('states')

    domain.set_parent(parent_domain)

Remove a parent domain
''''''''''''''''''''''

.. code-block:: python

    domain = client.get_domain('states')

    domain.remove_parent()

    domain.parent
    # None


Delete a domain
'''''''''''''''

.. code-block:: python

    domain = client.get_domain('states')

    domain.delete()

    domain.deleted
    # True

----------------------------

Entity object methods
---------------------

Update an entity
''''''''''''''''

.. code-block:: python

    entity = client.best_match({"name": "Texas"})

    entity.update({"capitol": "Austin"})


Alias entities
''''''''''''''

.. code-block:: python

    entity = client.best_match({"name": "Missouri"})
    alias = client.best_match({"name": "Show me state"})

    alias.set_alias_for(entity)

    alias.alias_for == entity.uuid
    # True

Remove an alias
'''''''''''''''

.. code-block:: python

    alias = client.best_match({"name": "Show me state"})

    alias.remove_alias_for()

    alias.alias_for
    # None


Set a superseding entity
''''''''''''''''''''''''

.. code-block:: python

    superseded = client.best_match({"name": "George W. Bush"}, domain="politicians")
    entity = client.best_match({"name": "George W. Bush"}, domain="presidents")

    superseded.set_superseded_by(entity)

    superseded.superseded_by == entity.uuid
    # True

Remove a superseding entity
'''''''''''''''''''''''''''

.. code-block:: python

    superseded = client.best_match({"name": "George W. Bush"}, domain="politicians")

    superseded.remove_superseded_by()

    superseded.superseded_by
    # None



Delete an entity
''''''''''''''''

.. code-block:: python

    entity = client.best_match({"name": "Texas"})

    entity.delete()

    entity.deleted
    # True
