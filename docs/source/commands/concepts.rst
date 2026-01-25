Concepts
========

This chapter explains the rules Flask-Commands follows, so the rest of the book
feels predictable rather than mysterious. In other words: fewer surprises, more
expectations.

Dot notation
------------

Many commands accept a dotted name such as ``recipes.comments.index``.

This is used to:

- create nested folders (templates and routes)
- register nested blueprints so dotted endpoint names work
- keep large apps tidy without you needing to do the wiring by hand

Generator flags
---------------

The ``flask make:view`` command supports optional generator flags:

- ``-c / --generate-controller`` or ``--controller NAME``
  Creates (or extends) a controller **class** in your application.
- ``-r / --generate-route`` or ``--route PATH``
  Adds blueprint routes and supports the seven RESTful actions.
- ``-m / --generate-model`` or ``--model NAME``
  Seeds a SQLAlchemy model with boilerplate columns.

You’ll see these combined frequently as ``-rc`` and ``-rcm``.
