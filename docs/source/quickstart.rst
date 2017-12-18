Quickstart
==========

Prerequisites
-------------

- Python ≥ 3
- Django ≥ 2.0
- PostgreSQL ≥ 9.4

Installation
------------

1. Install django-crosswalk.

::

  $ pip install django-crosswalk

2. Add the app and DRF to :code:`INSTALLED_APPS` in your project settings.

.. code-block:: python

    # settings.py

    INSTALLED_APPS = [
      # ...
      'rest_framework',
      'crosswalk',
    ]

3. Include the app in your project's URLconf.

.. code-block:: python

    # urls.py
    urlpatterns = [
        # ...
        path('crosswalk', include('crosswalk.urls')),
    ]

4. Migrate databases.

::

  $ python manage.py migrate crosswalk

5. Open Django's admin and create your first API users.

6. Install the client.

::

  $ pip install django-crosswalk-client

7. Read through the rest of these docs to see how to interact with your database.
