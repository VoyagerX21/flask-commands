make:model Flat vs Nested
=========================

Some model names describe one obvious structure. Others can describe more than
one valid resource shape, and Flask-Commands lets you choose the one that fits
your application.

Choose Flat vs Nested with ``--crud``
-------------------------------------

.. youtube_embed:: choose-flat-vs-nested-with-make-model-crud

Sometimes a model name describes one obvious structure.

Sometimes it describes more than one.

For example, if ``User`` already exists and you run:

.. code-block:: bash

   flask make:model UserComment --crud

Flask-Commands can see two valid stories:

- flat: ``UserComment``
- nested: ``Comment`` under ``User``

If you choose **flat**:

- model generated: ``UserComment``
- controller generated: ``UserCommentController``
- routes generated under ``/user-comments``
- templates generated under ``app/templates/user_comments/``

If you choose **nested**:

- model generated: ``Comment``
- controller generated: ``UserCommentController``
- routes generated under ``/users/<int:user_id>/comments``
- templates generated under ``app/templates/users/comments/``

You can skip the prompt with:

.. code-block:: bash

   flask make:model UserComment --crud --flat
   flask make:model UserComment --crud --nest

The rules are:

- ``--flat`` and ``--nest`` are mutually exclusive
- ``--flat`` and ``--nest`` require ``--crud``

That keeps the command honest. A name like ``UserComment`` can describe a flat
resource or a nested one, and sometimes it is better to ask than pretend the
choice is obvious.

Now that you have seen flat and nested from both directions, we can step back
and talk about the bigger design idea behind the choice.
