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

# This was CrudActionReference
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
    controller_name: str
    controller_file_path: str
    status: ScaffoldStatus
    is_successful: bool
    registration_file_path: str | None = None
    methods_added: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class CreatedModel:
    model_name: str
    model_file_path: str
    status: ScaffoldStatus
    is_successful: bool
    registration_file_path: str | None = None

@dataclass
class ModelResult:
    is_successful: bool
    created_models: list[CreatedModel] = field(default_factory=list)

@dataclass
class CrudResult:
    controller_result: ControllerResult
    model_result: ModelResult
    route_result: RouteResult | None = None
    action_results: list[ActionResult] = field(default_factory=list)

@dataclass
class WiringResult:
    action_result: ActionResult
    controller_result: ControllerResult | None
    route_result: RouteResult | None
    success_messages: list[str] = field(default_factory=list)
    warning_messages: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RouteSpec:
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
    segment: str
    model_name: str

@dataclass(frozen=True)
class RouteStructurePrompt:
    accepted_route: str
    declined_route: str

@dataclass(frozen=True)
class PromptPlan:
    missing_model: MissingModelPrompt | None = None
    route_structure: RouteStructurePrompt | None = None
