.. _usage:

Usage
=====

Contents under construction; this page is mainly a feature teaser.

The best sample code is currently found in:

* `the teamwork_example app`_ used in tests;

* and in `the backend tests`_ themselves.

.. _the backend tests: https://github.com/lmorchard/django-teamwork/blob/master/teamwork/tests/test_backends.py
.. _the teamwork_example app: https://github.com/lmorchard/django-teamwork/tree/master/teamwork_example

Checking permissions for a user and content object
--------------------------------------------------

@@ TODO. It goes a little something like this::

    if not request.user.has_perm('wiki.view_document', doc):
        raise PermissionDenied

Using the ``get_object_or_404_or_403`` shortcut
-----------------------------------------------

@@ TODO. It goes a little something like this::

    from teamwork.shortcuts import get_object_or_404_or_403
    # ...
    doc = get_object_or_404_or_403('wiki.add_revision', request.user,
        Document, locale=document_locale, slug=document_slug)

Base policy in ``settings.py``
------------------------------

@@ TODO. `Example <https://github.com/lmorchard/django-teamwork/blob/master/teamwork/tests/test_backends.py#L270>`_. Here's an inadequate sample::

    TEAMWORK_BASE_POLICIES = {
        'anonymous': (
            'wiki.view_document',),
        'authenticated': (
            'wiki.view_document', 'wiki.add_document', 'wiki.add_revision'),
    }


Setting a Policy on a Site
--------------------------

@@ TODO. `Example test <https://github.com/lmorchard/django-teamwork/blob/master/teamwork/tests/test_backends.py#L208>`_.

Setting a Policy on a content object
------------------------------------

@@ TODO. `Example test <https://github.com/lmorchard/django-teamwork/blob/master/teamwork/tests/test_backends.py#L65>`_.

Creating Teams and Roles
------------------------

@@ TODO. `Example test <https://github.com/lmorchard/django-teamwork/blob/master/teamwork/tests/test_backends.py#L65>`_.

Granting Team ownership of content Objects
------------------------------------------

@@ TODO. Example `model <https://github.com/lmorchard/django-teamwork/blob/master/teamwork_example/wiki/models.py#L17>`_ and `test <https://github.com/lmorchard/django-teamwork/blob/master/teamwork/tests/test_backends.py#L86>`_.

Assigning Roles to Users
------------------------

@@ TODO. `Example test <https://github.com/lmorchard/django-teamwork/blob/master/teamwork/tests/test_backends.py#L90>`_.

Filtering permissions with per-object logic
-------------------------------------------

@@ TODO. Example `model <https://github.com/lmorchard/django-teamwork/blob/master/teamwork_example/wiki/models.py#L43>`_ and `test <https://github.com/lmorchard/django-teamwork/blob/master/teamwork/tests/test_backends.py#L131>`_.

Supporting content hierarchies and Permission inheritance
---------------------------------------------------------

@@ TODO. Example `test <https://github.com/lmorchard/django-teamwork/blob/master/teamwork/tests/test_backends.py#L141>`_ and `model <https://github.com/lmorchard/django-teamwork/blob/master/teamwork_example/wiki/models.py#L51>`_.
