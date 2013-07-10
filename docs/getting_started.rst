.. _getting-started:

Getting Started
===============

Installation
------------

First, get the package itself installed. You may find it handy to try this::

    pip install -e 'git://github.com/lmorchard/django-teamwork.git#egg=django-teamwork`

This may or may not work, depending on whether I've yet done my job in
building a sensible ``setup.py``. 

(`Pull requests welcome!`_ See also: :ref:`contributing`)

Configuration
-------------

Add ``teamwork`` to your ``INSTALLED_APPS`` list in ``settings.py``::

    INSTALLED_APPS = (
        # ...
        'django.contrib.auth',
        'teamwork',
        # ...
    )

Add ``teamwork.backends.TeamworkBackend`` to ``AUTHENTICATION_BACKENDS`` in
``settings.py``::

    AUTHENTICATION_BACKENDS = (
        # ...
        'django.contrib.auth.backends.ModelBackend',
        'teamwork.backends.TeamworkBackend',
        # ...
    )

Finally, create all the models::

    $ ./manage.py syncdb
    $ ./manage.py migrate teamwork

Of course, your mileage may vary, if you're not using `South`_ to manage your
model changes.

.. LINKS

.. _Pull requests welcome!: https://github.com/lmorchard/django-teamwork/pulls
.. _South: http://south.aeracode.org/

.. vim:set tw=78 ai fo+=n fo-=l ft=rst:
