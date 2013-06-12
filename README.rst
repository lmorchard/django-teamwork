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

* Role inheritance 

  - All permissions applied to parent role apply to child

* Default roles for unauthenticated and non-team-member users
  
  - Useful for things like (dis)allowing view by default

* Recursive team ownership

  - If a content object claims another as a parent (ie. with a
    conventionally-named API), it can be considered as owned by the parent's
    team if any.


.. |build-status| image:: https://secure.travis-ci.org/lmorchard/django-teamwork.png?branch=master
           :target: http://travis-ci.org/lmorchard/django-teamwork

.. vim:set tw=78 ai fo+=n fo-=l ft=rst:
