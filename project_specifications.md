Package Goal
============
Provide a convention-driven Flask CLI that scaffolds views, controllers, models,
and routes, with minimal typing and predictable defaults. Commands
should be safe to re-run (skipping existing files with clear warnings) and
normalize user input names into the expected formats.

Naming + Normalization Rules
============================
All user input - `dotted_path_with_action`, `controller_name`, or `model_name` - are normalized into the expected format:

- Dotted path with action is a series of relative path segments. These segment determine where the view file will live in the templates folder.  Segments my represent namespaces, or pluralized model, and representing models may end with a RESTful action. A dotted path with action can also be a non-model location such as `admin_panel`.

  - Multiple words in a model or non-model segment srr separated with an underscores (`_`).

  - Normalization condenses repeated separators in `dotted_path_with_action`:
    - `-` is first converted to `_`
    - `\.+` becomes `.`
    - `[_]+` becomes `_`

  - Normalization removes leading and trailing separators:
    `.`, `_`, and `-`. 
  - If the result of the dotteted path with actions is empty (`''`) after the normiaztion process then an error message is returned.

  - Model matching is per segment; compound model names must be expressed with underscores in a single segment (example: `shop_images`). The CLI never combines adjacent segments to match a model.

  - A dotted path with action can contain a namespace at the beginning. The namespace is left as typed after normalization, with no singularization or pluralization.

- Controller names are singularized PascalCase and end with the word "Controller".

- Model names are singularized PascalCase.

Comparing & Interactions
========================
- When comparing a dotted path with action, first remove any action and look only at the relative segments. Each relative segment is singularized and compared to the list of known models (the list of known models is first converted into snake case before comparing).
- This comparison comes into play when a `route_name`, `model_name`, or `controller_name` must be generated from a dotted path with action.

Naming Convention
=================
- Naming convention for helpers: any function that produces a new name from an input should use the verb "generate" in its name (noted for a future refactor).

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
parent_models. Model matching is per segment; segments are not combined.

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
segments are collapsed into a single compound child model for naming/ids only;
this does not attempt to match a registered model. For example,
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
- Singularization/pluralization behavior comes directly from `naming.py`
  (`singularize`, `pluralize`) with no irregular-language dictionary. Example:
  `people.show` may generate `/peoples/<int:people_id>`.
- PascalCase splitting for parameter names follows `split_pascal_case`.
  Acronyms are accepted as-is under that splitter behavior (example:
  `OAuthToken` -> `o_auth_token_id`).

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

**RESTful Action With Empty Relative Path**
When `dotted_path_with_action` is split into `(relative_path, action)`, `action`
always comes from the last segment and can be RESTful even when
`relative_path = ''` (for example: `index`, `show`, `.index`, `.show`).

In this case, do not prompt for model creation or routing strategy.
Because `relative_path = ''`, flat and nested routes are identical.
Return the route as `/{action}`:
- `index` or `.index` -> `/index`
- `show` or `.show` -> `/show`

**Missing Model Prompt (RESTful Actions)**
If a RESTful action is used and the dotted path implies a model (for example,
`admin_reports.show` implies `AdminReport`) but the model is not registered,
prompt the user to create the missing model.

Unmatched leading segments are treated as namespace and do not trigger a
missing-model prompt when a later contiguous run of known models is detected.

If a namespace + segment could also be interpreted as a compound model that is
registered (example: `admin.reports.show` with `AdminReport` registered), prompt
to create the segment model (`Report`). If they accept, use the nested route with
the segment id (`/admin/reports/<int:report_id>`). If they decline, use the
entered segments (`/admin/reports/show`).

When existing segments already appear in the input, preserve them as written
(after normalization). Do not auto-pluralize those existing segments.

If they accept, treat the model as registered for route generation and do not
prompt for routing strategy; assume the nested route (e.g.,
`/admin-reports/<int:admin_report_id>`).
When accepting creation of a missing model segment, use the pluralized model
name in the nested route resource segment (example:
`/posts/<int:post_id>/audits/<int:audit_id>`).

If they decline, prompt them to choose:
1. Flat compound route (example: `/admin-reports-show`)
2. Nested route using the entered segments (example: `/admin-reports/show`)

**Missing Model Prompt (Non-RESTful Actions)**
If a non-RESTful action is used and the dotted path contains a known model,
any later segment that could be a model but is not registered should trigger a
prompt to create the missing model.

If they accept, treat the model as registered and include its id in the nested
route (example: `/part-one/part-two/<int:part_two_id>/part-three/<int:part_three_id>/custom-action`).

If they decline, keep the segment as-is in the nested route without an id
(example: `/part-one/part-two/<int:part_two_id>/part-three/custom-action`).

If flat and nested resolve to the same URL, do not prompt for routing strategy;
return the generated route directly (example: `admin_panel` -> `/admin-panel`).

**Route Examples Table (RESTful)**
Assumes `dotted_path_with_action` is already normalized. `flaten_route` is the flat compound route (single hyphenated segment; underscores become hyphens).

| dotted_path_with_action | registered_models | flaten_route | nested_route | prompt_notes |
| --- | --- | --- | --- | --- |
| `index` | `None` | `/index` | `/index` | No prompt: flat and nested are identical |
| `.index` | `None` | `/index` | `/index` | No prompt: flat and nested are identical |
| `show` | `None` | `/show` | `/show` | No prompt: flat and nested are identical |
| `.show` | `None` | `/show` | `/show` | No prompt: flat and nested are identical |
| `posts.index` | `Post` | `/posts-index` | `/posts` | `-` |
| `posts.index` | `None` | `/posts-index` | `/posts/index` | Prompt to create `Post`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/posts`<br>&nbsp;&nbsp;&nbsp;&nbsp;decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/posts-index`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested -> `/posts/index` |
| `posts.show` | `Post` | `/posts-show` | `/posts/<int:post_id>` | `-` |
| `admin.posts.comments.show` | `Comment, Post` | `/admin-posts-comments-show` | `/admin/posts/<int:post_id>/comments/<int:comment_id>` | `-` |
| `admin.shop_images.show` | `ShopImage` | `/admin-shop-images-show` | `/admin/shop-images/<int:shop_image_id>` | `-` |
| `admin.posts.comments.images.show` | `Comment, Image, Post` | `/admin-posts-comments-images-show` | `/admin/posts/<int:post_id>/comments/<int:comment_id>/images/<int:image_id>` | `-` |
| `admin.posts.comments.images.index` | `Comment, Image, Post` | `/admin-posts-comments-images-index` | `/admin/posts/<int:post_id>/comments/<int:comment_id>/images` | `-` |
| `posts.audit.show` | `Post` | `/posts-audit-show` | `/posts/<int:post_id>/audit/show` | Prompt to create `Audit`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/posts/<int:post_id>/audits/<int:audit_id>`<br>&nbsp;&nbsp;&nbsp;&nbsp;decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/posts-audit-show`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested -> `/posts/<int:post_id>/audit/show`|
| `admin.posts.show` | `Admin` | `/admin-posts-show` | `/admin/<int:admin_id>/posts/show` | Prompt to create `Post`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/admin/<int:admin_id>/posts/<int:post_id>`<br>&nbsp;&nbsp;&nbsp;&nbsp;decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/admin-posts-show`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested -> `/admin/<int:admin_id>/posts/show`  |
| `admin.user_accounts.show` | `AdminUserAccount` | `/admin-user-accounts-show` | `/admin/user-accounts/show` | Prompt to create `UserAccount`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/admin/user-accounts/<int:user_account_id>`<br>&nbsp;&nbsp;&nbsp;&nbsp;decline ->  choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/admin-user-accounts-show`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested -> `/admin/user-accounts/show` |
| `admin.reports.index` | `None` | `/admin-reports-index` | `/admin/reports/index` | Prompt to create `Report`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/admin/reports`<br>&nbsp;&nbsp;&nbsp;&nbsp;decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/admin-reports-index`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested -> `/admin/reports/index`|
| `admin.reports.index` | `AdminReport` | `/admin-reports-index` | `/admin/reports/index` | Prompt to create `Report`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/admin/reports`<br>&nbsp;&nbsp;&nbsp;&nbsp;decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/admin-reports-index`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested -> `/admin/reports/index`|
| `admin_reports.index` | `None` | `/admin-reports-index` | `/admin-reports/index` |Prompt to create `AdminReport`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/admin-reports`;<br>&nbsp;&nbsp;&nbsp;&nbsp;decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/admin-reports-index`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested -> `/admin-reports/index`|
| `admin_reports.index` | `AdminReport` | `/admin-reports-index` | `/admin-reports` | `-` |
| `admin.reports.show` | `None` | `/admin-reports-show` | `/admin/reports/show` | Prompt to create `Report`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/admin/reports/<int:report_id>`<br>&nbsp;&nbsp;&nbsp;&nbsp;decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/admin-reports-show`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested ->`/admin/reports/show` |
| `admin.reports.show` | `AdminReport` | `/admin-reports-show` | `/admin/reports/show` | Prompt to create `Report`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/admin/reports/<int:report_id>`<br>&nbsp;&nbsp;&nbsp;&nbsp;decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/admin-reports-show` <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested -> `/admin/reports/show` |
| `admin_reports.show` | `None` | `/admin-reports-show` | `/admin-reports/show` | Prompt to create `AdminReport`:<br>&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/admin-reports/<int:admin_report_id>`;<br>&nbsp;&nbsp;&nbsp;&nbsp;decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat -> `/admin-reports-show`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested -> `/admin-reports/show` |
| `admin_reports.show` | `AdminReport` | `/admin-reports-show` | `/admin-reports/<int:admin_report_id>` | `-` |

**Route Examples Table (Non-RESTful)**
`flaten_route` is the flat compound route (single hyphenated segment; underscores become hyphens). Underscores become hyphens in nested route segments, including the action name.

| dotted_path_with_action | registered_models | flaten_route | nested_route | prompt_notes |
| --- | --- | --- | --- | --- |
| `landing` | `None` | `/landing` | `/landing` | No prompt: flat and nested are identical |
| `admin_panel` | `None` | `/admin-panel` | `/admin-panel` | No prompt: flat and nested are identical |
| `company.about` | `None` | `/company-about` | `/company/about` | `-` |
| `team.about` | `None` | `/team-about` | `/team/about` | `-` |
| `abouts.team` | `None` | `/abouts-team` | `/abouts/team` | `-` |
| `abouts.company` | `None` | `/abouts-company` | `/abouts/company` | `-` |
| `components.button` | `None` | `/components-button` | `/components/button` | `-` |
| `company.about.team` | `None` | `/company-about-team` | `/company/about/team` | `-` |
| `components.ui.buttons.primary` | `None` | `/components-ui-buttons-primary` | `/components/ui/buttons/primary` | `-` |
| `admin_panel.stats` | `None` | `/admin-panel-stats` | `/admin-panel/stats` | `-` |
| `posts.custom_action` | `Post` | `/posts-custom-action` | `/posts/<int:post_id>/custom-action` | `-` |
| `posts.archive` | `Post` | `/posts-archive` | `/posts/<int:post_id>/archive` | `-` |
| `admin.user_accounts.security_logs.custom_action` | `UserAccount` | `/admin-user-accounts-security-logs-custom-action` | `/admin/user-accounts/<int:user_account_id>/security-logs/custom-action` | Prompt to create `SecurityLog`:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;accept -> `/admin/user-accounts/<int:user_account_id>/security-logs/<int:security_log_id>/custom-action`<br>decline -> choose<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;flat ->`/admin-user-accounts-security-logs-custom-action`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nested ->`/admin/user-accounts/<int:user_account_id>/security-logs/custom-action` |


**Explicit Route Override**
Providing --route bypasses all inference and disables all route/model prompts.
`--route` is authoritative and is used exactly as provided, even when it does
not match what `dotted_path_with_action` inference would generate.

Example:
```bash
flask make:view admin.posts.comments.create --route "/internal/reporting/comments"
```

**Model Generation (-m)**
-m prompts for nesting vs flat.

Nesting: inspect the dotted path for model relationships and choose the child
model, which may be a compound segment already written with underscores
(example: `shop_images`).

Flat: treat the entire dotted path (minus the action) as one resource.

**File Safety**
- The CLI is safe to re-run.
- Existing files are never overwritten.
- Imports are appended safely.
- Routes are registered without duplicating entries.
- If a route already exists, it is not overwritten and a clear warning is shown.
- If different inputs resolve to an existing route, the existing route is kept
  and the new one is skipped with a warning.
- Clear warnings are shown when a file already exists.

**Future Release Notes**
- Add `flask undo` to revert the most recent command's generated changes.

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
