.. _contributing:

Contributing
============

More to come here, soon.  See also, :ref:`todo`. 

`Pull requests welcome!`_ 

.. _Pull requests welcome!: https://github.com/lmorchard/django-teamwork/pulls

Hacking notes
-------------

* Setting up a virtualenv::

    virtualenv ./test-venv
    . ./test-venv/bin/activate
    pip install -r requirements-test.txt

* Running tests::

    ./teamwork_example/manage.py test teamwork

* To continually check pep8, tests, and coverage while working on OS X::

    gem install kicker
    kicker -c -e ./run-tests.sh teamwork teamwork_example

* Running the example site::

    ./teamwork_example/manage.py syncdb --noinput; ./teamwork_example/manage.py runserver

* To regenerate ``initial_data.json`` from example site::

    ./teamwork_example/manage.py dumpdata -n --indent=4 sites auth.user teamwork wiki > teamwork_example/fixtures/initial_data.json
