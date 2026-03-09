from dataclasses import dataclass, field
from enum import Enum


class ScaffoldStatus(Enum):
    ADDED = "added"         # New Object Added
    EXISTS = "exists"       # Object already exists
    SKIPPED = "skipped"
    WARNING = "warning"
    ERROR = "error"         # Unexpected Failure

@dataclass
class RouteResult:
    directory_status: ScaffoldStatus
    is_successful: bool
    route_init_path: str | None = None
    route_file_path: str | None = None
    blueprint_name: str | None = None
    blueprint_registration_file_path: str | None = None

# This was CrudActionReference
@dataclass(frozen=True)
class ActionResult:
    action: str
    http_method: str
    route_name: str
    url_for_example: str
    is_successful: bool
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
