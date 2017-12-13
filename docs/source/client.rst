Using the client
================

The client lets you interact with your crosswalk database much like you would any standard library.


Install
-------

The client is maintained as a separate package, which you can install via pip.

::

  $ pip install django-crosswalk-client

Client
------


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
      domain='states', # default is None
      create_threshold=90 # default is 80
  )

In order to query, create or edit entities, you must set a domain for your client to work on. You can set it anytime like this:

.. code-block:: python

  client.set_domain('states')


Domain
------

Create a domain
'''''''''''''''

.. code-block:: python

    domain = client.create_domain('states')

    domain.name
    # states

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


Entity
------

Create entities in bulk
'''''''''''''''''''''''

Create a list of shallow dictionaries for each object you'd like to create. This method uses Django's :code:`bulk_create` method.

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


Find the entity that best matches a fuzzy query
'''''''''''''''''''''''''''''''''''''''''''''''

Set the domain if not already set, then provide a simple dictionary with the attribute you'd like to query with a fuzzy string.

.. code-block:: python

    client.set_domain('states')
    entity = client.best_match({"name": "Kalifornia"})

    # or, shorter...
    entity = client.best_match({"name": "Kalifornia"}, domain="states")

    entity.name
    # California

Restricting a fuzzy query to a block
''''''''''''''''''''''''''''''''''''

Pass a dictionary of block attributes to reduce the number of entities *before* querying with a fuzzy string.

.. code-block:: python

    # Only entities that exactly match the postal_code attribute will be queried
    # by fuzzy match.
    entity = client.best_match(
      {"name": "Arkansas"},
      block_attrs={"postal_code": "KS"}
    )

    entity.name
    # Kansas


Find a match or create a new entity
'''''''''''''''''''''''''''''''''''

You can create a new entity if one isn't found above a match threshold.

.. code-block:: python

  entity = client.best_match_or_create(
      {"name": "Narnia"},
      create_threshold=80,
  )

  entity.created
  # True

.. note::

  If the best match for your query is an alias of or is superseded by another entity, this method will return the entity it is an alias for or that supercedes it with property :code:`aliased` or :code:`superseding` set to :code:`True`.


You can supply match attributes to restrict matches to a subset.

.. code-block:: python

    entity = client.best_match_or_create(
        {"name": "Narnia"},
        block_attrs={"postal_code": "NA"},
        create_threshold=80,
    )


You can also supply a dictionary of attributes with which to create an entity if a match is not found.

.. code-block:: python

    import uuid

    id = uuid.uuid4().hex

    entity = client.best_match_or_create(
        {"name": "Xanadu"},
        create_attrs={"uuid": id},
        create_threshold=75,
    )

    entity.uuid == id
    # True

Delete a matched entity
'''''''''''''''''''''''

.. code-block:: python

    client.delete_match({"name": "Xanadu"})

    client.delete_match({"name": "Narnia", "postal_code": "NA"})

.. warning::

    If your match attributes return more than one entity to be deleted, an :code:`UnspecificDeleteRequestError` will be raised. No entities will be deleted.
