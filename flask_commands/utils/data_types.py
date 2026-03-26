from dataclasses import dataclass, field
from enum import Enum


class ScaffoldStatus(Enum):
    """
    Enumerate scaffold outcome states used across controller, model, view, and route generation.

    This enum provides a shared status language for structured scaffold results.
    It is used to describe whether a scaffold step created something new,
    encountered an existing artifact, skipped a step intentionally, produced a
    recoverable warning, or failed with an error.

    Members:
        ADDED: A new artifact or code block was created successfully.
        EXISTS: The target artifact already existed and was left unchanged.
        SKIPPED: The step was intentionally not applicable for the current flow.
        WARNING: The step encountered a recoverable issue and may have produced
            only a partial result.
        ERROR: The step failed and did not complete successfully.

    Examples:
        >>> ScaffoldStatus.ADDED.value
        'added'
        >>> ScaffoldStatus.SKIPPED.value
        'skipped'

    Notes:
        `is_successful` flags on the result dataclasses are the authoritative
        success indicator for command flow. This enum describes scaffold state,
        not command-control behavior by itself.
    """
    ADDED = "added"
    EXISTS = "exists"
    SKIPPED = "skipped"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class RouteResult:
    """
    Store route-directory level scaffold results for a generated resource.

    This dataclass describes work that happened at the route package level,
    rather than at the individual action level. It is used when a route
    directory is created and registered, and may be absent when CRUD wiring only
    appended methods to an already existing route package.

    Attributes:
        directory_status (ScaffoldStatus): Outcome of the route-directory level
            scaffold step.
        is_successful (bool): Whether the route-directory operation completed
            successfully.
        route_init_path (str | None): Path to the generated or target
            `__init__.py` for the route package.
        route_file_path (str | None): Path to the generated or target
            `routes.py` file.
        blueprint_name (str | None): Generated blueprint alias used during
            registration.
        blueprint_registration_file_path (str | None): File where the blueprint
            was or would be registered.

    Examples:
        >>> route_result = RouteResult(
        ...     directory_status=ScaffoldStatus.ADDED,
        ...     is_successful=True,
        ...     route_init_path='app/routes/posts/__init__.py',
        ...     route_file_path='app/routes/posts/routes.py',
        ...     blueprint_name='posts_blueprint',
        ...     blueprint_registration_file_path='app/__init__.py',
        ... )
        >>> route_result.blueprint_name
        'posts_blueprint'

    Notes:
        This result is intentionally resource-level. Individual route actions are
        represented by `ActionResult`.
    """
    directory_status: ScaffoldStatus
    is_successful: bool
    route_init_path: str | None = None
    route_file_path: str | None = None
    blueprint_name: str | None = None
    blueprint_registration_file_path: str | None = None

@dataclass(frozen=True)
class ActionResult:
    """
    Store the aggregate scaffold result for one action within a resource flow.

    This dataclass represents the full action-level outcome after view,
    controller, and route wiring have been considered together. It is the
    primary presentation object used by CRUD summaries.

    Attributes:
        action (str): Action name such as `index`, `show`, `create`, `store`,
            `edit`, `update`, or `destroy`.
        http_method (str): HTTP method associated with the action.
        route_name (str): Flask route rule for the action.
        url_for_example (str): Presentation string showing how to reference the
            route with `url_for(...)`.
        is_successful (bool): Whether the full action wiring completed
            successfully.
        visit_example (str | None): Presentation string showing how to visit the
            route in a browser for GET actions. `None` when not applicable.
        view_file_path (str | None): Path to the generated view template for GET
            actions when applicable.
        view_status (ScaffoldStatus): Outcome of the view scaffold step.
        route_status (ScaffoldStatus): Outcome of the route scaffold step.

    Examples:
        >>> action_result = ActionResult(
        ...     action='show',
        ...     http_method='GET',
        ...     route_name='/posts/<int:post_id>',
        ...     url_for_example=\"Reference this route with url_for('posts.show', post_id=1)\",
        ...     is_successful=True,
        ...     visit_example='Visit the new route at /posts/1',
        ...     view_file_path='app/templates/posts/show.html',
        ...     view_status=ScaffoldStatus.ADDED,
        ...     route_status=ScaffoldStatus.ADDED,
        ... )
        >>> action_result.http_method
        'GET'

        >>> post_action = ActionResult(
        ...     action='store',
        ...     http_method='POST',
        ...     route_name='/posts',
        ...     url_for_example=\"Reference this route with url_for('posts.store')\",
        ...     is_successful=True,
        ... )
        >>> post_action.visit_example is None
        True

    Notes:
        This is the aggregate action result used by wiring and presentation.
        Route helper functions may also produce action-level data, but the final
        `ActionResult` is the source of truth for command output.
    """
    action: str
    http_method: str
    route_name: str
    url_for_example: str
    is_successful: bool
    visit_example: str | None = None
    view_file_path: str | None = None
    view_status: ScaffoldStatus = ScaffoldStatus.SKIPPED
    route_status: ScaffoldStatus = ScaffoldStatus.SKIPPED

@dataclass
class ControllerResult:
    """
    Store scaffold outcomes for controller file creation or method updates.

    This dataclass captures controller-level metadata returned by controller
    scaffold helpers and normalization utilities, including whether any methods
    were added during the operation.

    Attributes:
        controller_name (str): Controller class name, such as
            `"PostController"`.
        controller_file_path (str): Path to the controller file under
            `app/controllers/`.
        status (ScaffoldStatus): Outcome of the controller scaffold step.
        is_successful (bool): Whether the controller operation completed
            successfully.
        registration_file_path (str | None): File path where registration/import
            updates were applied when relevant.
        methods_added (list[str]): Controller methods added during this run.
        methods_existing (list[str]): Controller methods that already existed and
            were intentionally reused without change during this run.
    Examples:
        >>> controller_result = ControllerResult(
        ...     controller_name="PostController",
        ...     controller_file_path="app/controllers/post_controller.py",
        ...     status=ScaffoldStatus.ADDED,
        ...     is_successful=True,
        ...     registration_file_path="app/controllers/__init__.py",
        ...     methods_added=["index", "show"],
        ...     methods_existing=["create", "store"]
        ... )
        >>> controller_result.methods_added
        ['index', 'show']

    Notes:
        `is_successful` commonly reflects whether `status` is `ADDED` in
        normalized helper output.
    """
    controller_name: str
    controller_file_path: str
    status: ScaffoldStatus
    is_successful: bool
    registration_file_path: str | None = None
    methods_added: list[str] = field(default_factory=list)
    methods_existing: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class CreatedModel:
    """
    Store the scaffold result for one model generation attempt.

    This dataclass represents the per-model result returned from model creation
    flows, including both filesystem output and registration context.

    Attributes:
        model_name (str): PascalCase model class name, such as `"Post"`.
        model_file_path (str): Path to the model file under `app/models/`.
        status (ScaffoldStatus): Outcome of the model scaffold step.
        is_successful (bool): Whether model creation and registration completed
            successfully.
        registration_file_path (str | None): Path to registration target file,
            typically `app/models/__init__.py`.

    Examples:
        >>> created_model = CreatedModel(
        ...     model_name="Post",
        ...     model_file_path="app/models/post.py",
        ...     status=ScaffoldStatus.ADDED,
        ...     is_successful=True,
        ...     registration_file_path="app/models/__init__.py",
        ... )
        >>> created_model.status.value
        'added'

    Notes:
        `status` may be `EXISTS`, `WARNING`, or `ERROR` when file creation or
        registration is partial/unsuccessful.
    """
    model_name: str
    model_file_path: str
    status: ScaffoldStatus
    is_successful: bool
    registration_file_path: str | None = None

@dataclass
class ModelResult:
    """
    Aggregate model scaffold outcomes for a command flow.

    This dataclass tracks overall model-stage success and the individual
    `CreatedModel` entries collected during execution.

    Attributes:
        is_successful (bool): Whether the aggregate model stage succeeded.
        created_models (list[CreatedModel]): Per-model scaffold results.

    Examples:
        >>> model_result = ModelResult(
        ...     is_successful=True,
        ...     created_models=[
        ...         CreatedModel(
        ...             model_name="Post",
        ...             model_file_path="app/models/post.py",
        ...             status=ScaffoldStatus.ADDED,
        ...             is_successful=True,
        ...             registration_file_path="app/models/__init__.py",
        ...         )
        ...     ],
        ... )
        >>> len(model_result.created_models)
        1

    Notes:
        This result is often embedded in `CrudResult` to keep model outcomes
        alongside controller/route/action outcomes.
    """
    is_successful: bool
    created_models: list[CreatedModel] = field(default_factory=list)

@dataclass
class CrudResult:
    """
    Store aggregate structured results for a full CRUD scaffold operation.

    This dataclass combines:
    - controller scaffold state
    - model scaffold state
    - route-directory state when a route package was created
    - action-level results for the RESTful action set
    - command-level message blocks collected during CRUD preparation/wiring
    - the overall success state for the CRUD flow 
    This wasy presentation helpers can render one consolidated CRUD summary.

    Attributes:
        controller_result (ControllerResult): Aggregate controller scaffold result.
        model_result (ModelResult): Aggregate model scaffold result.
        is_successful (bool): Whether the full CRUD flow completed successfully.
        route_result (RouteResult | None): Route-directory result when a route
            package was created/registered; `None` when only existing route files
            were updated.
        action_results (list[ActionResult]): Action-level results for generated
            CRUD actions.
        message_updates (list[str]): Extra message blocks produced during CRUD
            preparation, such as fallback model creation.
        warning_updates (list[str]): Warning/error messages collected during
            CRUD wiring.

    Examples:
        >>> crud_result = CrudResult(
        ...     controller_result=controller_result,
        ...     model_result=model_result,
        ...     is_successful=True,
        ...     route_result=route_result,
        ...     action_results=[action_result],
        ...     message_updates=[],
        ...     warning_updates=[],
        ... )
        >>> crud_result.is_successful
        True

    Notes:
        `action_results` is the primary source for per-action output in CRUD
        summaries.
        `message_updates` and `warning_updates` carry command-level presentation
        context gathered during the full CRUD flow.
    """
    controller_result: ControllerResult
    model_result: ModelResult
    is_successful: bool
    route_result: RouteResult | None = None
    action_results: list[ActionResult] = field(default_factory=list)
    message_updates: list[str] = field(default_factory=list)
    warning_updates: list[str] = field(default_factory=list)

@dataclass
class WiringResult:
    """
    Store one action's wiring outcome across view, controller, and route steps.

    This dataclass is returned by action-level wiring orchestration and separates
    execution data from presentation strings.

    Attributes:
        action_result (ActionResult): Aggregate action-level result.
        controller_result (ControllerResult | None): Controller result when
            controller wiring ran.
        route_result (RouteResult | None): Route-directory result when route
            package creation/registration occurred.
        success_messages (list[str]): Success updates for this action.
        warning_messages (list[str]): Warning/error updates for this action.

    Examples:
        >>> wiring_result = WiringResult(
        ...     action_result=action_result,
        ...     controller_result=controller_result,
        ...     route_result=None,
        ...     success_messages=["Created route"],
        ...     warning_messages=[],
        ... )
        >>> wiring_result.action_result.is_successful
        True

    Notes:
        `route_result` is intentionally optional because many actions append to
        existing route packages rather than creating new ones.
    """
    action_result: ActionResult
    controller_result: ControllerResult | None
    route_result: RouteResult | None
    success_messages: list[str] = field(default_factory=list)
    warning_messages: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class RouteSpec:
    """
    Capture immutable route analysis derived from dotted CLI input.

    This dataclass is generated before prompt decisions and route writes. It
    stores both parsed path/action details and model-matching metadata used for
    route-name generation and optional prompt planning.

    Attributes:
        dotted_path_with_action (str): Original dotted input, e.g.
            `"posts.show"` or `"admin.posts.index"`.
        relative_path (str): Slash-delimited path extracted before action.
        action (str): Action extracted from input.
        is_restful (bool): Whether action is one of the recognized RESTful
            actions.
        relative_path_segments (tuple[str]): Split path segments from
            `relative_path`.
        relative_path_segment_models (tuple[str]): Segments recognized as model
            segments.
        registered_models (tuple[str]): Registered model names (PascalCase).
        registered_snake_models (tuple[str]): Registered model names converted to
            snake_case.
        generated_route_name (str): Route rule generated from this analysis.

    Examples:
        >>> route_spec = RouteSpec(
        ...     dotted_path_with_action="posts.show",
        ...     relative_path="posts",
        ...     action="show",
        ...     is_restful=True,
        ...     relative_path_segments=("posts",),
        ...     relative_path_segment_models=("posts",),
        ...     registered_models=("Post",),
        ...     registered_snake_models=("post",),
        ...     generated_route_name="/posts/<int:post_id>",
        ... )
        >>> route_spec.is_restful
        True

    Notes:
        This object is analysis-only; it does not imply any filesystem writes.
    """
    dotted_path_with_action: str
    relative_path: str
    action: str
    is_restful: bool
    relative_path_segments: tuple[str]
    relative_path_segment_models: tuple[str]
    registered_models: tuple[str]
    registered_snake_models: tuple[str]
    generated_route_name: str

@dataclass(frozen=True)
class MissingModelPrompt:
    """
    Store a prompt payload suggesting a missing model segment.

    This dataclass is used when RESTful route analysis detects a last path
    segment that does not map to a known model.

    Attributes:
        segment (str): Route segment that appears to be missing model treatment.
        model_name (str): Suggested PascalCase model name derived from segment.

    Examples:
        >>> missing_prompt = MissingModelPrompt(
        ...     segment="comments",
        ...     model_name="Comment",
        ... )
        >>> missing_prompt.model_name
        'Comment'

    Notes:
        This payload is optional and appears only when prompt planning detects a
        likely missing model case.
    """
    segment: str
    model_name: str

@dataclass(frozen=True)
class RouteStructurePrompt:
    """
    Store accepted vs declined route alternatives for interactive prompts.

    Attributes:
        accepted_route (str): Route rule suggested when inferred structure is
            accepted.
        declined_route (str): Route rule used when inferred structure is
            declined.

    Examples:
        >>> structure_prompt = RouteStructurePrompt(
        ...     accepted_route="/posts/<int:post_id>/comments/<int:comment_id>",
        ...     declined_route="/posts/<int:post_id>/comments",
        ... )
        >>> structure_prompt.declined_route
        '/posts/<int:post_id>/comments'

    Notes:
        This dataclass is presentation-oriented and paired with
        `MissingModelPrompt` in `PromptPlan`.
    """
    accepted_route: str
    declined_route: str

@dataclass(frozen=True)
class PromptPlan:
    """
    Bundle optional prompt payloads used during route planning.

    This dataclass allows route analysis to return a single structured plan
    indicating whether missing-model and/or route-structure prompts should be
    shown.

    Attributes:
        missing_model (MissingModelPrompt | None): Missing-model prompt payload
            when applicable.
        route_structure (RouteStructurePrompt | None): Route-structure prompt
            payload when applicable.

    Examples:
        >>> prompt_plan = PromptPlan(
        ...     missing_model=MissingModelPrompt(segment="comments", model_name="Comment"),
        ...     route_structure=RouteStructurePrompt(
        ...         accepted_route="/posts/<int:post_id>/comments/<int:comment_id>",
        ...         declined_route="/posts/<int:post_id>/comments",
        ...     ),
        ... )
        >>> prompt_plan.missing_model is not None
        True

    Notes:
        An empty `PromptPlan()` means no prompts are needed for the analyzed
        route input.
    """
    missing_model: MissingModelPrompt | None = None
    route_structure: RouteStructurePrompt | None = None
