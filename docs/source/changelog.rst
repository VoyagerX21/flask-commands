Changelog
=========

All notable changes to this project are documented here.
This project follows `Keep a Changelog <https://keepachangelog.com/>`_ and
`SemVer <https://semver.org/>`_.

Unreleased
----------
Added
~~~~~
- Started work on new command ``flask make:controller``
- Add a project-root safeguard so ``flask make:...`` commands only run when ``app/`` and ``run.py`` are present.

Changed
~~~~~~~
-

Fixed
~~~~~
-

0.1.21 - 2026-01-17
-------------------
Added
~~~~~
- Add tests for nested route blueprint registration and controller creation with route names.

Changed
~~~~~~~
- Clarify scaffold helpers for model detection and CRUD route generation.
- Remove the top-level CHANGELOG.md in favor of this docs changelog.

Fixed
~~~~~
- Avoid controller_make_file crashing when no route_name is provided.
- Fix small typos in tests and view docstrings.
- Register nested relationship blueprints with their parent instead of the top-level route, enabling full dotted-path route naming.

0.1.20 - 2026-01-16
-------------------
Added
~~~~~
- Add changelog page to the docs toctree and remove the top nav link.

Changed
~~~~~~~
- Update flask make:view documentation with clearer examples and RESTful guidance.
- Improve nested blueprint registration so `url_for` uses dot notation consistently,
  avoiding mixed dot/underscore names in nested relationships.
- Register nested blueprints at the top of the relationship tree instead of the app level.

Fixed
~~~~~
- Placeholder for upcoming fixes.

0.1.19 - 2026-01-10
-------------------

Changed
~~~~~~~
- Update commands documentation and release notes.

Fixed
~~~~~
- Fix a second typo in controller comment text that was breaking tests.

0.1.18 - 2026-01-10
-------------------

Changed
~~~~~~~
- Update release notes.

Fixed
~~~~~
- Fix a controller comment typo that was breaking tests.

0.1.17 - 2026-01-10
-------------------

Added
~~~~~
- Add `project.urls` metadata (homepage, repo, issues) to `pyproject.toml`.
- Add controller registration feedback to the success output.

Changed
~~~~~~~
- Expand commands documentation (nested views and RESTful actions).
- Refresh README and docs index copy.

Fixed
~~~~~
- Fix `flask make:view about -rc` warning by inferring `MainController` when
  `-c` is provided; update tests accordingly.

0.1.16 - 2026-01-10
-------------------

Changed
~~~~~~~
- Remove unused docs dependency blocks and extras from `pyproject.toml`.
- Simplify configuration and reduce `poetry.lock` churn.

0.1.15 - 2026-01-09
-------------------

Changed
~~~~~~~
- Minor README and docs navigation updates.
- Small Sphinx configuration tweak.

0.1.14 - 2026-01-09
-------------------

Changed
~~~~~~~
- Update README image source and bump version.

0.1.13 - 2026-01-09
-------------------

Changed
~~~~~~~
- Update README copy and PyPI badge versions.

0.1.12 - 2026-01-09
-------------------

Changed
~~~~~~~
- Iterate on publish-to-PyPI workflow configuration.

0.1.11 - 2026-01-09
-------------------

Changed
~~~~~~~
- Tweak publish-to-PyPI workflow configuration.

0.1.10 - 2026-01-09
-------------------

Changed
~~~~~~~
- Tweak publish-to-PyPI workflow configuration.

0.1.9 - 2026-01-09
------------------

Changed
~~~~~~~
- Tweak publish-to-PyPI workflow configuration.

0.1.8 - 2026-01-09
------------------

Changed
~~~~~~~
- Version bump only.

0.1.7 - 2026-01-08
------------------

Changed
~~~~~~~
- Update publish-to-PyPI workflow configuration.

0.1.6 - 2026-01-08
------------------

Changed
~~~~~~~
- Version bump only.

0.1.5 - 2026-01-08
------------------

Changed
~~~~~~~
- Update publish-to-PyPI workflow configuration.

0.1.4 - 2026-01-08
------------------

Changed
~~~~~~~
- Update publish-to-PyPI workflow configuration.

0.1.3 - 2026-01-08
------------------

Changed
~~~~~~~
- Update publish-to-PyPI workflow configuration.
- Remove small README artifacts during workflow cleanup.

0.1.2 - 2026-01-08
------------------

Changed
~~~~~~~
- Update publish-to-PyPI workflow configuration.

0.1.1 - 2026-01-08
------------------

Added
~~~~~
- Sphinx documentation scaffold, Read the Docs configuration, and Makefiles.
- Project logo asset, theme CSS overrides, and Read the Docs badges.
- PyPI publish workflow that triggers on version changes.
- Template-based project scaffolding with config, routes, controllers, and run
  scripts.
- Tailwind CSS setup in generated projects (npm install, input.css, template
  wiring).
- `make:view` command and supporting controller/view utilities.
- Optional route flag support, route parameter handling, and controller
  generation enhancements.
- SQLite development setup and example model scaffolding.
- Initial test suite, coverage configuration, and CI workflow.

Changed
~~~~~~~
- Refactor utilities from a monolithic module into focused files
  (controllers, files, models, naming, routes, scaffold, venv, views).
- Rework `flask new`, view, and route messaging for clearer feedback.
- Improve route inference, blueprint registration, and generation flow.
- Update README and docs content as features landed.
- Adjust project structure to use `flask_commands/project` templates.

Fixed
~~~~~
- Ensure `append_file` inserts a newline and handles empty files safely.
- Guard blueprint registration when `return app` is missing.
- Fix controller option errors and model name inference.
- Improve error handling for controller/model generation and align tests.

0.1.0 - 2025-11-23
------------------

Added
~~~~~
- Initial repository structure, CLI entrypoint, and command stubs.
- Project metadata, license, and base README.
