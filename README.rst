django-teamwork is a Django app for managing teams that own content objects and
assign roles to users who gain delegated permissions to act upon team-owned
content objects.

TODO: Write a better description. For now, read my
`blog post <https://blog.lmorchard.com/2013/02/23/looking-for-a-django-app-to-manage-roles-within-groups>`_ 
for more background.

- `Build status on travis-ci <http://travis-ci.org/lmorchard/django-teamwork>`_ (|build-status|)
- `Latest documentation on Read The Docs <https://django-teamwork.readthedocs.org/en/latest/>`_
  (`source <https://github.com/lmorchard/django-teamwork/tree/master/docs>`_)

TODO
----

* Move all the below into GitHub Issues, once this gets to feature-complete

* API ergonomics

  - shortcut to convert from codename + content object to Permission

* Support ForeignKey for Policy directly from content objects?

* Support many-to-many for Policies and content objects?

* Popup-friendly views? 

  - to apply / adjust Policy on a content Object
  
  - to assign a user to one of your Teams

* Abstract out / make more flexible some of the integration points
    
  - optional fields & methods on content objects
      
    * team field
    
    * get_permission_parents, get_all_permissions

* Consider optimizations for mass-lookup cases, because this does nothing for
  that now.

Notes to self
-------------

* To regenerate ``initial_data.json``::

    ./teamwork_example/manage.py dumpdata -n --indent=4 sites auth.user teamwork wiki > teamwork_example/initial_data.json

Use Cases / Specs
-----------------

This is a thinking-aloud section where I try to keep track of what I'm trying
to accomplish here:

* As a creator of a content Object
  I want to create a Team
  In order to delegate Permissions granted by a content Object

* As a creator of a content Object
  I want to assign ownership of my Object to a Team
  In order to share ownership of a content Object

* As a manager of a Team
  I want to create a Team Role that encompasses a subset of my Permissions
  In order to delegate some, but not all, Permissions granted by an Object

* As a manager of a Team
  I want to assign a Role on my Team to another User
  In order to delegate Permissions granted by Team-owned Objects

* As the manager of a Role,
  I want to be given a list of my Permissions that are available to delegate,
  So that I can easily build a Role

  - How to assemble this list? Can't be as permissive as superuser access, can
    only consist of Permissions available to Team creator

* As a manager of a content Object,
  I want to be able to create a Policy that encompasses a set of Permissions,
  In order to delegate Permissions to Users who are not Team members

* As a creator of content Objects in a hierarchical tree,
  I want Team ownership to apply recursively down through the tree,
  In order to avoid assigning Team ownership to each child Object individually

* As a creator of content Objects in a hierarchical tree,
  I want a Policy to apply recursively down through the tree,
  In order to avoid assigning a Policy to each child Object individually


.. |build-status| image:: https://secure.travis-ci.org/lmorchard/django-teamwork.png?branch=master
           :target: http://travis-ci.org/lmorchard/django-teamwork

.. vim:set tw=78 ai fo+=n fo-=l ft=rst:
