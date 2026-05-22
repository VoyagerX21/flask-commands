Video Series
============

This page gathers the Flask-Commands video course in documentation order while
also giving each major topic area its own home in the docs navigation.

:doc:`Watch the Series in Order </videos/watch_the_series_in_order>`
--------------------------------------------------------------------------------

Start here if you want the closest thing to a full playlist. This page follows
the documentation from the welcome material through installation, project
setup, generators, nested resources, and architecture choices.

The takeaway is the full course flow: what Flask-Commands is for, how to get it
running, how to build with it, and how the later structure decisions fit
together.

:doc:`Welcome and Setup Videos </videos/welcome_and_setup_videos>`
--------------------------------------------------------------------------------

Here you will find the orientation material, installation steps, project
creation flow, and the core ideas readers should understand before the deeper
generator chapters.

The takeaway is foundation: what the tool does, how to install it cleanly, how
to start a project safely, and which naming and routing ideas make the rest of
the docs easier to understand.

:doc:`make:view Videos </videos/make_view_videos>`
--------------------------------------------------------------------------------

These videos follow the page-first workflow, including basic view generation,
smarter prompts and normalization, first resource-building, and nested view
work.

The takeaway is page-first scaffolding: how to generate templates and routes
quickly, when the prompts are helping you, and how nested view structure grows
without turning into guesswork.

:doc:`make:controller Videos </videos/make_controller_videos>`
--------------------------------------------------------------------------------

That group follows the controller-first workflow, from simple controller
creation through CRUD scaffolding, controller-driven model generation, and
structure choices.

The takeaway is controller-first thinking: when to start from the behavior
layer, how CRUD generation expands a resource, and how model creation can be
pulled into that same workflow.

:doc:`make:model Videos </videos/make_model_videos>`
--------------------------------------------------------------------------------

This page follows the model-first workflow, covering basic model generation,
CRUD scaffolding from a model, and the flat-vs-nested choice when generating
structure.

The takeaway is data-first scaffolding: how to start from the model, how that
decision pushes outward into routes and controllers, and when that workflow
makes more sense than starting from views or controllers.

.. toctree::
   :hidden:
   :maxdepth: 1

   videos/watch_the_series_in_order
   videos/welcome_and_setup_videos
   videos/make_view_videos
   videos/make_controller_videos
   videos/make_model_videos
