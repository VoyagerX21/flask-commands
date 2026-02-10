Package Goal
============
Provide a convention-driven Flask CLI that scaffolds views, controllers, models,
and routes, with minimal typing and predictable defaults. Commands
should be safe to re-run (skipping existing files or function/methods with clear warnings) and
normalize user input names into the expected formats.

 Normalization Rules
============================
All user inputs  `dotted_path_with_action`, `controller_name`, or `model_name` are normalized into the following format:

- Dotted path with action is a series of relative path segments separated by dots. These segments determine where the view file will live in the templates folder. Segments are often used to represent namespaces, pluralized models, and can end with a RESTful action. A segement my contain multiple words eparated with underscores (`_`). The dottted path can define hierarchy and action.

  - The Normalization prococced
    - Condenses repeated separators in `dotted_path_with_action`:
      - `-` is first converted to `_`
      - `\.+` becomes `.`
      - `[_]+` becomes `_`
    - Removes leading and trailing separators:
      - `.`, `_`, and `-`.

  - If the result of the dotted path with action is empty (`''`) after the normalization process then an error message is returned.

- Controller names are singularized PascalCase and end with the word "Controller".

- Model names are singularized PascalCase.

Comparing & Interactions
========================
- The CLI can generate a `route_name`, `model_name`, or `controller_name`  from a dotted path with action using the following procedure:
  - Split the dotted path with actions over all dots and calling each piece a segment and the last piece the action.  The segments make up a relative path. Each relative segment is singularized and compared to the list of registered models (the list of registered models is first converted into snake case before comparing).  If the sgement matches a known model then id for the signular version of the sement is placed in the route name.  If the action is RESTful, then the approprate restful ending is added to the route name, otherwise the ending
  - Model matching is per segment; compound model names must be expressed with underscores in a single segment (example: `shop_images`). The CLI never combines adjacent segments to match a model.

Command Goals
=============

## Make View: flask make:view dotted_path_with_action

**Summary**
Creates a view template and optionally generates the associated route, controller, and model
using comparing and interactions described above. The command will first normalizes
the input of the dotted path with action, and safely updates project files without
overwriting existing user code.  If the route's function already exist, if the view file already exist, or if the controller method already exist file updates/creation will  be skipped and a warning will display to the user.

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
[namespace].[models].[child_models].[action]
```
Most of the dotted path will be in the above format; however, this is just a suggestion and not required.  Only dots split segments; underscores stay inside a segment. For example, `posts_index` is a single segment and is not treated as `posts.index`.

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
  final dot-separated segment.

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

**Hierarchy Naming Convention**
Hierarchical paths are described as:
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
Because underscores do not split, inputs like `posts_index` are treated as a
non-RESTful action name and map to `/posts-index` when generating a route.

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

**Routing Is Deterministic**
The CLI generates a single route from the dotted path. There is no flat vs
nested choice.

Rules:
- Dots become URL slashes.
- Underscores become hyphens.
- RESTful actions follow RESTful patterns and insert `<int:..._id>` for segments
  that match registered models.
- Non-RESTful actions keep the last segment as the action and include ids for
  any earlier model segments.

**RESTful Action With Empty Relative Path**
When `dotted_path_with_action` is split into `(relative_path, action)`, `action`
always comes from the last segment and can be RESTful even when
`relative_path = ''` (for example: `index`, `show`, `.index`, `.show`).

In this case, return the route as `/{action}`:
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
to create the segment model (`Report`). If they accept, include the segment id
in the generated route (`/admin/reports/<int:report_id>`). If they decline, keep
the entered segments (`/admin/reports/show`).

When existing segments already appear in the input, preserve them as written
(after normalization). Do not auto-pluralize those existing segments.

If they accept, treat the model as registered for route generation and include
its id in the generated route (e.g., `/admin-reports/<int:admin_report_id>`).
When accepting creation of a missing model segment, use the pluralized model
name in the route resource segment (example:
`/posts/<int:post_id>/audits/<int:audit_id>`).

If they decline, keep the segment as written (no id is inserted).

**Non-RESTful Actions Never Prompt**
Non-RESTful routes are deterministic. The CLI never prompts to create models
for non-RESTful actions. It only inserts ids for segments that already match
registered models and leaves all other segments as written.

**Route Examples Table (RESTful)**
Assumes `dotted_path_with_action` is already normalized. `generated_route` is the inferred route.

| dotted_path_with_action | registered_models | generated_route | prompt |
| --- | --- | --- | --- |
| `index` | `None` | `/index` | No prompt |
| `.index` | `None` | `/index` | No prompt |
| `show` | `None` | `/show` | No prompt |
| `.show` | `None` | `/show` | No prompt |
| `posts.index` | `Post` | `/posts` | No prompt |
| `posts.index` | `None` | `/posts/index` | Prompt to create `Post`: accept -> `/posts` |
| `posts.show` | `Post` | `/posts/<int:post_id>` | No prompt |
| `admin.posts.comments.show` | `Comment, Post` | `/admin/posts/<int:post_id>/comments/<int:comment_id>` | No prompt |
| `admin.shop_images.show` | `ShopImage` | `/admin/shop-images/<int:shop_image_id>` | No prompt |
| `admin.posts.comments.images.show` | `Comment, Image, Post` | `/admin/posts/<int:post_id>/comments/<int:comment_id>/images/<int:image_id>` | No prompt |
| `admin.posts.comments.images.index` | `Comment, Image, Post` | `/admin/posts/<int:post_id>/comments/<int:comment_id>/images` | No prompt |
| `posts.audit.show` | `Post` | `/posts/<int:post_id>/audit/show` | Prompt to create `Audit`: accept -> `/posts/<int:post_id>/audits/<int:audit_id>` |
| `admin.posts.show` | `Admin` | `/admin/<int:admin_id>/posts/show` | Prompt to create `Post`: accept -> `/admin/<int:admin_id>/posts/<int:post_id>` |
| `admin.user_accounts.show` | `AdminUserAccount` | `/admin/user-accounts/show` | Prompt to create `UserAccount`: accept -> `/admin/user-accounts/<int:user_account_id>` |
| `admin.reports.index` | `None` | `/admin/reports/index` | Prompt to create `Report`: accept -> `/admin/reports` |
| `admin.reports.index` | `AdminReport` | `/admin/reports/index` | Prompt to create `Report`: accept -> `/admin/reports` |
| `admin_reports.index` | `None` | `/admin-reports/index` | Prompt to create `AdminReport`: accept -> `/admin-reports` |
| `admin_reports.index` | `AdminReport` | `/admin-reports` | No prompt |
| `admin.reports.show` | `None` | `/admin/reports/show` | Prompt to create `Report`: accept -> `/admin/reports/<int:report_id>` |
| `admin.reports.show` | `AdminReport` | `/admin/reports/show` | Prompt to create `Report`: accept -> `/admin/reports/<int:report_id>` |
| `admin_reports.show` | `None` | `/admin-reports/show` | Prompt to create `AdminReport`: accept -> `/admin-reports/<int:admin_report_id>` |
| `admin_reports.show` | `AdminReport` | `/admin-reports/<int:admin_report_id>` | No prompt |

**Route Examples Table (Non-RESTful)**
Assumes `dotted_path_with_action` is already normalized. `generated_route` is the inferred route.

| dotted_path_with_action | registered_models | generated_route |
| --- | --- | --- |
| `landing` | `None` | `/landing` |
| `admin_panel` | `None` | `/admin-panel` |
| `company_about` | `None` | `/company-about` |
| `posts_index` | `None` | `/posts-index` |
| `company.about` | `None` | `/company/about` |
| `team.about` | `None` | `/team/about` |
| `abouts.team` | `None` | `/abouts/team` |
| `abouts.company` | `None` | `/abouts/company` |
| `components.button` | `None` | `/components/button` |
| `company.about.team` | `None` | `/company/about/team` |
| `components.ui.buttons.primary` | `None` | `/components/ui/buttons/primary` |
| `admin_panel.stats` | `None` | `/admin-panel/stats` |
| `posts.custom_action` | `Post` | `/posts/<int:post_id>/custom-action` |
| `posts.archive` | `Post` | `/posts/<int:post_id>/archive` |
| `admin.user_accounts.security_logs.custom_action` | `UserAccount` | `/admin/user-accounts/<int:user_account_id>/security-logs/custom-action` |


**Explicit Route Override**
Providing --route bypasses all inference and disables all route/model prompts.
`--route` is authoritative and is used exactly as provided, even when it does
not match what `dotted_path_with_action` inference would generate.

Example:
```bash
flask make:view admin.posts.comments.create --route "/internal/reporting/comments"
```

**Model Generation (-m)**
-m generates the inferred model from the dotted path.
The model is the singularized last segment of the relative path (or the
compound remainder if unmatched segments are collapsed, e.g. `shop_images`).

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

**Hierarchy Detection With --crud**
Remove the "Controller" suffix and split on capital letters. The CLI derives
the route hierarchy deterministically; there is no flat vs nested prompt.

**Nesting Detection (namespace/parent_models/child_model)**
1. Strip the "Controller" suffix, then split the remaining name into parts.
2. Scan parts from left to right, matching against registered models.
3. Any leading unmatched parts become the namespace.
4. The first contiguous match becomes parent_models.
5. Any remaining unmatched parts become the child_model.
6. The derived path is written as: namespace/parent_models/child_model.
7. If no model matches are found, treat the remaining name as a single resource.

If parent models are detected, routes include parent ids on all routes and child
ids on member routes.

**Model Generation**
-m or --model: generate a model.

If parent models are detected, the model is the child model. Otherwise, the
model is the base name (ControllerName minus "Controller").

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

**Hierarchy Detection With --crud**
Split ModelName on capital letters to detect hierarchical relationships. The CLI
derives the route hierarchy deterministically; there is no flat vs nested prompt.

**Nesting Detection (namespace/parent_models/child_model)**
1. Split ModelName into parts by capital letters.
2. Scan parts from left to right, matching against registered models.
3. Any leading unmatched parts become the namespace.
4. The first contiguous match becomes parent_models.
5. Any remaining unmatched parts become the child_model.
6. The derived path is written as: namespace/parent_models/child_model.
7. If no model matches are found, treat the remaining name as a single resource.

If parent models exist, generate missing routes/controllers as needed; do not
overwrite existing files.

If the model already exists, do nothing.

**Examples**
```bash
flask make:model Comment
flask make:model Comment --crud
flask make:model RecipeComment --crud
```
