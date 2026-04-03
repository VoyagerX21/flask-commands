Release Notes
=============

This page is where version-specific changes belong. The command chapters teach
the package as it works now. This page explains what changed, why it changed,
and why those changes matter when you are actually building with
Flask-Commands.

Current Development Notes
-------------------------

The next release is focused on making the generators more flexible without
making them harder to understand.

The biggest changes are:

- ``flask new --no-db`` for projects that do not want database wiring yet
- ``--flat`` and ``--nest`` overrides for ambiguous controller and model flows
- interactive prompts when a nested model shape could reasonably go more than
  one way
- cleaner route and dotted-path normalization across the command set
- better nested parent-route scaffolding for multi-level resources
- documentation updates so the behavior and the docs finally tell the same
  story

Why These Changes Matter
------------------------

**Prefer a walkthrough? Click to expand a YouTube Tutorial**

*Video placeholder: Why the latest release changes matter.*

``flask new --no-db`` matters because not every project needs a database on
day one.

``--flat`` and ``--nest`` matter because some names honestly describe more
than one valid structure, and it is better to let you choose than guess wrong.

The prompt improvements matter because they help Flask-Commands stay helpful
without becoming mysterious.

And the docs refresh matters because a command-line tool is only as friendly as
the explanation that comes with it.

Read the Full History
---------------------

If you want the full historical changelog with every version entry, the next
page in the docs still keeps that running history intact.
