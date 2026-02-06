Package Goal
============
Provide a convention-driven Flask CLI that scaffolds views, controllers, models,
routes, and templates with minimal typing and predictable defaults. Commands
should be safe to re-run (skipping existing files with clear warnings) and
normalize input names into the expected formats.

Naming + Normalization Rules
============================
- Dotted paths are plural (models/resources are plural in the path).
- Controller names are singular PascalCase and must end with "Controller".
- Model names are singular PascalCase.
- Namespaces are left exactly as typed (after normalization), with no
  singularization or pluralization.
- All user input is normalized into the expected format (case, separators,
  suffixes).
- When comparing dotted path segments to models/controllers, convert plural path
  segments to singular before matching.
- Naming convention for helpers: any function that produces a new name from an
  input should use the verb "generate" in its name (noted for a future
  refactor).

Command Goals
=============

## Make View: flask make:view dotted_path_with_action

**Summary**
Creates a view template and optionally generates the associated route,
controller, and model using convention-driven defaults. The command normalizes
input names, detects namespaces, and safely updates project files without
overwriting existing user code.

**Basic Usage**
```bash
flask make:view dotted_path_with_action
```

**Example**
```bash
flask make:view posts.index
```

**Creates**
```
app/templates/posts/index.html
```

No routes, controllers, or models are generated unless explicitly requested.

**Generator Flags**

| Flag | Description |
| --- | --- |
| -r, --generate-route | Generate and register a route inferred from the dotted path. |
| -c, --generate-controller | Generate or update the controller used by the route. |
| -m, --generate-model | Generate a model inferred from the dotted path. |
| --route | Register the explicit route URL provided. |
| --controller | Use the explicit controller name provided (verbatim). |
| --model | Use the explicit model name provided (verbatim). |

**Flag Combination**
```bash
flask make:view posts.index -rcm
```

**Dotted Path Structure**
```
[namespace.]models[.nested_models][.action]
```

**Examples**
```
posts.index
posts.comments.show
admin.posts.create
admin.posts.comments.edit
landing
components.buttons
```

**Token Definitions**
- Namespace: structural prefix used for route grouping and file paths.
- Models: plural model names in the path.
- Action: optional controller method and view name. When present, it is the
  final segment.

**Namespace + Model Detection**
Namespaces are automatically detected. The CLI scans path segments from left to
right, matching plural model segments (singularized for comparison) against
known models exported in app/models/__init__.py. Any unmatched leading segments
become the namespace; the first contiguous run of matched models becomes
parent_models.

Controller name inference from a relative path is convention-only (singularize
each path segment, PascalCase, append Controller) and does not depend on
existing models.

Example:
```
admin.posts.comments.create
```

Detected as:
```
Namespace: admin
Models: Post -> Comment
Action: create
```

**Nested Naming Convention**
Nested paths are described as:
```
namespace/parent_models/child_model
```
This convention is used consistently for route inference, controller naming,
and model prompts.

If there are leftover unmatched segments after finding parent models, those
segments are collapsed into a single compound child model. For example,
`admin.posts.shop.images.show` yields:
namespace = admin, parent_models = posts, child_model = shop_images
which maps to a singular child id of `shop_image_id`.

**Route Generation (-r)**
-r generates a URL rule inferred from the dotted path. If --route is provided,
the CLI registers the route exactly as written and skips inference.

Example:
```bash
flask make:view posts.index --route "/articles"
```

**Single Resource Routes**
```bash
flask make:view posts.index -r
```
Generates:
```
/posts
```

**Member Action**
```bash
flask make:view posts.show -r
```
Generates:
```
/posts/<int:post_id>
```

**Non-RESTful Actions**
If the dotted path does not end with a RESTful action, the last segment is treated
as a view name only. The -r flag still infers a route (for example, /landing).

**RESTful Action Semantics**
- If the action is one of index, show, create, store, edit, update, destroy,
  delete, it is treated as RESTful even if no model matches are found.
- HTTP methods follow RESTful semantics: store/update/destroy/delete use POST;
  all others use GET.

**Route Parameter Rules**
- Parameter names derive from the singular model name.
- <int:id> is never used unless explicitly defined via --route.
- For compound child models, the parameter uses the full compound name:
  <int:recipe_comment_image_id>.

**Multiple Models: Routing Strategy Prompt**
When multiple models are detected, the CLI prompts for a routing strategy.
If no model matches are found, the CLI defaults to flat (no prompt), unless a
RESTful action is present (see below).
Prompt choices are per-invocation and are not remembered.

Example:
```
Multiple models detected: posts -> comments
```

Choose routing strategy:
1. Nested
2. Flat (compound route)

**Nested Routing**
Treat earlier models as parents and include their identifiers in the URL.

```bash
flask make:view admin.posts.comments.show -r
```
Generates:
```
/admin/posts/<int:post_id>/comments/<int:comment_id>
```

Rules:
- Namespaces become URL prefixes.
- Models remain plural.
- Route parameters use singular model names.
- Compound child models use the full compound singular name for the id
  (example: `shop_images` -> `shop_image_id`).

**Flat Routing (Compound Routes)**
Flat routing collapses namespaces, models, and the action into a single
hyphenated URL segment. Flat routes always include the action segment when
present.

```bash
flask make:view admin.posts.comments.create -r
```
Generates:
```
/admin-posts-comments-create
```

**RESTful Action With No Model Matches**
If the action is RESTful but no model matches are found, prompt the user to
choose between:
1. RESTful-style route based on the namespace (example: /admin-reports/<int:admin_reports_id>)
2. Flat compound route (example: /admin-reports-index)

**Explicit Route Override**
Providing --route bypasses all inference and disables the routing prompt.

Example:
```bash
flask make:view admin.posts.comments.create --route "/internal/reporting/comments"
```

**Model Generation (-m)**
-m prompts for nesting vs flat.

Nesting: inspect the dotted path for model relationships and choose the child
model, which may be multiple parts of the relationship name.

Flat: treat the entire dotted path (minus the action) as one resource.

**File Safety**
- The CLI is safe to re-run.
- Existing files are never overwritten.
- Imports are appended safely.
- Routes are registered without duplicating entries.
- Clear warnings are shown when a file already exists.

**Examples**
```bash
flask make:view posts.index
flask make:view posts.index -rcm
flask make:view posts.comments.index -rcm
flask make:view landing -r
flask make:view posts.show --route "/posts/<int:post_id>" --controller PostController --model Post
```

## Make Controller: flask make:controller ControllerName

**Summary**
Scaffolds a controller class and optionally generates RESTful routes, views, and
an associated model.

**Flags**
Optional flags: --crud, -m, --model

**Expectation**
ControllerName is singular PascalCase ending in "Controller".

**Behavior**
No flags: create a stub controller class in app/controllers and register it in
app/controllers/__init__.py.

--crud: create a controller with the seven RESTful actions, generate the routes,
register the blueprint, and create the four GET views (index, show, create,
edit). No templates are generated for store/update/destroy/delete.

**Nesting Prompt With --crud**
Remove the "Controller" suffix and split on capital letters. Prompt to choose
nested vs flat routing.
Prompt choices are per-invocation and are not remembered.

**Nesting Detection (namespace/parent_models/child_model)**
1. Strip the "Controller" suffix, then split the remaining name into parts.
2. Scan parts from left to right, matching against registered models.
3. Any leading unmatched parts become the namespace.
4. The first contiguous match becomes parent_models.
5. Any remaining unmatched parts become the child_model.
6. The derived path is written as: namespace/parent_models/child_model.
7. If no model matches are found, default to flat (no prompt).

Nested: routes like /parent/<int:parent_id>/child, with parent ids on all routes
and child ids on member routes.

Flat: treat the remaining name as a single resource.

**Model Generation**
-m or --model: generate a model.

If nesting is chosen, the model is the child model.
If flat, the model is the base name (ControllerName minus "Controller").

**Examples**
```bash
flask make:controller RecipeController
flask make:controller IngredientController --crud
flask make:controller RecipeIngredientController --crud -m
```

## Make Model: flask make:model ModelName

**Summary**
Scaffolds a model and optionally generates a matching controller, routes, and
views for RESTful actions.

**Flags**
Optional flags: --crud

**Expectation**
ModelName is singular PascalCase.

**Behavior**
No flags: create a stub model in app/models and register it in app/models/__init__.py.

--crud: create the model plus matching controller, routes, and the four GET
views (index, show, create, edit). No templates are generated for
store/update/destroy/delete.

**Nesting Prompt With --crud**
Split ModelName on capital letters to detect nested relationships. Prompt to
choose nested vs flat routing.
Prompt choices are per-invocation and are not remembered.

**Nesting Detection (namespace/parent_models/child_model)**
1. Split ModelName into parts by capital letters.
2. Scan parts from left to right, matching against registered models.
3. Any leading unmatched parts become the namespace.
4. The first contiguous match becomes parent_models.
5. Any remaining unmatched parts become the child_model.
6. The derived path is written as: namespace/parent_models/child_model.
7. If no model matches are found, default to flat (no prompt).

If nested and parent models exist, generate missing routes/controllers as
needed; do not overwrite existing files.

If flat and the model already exists, do nothing.

**Examples**
```bash
flask make:model Comment
flask make:model Comment --crud
flask make:model RecipeComment --crud
```
