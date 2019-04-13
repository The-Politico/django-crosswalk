Using the client
================

The django-crosswalk client lets you interact with your crosswalk database much like you would any standard library, albeit through an API.

Generally, we **do not** recommend interacting with django-crosswalk's API directly. Instead, use the methods built into the client, which have more verbose validation and error messages and are well tested.

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
  token = "<TOKEN>"

  # Address of django-crosswalk's API
  service = "https://mysite.com/crosswalk/api/"

  client = Client(token, service)

You can also instantiate a client with defaults.

.. code-block:: python

  client = Client(
      token,
      service,
      domain=None, # default
      scorer="fuzzywuzzy.default_process", # default
      threshold=80, # default
  )


Set the default domain
''''''''''''''''''''''

In order to query, create or edit entities, you must specify a domain. You can set a default anytime:

.. code-block:: python

  # Using domain instance
  client.set_domain(states)

  # ... or a domain's slug
  client.set_domain("states")


Set the default scorer
''''''''''''''''''''''

The string module path to a scorer function in :code:`crosswalk.scorers`.

.. code-block:: python

  client.set_scorer("fuzzywuzzy.token_sort_ratio_process")


Set the default threshold
'''''''''''''''''''''''''

The default threshold is used when creating entities based on a match score. For all scorers, the match score should be an integer between 0 - 100.

.. code-block:: python

  client.set_threshold(90)

-------------------------------

Client domain methods
---------------------


Create a domain
'''''''''''''''

.. code-block:: python

    states = client.create_domain("U.S. states")

    states.name == "U.S. states"
    states.slug == "u-s-states" # Name of domain is always slugified!

    # Create with a parent domain instance
    client.create_domain("counties", parent=states)

    # ... or a parent domain's slug
    client.create_domain("cities", parent="u-s-states")


Get a domain
''''''''''''

.. code-block:: python

    # Use a domain's slug
    states = client.get_domain("u-s-states")

    states.name == "U.S. states"


Get all domains
'''''''''''''''

.. code-block:: python

    states = client.get_domains()[0]

    states.slug == "u-s-states"

    # Filter domains by a parent domain instance
    client.get_domains(parent=states)

    # ... or parent domain's slug
    client.get_domains(parent="u-s-states")


Update a domain
'''''''''''''''

.. code-block:: python

    # Using the domain's slug
    states = client.update_domain("u-s-states", {"parent": "countries"})

    # ... or the domain instance
    client.update_domain(states, {"parent": "country"})


Delete a domain
'''''''''''''''

.. code-block:: python

    # Using domain's slug
    client.delete_domain('u-s-states')

    # ... or the domain instance
    client.delete_domain(states)


-------------------------------

Client entity methods
---------------------


Create entities
'''''''''''''''

Create a single entity as a shallow dictionary.

.. code-block:: python

    entities = client.create({"name": "Kansas", "postal_code": "KS"}, domain=states)


Create a list of shallow dictionaries for each entity you'd like to create. This method uses Django's :code:`bulk_create` method.

.. code-block:: python

    import us

    state_entities = [
        {
            "name": state.name,
            "fips": state.fips,
            "postal_code": state.abbr,
        } for state in us.states.STATES
    ]

    entities = client.bulk_create(state_entities, domain=states)

.. note::

  Django-crosswalk will create UUIDs for any new entities, which are automatically serialized and deserialized by the client.

  You can also create entities with your own UUIDs. For example:

  .. code-block:: python

    from uuid import uuid4()

    uuid = uuid4()

    entities = [
        {
          "uuid": uuid,
          "name": "some entity",
        }
    ]

    entity = client.bulk_create(entities)[0]

    entity.uuid == uuid
    # True

.. warning::

    You can't re-run a bulk create. If your script needs the equivalent of :code:`get_or_create` or :code:`update_or_create`, use the :code:`match` or :code:`match_or_create` methods and then update if needed it using the built-in entity :code:`update` method.

Get entities in a domain
''''''''''''''''''''''''

.. code-block:: python

    entities = client.get_entities(domain=states)

    entities[0].name
    # Alabama

Pass a dictionary of block attributes to filter entities in the domain.

.. code-block:: python

    entities = client.get_entities(
      domain=states,
      block_attrs={"postal_code": "KS"}
    )

    entities[0].name
    # Kansas


Find an entity
''''''''''''''

Pass a query dictionary to find an entity that *exactly* matches.

.. code-block:: python

    client.match({"name": "Missouri"}, domain=states)

    # Pass block attributes to filter possible matches
    client.match(
      {"name": "Texas"},
      block_attrs={"postal_code": "TX"},
      domain=states
    )

You can also fuzzy match on your query dictionary and return the entity that *best* matches.

.. code-block:: python

    entity = client.best_match({"name": "Kalifornia"}, domain=states)

    # Pass block attributes to filter possible matches
    entity = client.best_match(
      {"name": "Kalifornia"},
      block_attrs={"postal_code": "CA"},
      domain=states
    )

    entity.name == "California"


.. note::

  If the match for your query is an alias of another entity, this method will return the canonical entity with :code:`entity.aliased = True`. To ignore aliased entities, set :code:`return_canonical=False` and the method will return the best match for your query, regardless of whether it is an alias for another entity.

  .. code-block:: python

    client.best_match(
      {"name": "Misouri"},
      return_canonical=False
    )


Find a match or create a new entity
'''''''''''''''''''''''''''''''''''

You can create a new entity if an *exact* match isn't found.

.. code-block:: python

  entity = client.match_or_create({"name": "Narnia"})


  entity.created
  # True


Or use a fuzzy matcher to find the *best* match. If one isn't found above a match threshold returned by your scorer, create a new entity.

.. code-block:: python

  entity = client.best_match_or_create({"name": "Narnia"})

  entity.created
  # True

  # Set a custom threshold for the match scorer instead of using the default
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

    entity = client.match_or_create(
        {"name": "Narnia"},
        block_attrs={"postal_code": "NA"},
    )

    entity = client.best_match_or_create(
        {"name": "Narnia"},
        block_attrs={"postal_code": "NA"},
    )


If a sufficient match is not found, you can pass a dictionary of attributes to create your entity with. These will be combined with your query when creating a new entity.

.. code-block:: python

    import uuid

    id = uuid.uuid4()

    entity = client.match_or_create(
        {"name": "Xanadu"},
        create_attrs={"uuid": id},
    )

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

Create an alias if an entity above a certain match score threshold is found or create a new entity. Method returns the aliased entity.

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


Get an entity by ID
'''''''''''''''''''

Use the entity's UUID to retrieve it.

.. code-block:: python

  entity = client.get_entity(uuid)


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
        domain=states
    )

    entity.capital
    # Jefferson City

    entity = client.update_match(
        {"name": "Texas", "postal_code": "TX"},
        update_attrs={"capital": "Austin"},
        domain=states
    )

    entity.capital
    # Jefferson City

.. note::

    If your block attributes return more than one matched entity to be updated, an :code:`UnspecificQueryError` will be raised and no entities will be updated.



Delete an entity by ID
''''''''''''''''''''''

.. code-block:: python

    entity = client.match({"name": "New York"})
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

    If your block attributes return more than one matched entity to be deleted, an :code:`UnspecificQueryError` will be raised and no entities will be deleted.

----------------------------

Domain object methods
---------------------

Update a domain
'''''''''''''''

.. code-block:: python

    domain = client.get_domain('u-s-states')

    domain.update({"parent": "countries"})

Set a parent domain
'''''''''''''''''''

.. code-block:: python

    parent_domain = client.get_domain('countries')
    domain = client.get_domain('u-s-states')

    domain.set_parent(parent_domain)

Remove a parent domain
''''''''''''''''''''''

.. code-block:: python

    domain = client.get_domain('u-s-states')

    domain.remove_parent()

    domain.parent
    # None


Delete a domain
'''''''''''''''

.. code-block:: python

    domain = client.get_domain('u-s-states')

    domain.delete()

    domain.deleted
    # True


Get domain's entities
'''''''''''''''''''''

.. code-block:: python

    domain = client.get_domain('u-s-states')

    # Get all states
    domain.get_entities()

    # Filter entities using block attributes
    entities = domain.get_entities({"postal_code": "KS"})
    entities[0].name == "Kansas"


----------------------------

Entity object methods
---------------------

Access an entity's attributes
'''''''''''''''''''''''''''''

.. code-block:: python

    entity = client.match({"name": "Texas"})

    # See what user-defined attributes are set
    entity.attrs() == ["fips", "name", "postal_code", "uuid"]

    # Access a specific attribute
    entity.attrs("postal_code") == "TX"
    entity.postal_code == "TX"

    # Raise AttributeError if undefined
    entity.attrs("undefined_attr")
    entity.undefined_attr


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
