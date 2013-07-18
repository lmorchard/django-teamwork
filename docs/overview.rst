Overview
========

What is django-teamwork?
------------------------

django-teamwork is a Django app that offers an authorization backend with
support for per-object permissions based on combinations of Teams, Roles, and
Policies.

This app was born out of `Kuma`_, the Django-based wiki / CMS that powers the
`Mozilla Developer Network`_. MDN hosts a large body of documentation, with
pages arranged into a tree of sections and sub-sections. These site sections
are each managed by different teams and people, whom in turn have their own
requirements for controlling access to read and alter content.

.. _`Kuma`: https://github.com/mozilla/kuma
.. _`Mozilla Developer Network`: https://developer.mozilla.org

So, django-teamwork was created to provide per-object and per-section
flexibility for controlling permissions granted by content objects. Here are
some highlights:

* Teams can be given ownership of content Objects

* Teams offer Roles that, when assigned to Users, grant selected Privileges
  for team-owned content objects

* Independent of Teams and Roles, Policies can be set on content objects that
  grant Permissions based on criteria such as:

  - whether a User is anonymous or authenticated;
  
  - whether the User owns the object;
  
  - or by matching specific Users and Groups.

* Policies can be set on a Site objects to apply site-wide
  
* Policies can be specified in ``settings.py`` to establish a base set of
  Permissions for the entire installation.

* Content objects can optionally filter the set of Permissions granted by
  Teams, Roles, and Policies to add or remove Permissions based on custom
  model logic.

* Content objects with a hierarchical tree structure can optionally offer a
  list of parents. This is used to implement inheritance for Team ownership and
  Policy application, so that Permissions cascade down the content tree.

.. vim:set tw=78 ai fo+=n fo-=l ft=rst:
