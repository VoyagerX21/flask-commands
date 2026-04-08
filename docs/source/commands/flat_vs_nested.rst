Flat vs Nested as a Concept
===========================

By this point you have seen flat and nested structures from both directions.
Now it is worth slowing down and talking about the idea itself, because this
is not really a command problem, it is a design decision.

The Short Version
-----------------

- **Flat** means the thing stands on its own.
- **Nested** means the thing belongs under something else.

That is the whole big idea.

If you only keep one sentence from this chapter, keep that one.

Flat Structure
--------------

.. youtube_embed:: understand-flat-structure

A flat resource stands on its own.

For example:

- ``comments.index``
- ``CommentController``
- ``Comment``

That gives you routes like:

- ``/comments``
- ``/comments/<int:comment_id>``

Flat structure is a good fit when the resource makes sense by itself.

Nested Structure
----------------

.. youtube_embed:: understand-nested-structure

A nested resource belongs under a parent.

For example:

- ``recipes.comments.index``
- ``RecipeCommentController``
- ``Comment`` under ``Recipe``

That gives you routes like:

- ``/recipes/<int:recipe_id>/comments``
- ``/recipes/<int:recipe_id>/comments/<int:comment_id>``

Nested structure is a good fit when the child depends on the parent.

How to Choose
-------------

.. youtube_embed:: how-to-choose-flat-vs-nested

Choose **flat** when:

- the resource makes sense on its own
- you expect to reach it without first visiting a parent
- the parent relationship is not the most important part of the story

Choose **nested** when:

- the child depends on the parent
- the route should clearly show that dependency
- you want the folders, routes, and endpoint names to reflect the relationship

There is not always one perfect answer. Sometimes both are valid. That is why
Flask-Commands prompts in those ambiguous cases instead of pretending the
decision is obvious.

Why This Matters
----------------

.. youtube_embed:: why-flat-vs-nested-matters

This choice affects more than the URL.

It affects:

- controller naming
- route folders
- template folders
- endpoint names
- how easily someone can understand the app later

When the structure matches the data relationship, the application becomes much
easier to read.

Wrap-Up
-------

Flat vs nested is not really about flags.

It is about deciding whether one thing stands alone or belongs under another
thing.

Once that idea is clear in your head, the command flags stop feeling magical
and start feeling like honest ways to express the structure you actually want.
