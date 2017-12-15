Using the client
================

The django-crosswalk client lets you interact with your crosswalk database much like you would any standard library, albeit through an API.

Generally, we recommend you **don't** interact with django-crosswalk's API directly, but use the methods built into the client. We aren't even documenting the API endpoints explicitly.

-------------------------------

Install
-------

The client is maintained as a separate package, which you can install via pip.

::

  $ pip install django-crosswalk-client

-------------------------------

Client methods
--------------


Creating a client instance
''''''''''''''''''''''''''

Create a client instance by passing your API token and the URL to the root of your hosted django-crosswalk API.

.. code-block:: python

  from crosswalk_client import Client

  # Your API token
  token = '<TOKEN>'
  # Address for root of API
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

In order to query, create or edit entities, you must include a domain. You can set a default anytime using a Domain object slug:

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

Domain methods
--------------


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


Get all domains
'''''''''''''''

.. code-block:: python

    domains = client.get_domains()

    domains[0].slug
    # states

-------------------------------

Entity methods
--------------


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

  If the best match for your query is an alias of another entity, this method will return the canonical entity with :code:`aliased = True`.


Find a match or create a new entity
'''''''''''''''''''''''''''''''''''

You can create a new entity if one isn't found above a match threshold.

.. code-block:: python

  entity = client.best_match_or_create(
      {"name": "Narnia"},
      threshold=80,
  )

  entity.created
  # True

.. note::

  If the best match for your query is an alias of another entity, this method will return the canonical entity with :code:`aliased = True`.


Pass a dictionary of block attributes to filter match candidates.

.. code-block:: python

    entity = client.best_match_or_create(
        {"name": "Narnia"},
        block_attrs={"postal_code": "NA"},
        threshold=80,
    )


You can also supply a dictionary of attributes to create an entity with if a match is not found.

.. code-block:: python

    import uuid

    id = uuid.uuid4().hex

    entity = client.best_match_or_create(
        {"name": "Xanadu"},
        create_attrs={"uuid": id},
        threshold=75,
    )

    entity.uuid == id
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

  If the best match for your query is above the treshold and is itself an alias of another entity, this method will return the canonical entity.


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
    response = client.delete_by_id(entity.uuid)

    response
    # True


Delete a matched entity
'''''''''''''''''''''''

.. code-block:: python

    response = client.delete_match({"name": "Xanadu"})

    response
    # True

    response = client.delete_match({"name": "Narnia", "postal_code": "NA"})

    response
    # True

.. note::

    If your block attributes return more than one matched entity to be deleted, an :code:`UnspecificDeleteRequestError` will be raised and no entities will be deleted.
