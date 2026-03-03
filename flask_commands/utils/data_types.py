from dataclasses import dataclass, field
from enum import Enum


class ScaffoldStatus(Enum):
    ADDED = "added"
    EXISTS = "exists"
    SKIPPED = "skipped"
    WARNING = "warning"
    ERROR = "error"

@dataclass(frozen=True)
class CreatedModel:
    model_name: str
    model_file_path: str
    status: ScaffoldStatus

# This was CrudActionReference
@dataclass(frozen=True)
class ActionResult:
    action: str
    http_method: str
    route_path: str
    url_for_example: str
    view_file_path: str | None = None
    view_status: ScaffoldStatus | None = None
    route_status: ScaffoldStatus = ScaffoldStatus.ADDED

@dataclass
class ControllerResult:
    controller_name: str
    registration_file_path: str
    controller_file_path: str
    status: ScaffoldStatus
    methods_added: list[str] = field(default_factory=list)

@dataclass
class ModelResult:
    generated_model_names: list[str] = field(default_factory=list)
    registration_file_path: str | None = None
    created_models: list[CreatedModel] = field(default_factory=list)

@dataclass
class RouteResult:
    directory_status: ScaffoldStatus
    route_init_path: str
    route_file_path: str
    blueprint_name: str
    blueprint_registration_file_path: str
    functions_added: list[str] = field(default_factory=list)

@dataclass
class CrudResourceResult:
    controller: ControllerResult
    model: ModelResult
    route: RouteResult
    actions: list[ActionResult] = field(default_factory=list)


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
