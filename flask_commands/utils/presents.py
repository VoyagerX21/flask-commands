import click

from flask_commands.utils.data_types import (
    ActionResult,
    ControllerResult,
    CrudResult,
    RouteResult,
    ScaffoldStatus
)

def present_output_blocks(
        info_updates: list[str], 
        message_updates: list[str], 
        crud_result: CrudResult | None
) -> list[str]:
    """
    Build the ordered output blocks for controller/model commands.

    This helper centralizes command presentation so both `make:controller` and
    `make:model` can render consistent output.

    Args:
        info_updates (list[str]): Informational updates gathered from flags or
            prompt decisions.
        message_updates (list[str]): Non-CRUD message blocks gathered earlier in
            the command flow, such as controller/model creation messages.
        crud_result (CrudResult | None): Aggregate CRUD result when running a
            CRUD scaffold flow; `None` for non-CRUD command runs.

    Returns:
        list[str]: Ordered terminal-ready blocks to `click.echo(...)`.

    Notes:
    - When `crud_result` is provided, this includes:
      - the controller CRUD summary
      - pre-CRUD message updates
      - CRUD preparation message updates
      - route summary when applicable
      - CRUD wiring summary
      - CRUD warning updates
    - When `crud_result` is `None`, only `info_updates` and `message_updates`
      are rendered.
    """
    blocks: list[str] = []
    
    if info_updates:
        blocks.append(_generated_from_flags(info_updates))
    
    if crud_result is not None:
        blocks.append(
            _controller_crud_summary(crud_result.controller_result))
        blocks.extend(message_updates)
        blocks.extend(crud_result.message_updates)

        if crud_result.route_result is not None:
            blocks.append(
                _crud_route_summary(
                    crud_result.route_result,
                    crud_result.action_results,
                )
            )
        
        blocks.append(_crud_wiring(crud_result.action_results))
        blocks.extend(crud_result.warning_updates)
    else:
        blocks.extend(message_updates)
    
    return blocks

def _controller_crud_summary(controller_result: ControllerResult) -> str:
    """
    Build the consolidated CRUD controller presentation block.

    This formatter renders the controller section used by CRUD scaffold flows.
    It summarizes:
    - whether the controller was created or already existed
    - controller file location
    - controller registration path when created
    - controller methods added during CRUD wiring
    - controller methods that were already present and reused

    Args:
        controller_result (ControllerResult): Aggregate controller result for
            the current CRUD scaffold.

    Returns:
        str: Styled multi-line success summary for the controller section.

    Examples:
        >>> summary = _controller_crud_summary(controller_result)
        >>> "Created Controller Class" in summary
        True
    """
    if controller_result.status == ScaffoldStatus.EXISTS:
        message = (
            click.style("✅ Success: Reused Existing Controller Class\n", fg="green", bold=True) +
            click.style(
                f"    - Controller {controller_result.controller_name} already existed\n",
                fg="green",
            ) +
            click.style(
                f"    - Existing controller located at {controller_result.controller_file_path}\n",
                fg="green",
            )
        )
    else:
        message = (
            click.style("✅ Success: Created Controller Class\n", fg="green", bold=True) +
            click.style(
                f"    - Created a new controller called {controller_result.controller_name}\n",
                fg="green",
            ) +
            click.style(
                f"    - New controller located at {controller_result.controller_file_path}\n",
                fg="green",
            )
        )

    if controller_result.registration_file_path and controller_result.status != ScaffoldStatus.EXISTS:
        message += click.style(
            f"    - Registered {controller_result.controller_name} at "
            f"{controller_result.registration_file_path}\n",
            fg="green",
        )

    if controller_result.methods_added:
        message += click.style(
            f"    - Added controller methods: {', '.join(controller_result.methods_added)}\n",
            fg="green",
        )
    
    if controller_result.methods_existing:
        message += click.style(
            f"    - Controller methods already present: {', '.join(controller_result.methods_existing)}\n",
            fg="green",
        )

    return message

def _crud_route_summary(
    route_result: RouteResult,
    action_results: list[ActionResult],
) -> str:
    """
    Build the consolidated CRUD route-directory presentation block.

    This formatter renders either:
    - `Created New Route Directory`
    - `Updated Existing Route Directory`

    It also summarizes:
    - route package files created during this scaffold
    - blueprint registration target
    - route functions added across the CRUD action set

    Args:
        route_result (RouteResult): Route-directory level result for the CRUD scaffold.
        action_results (list[ActionResult]): All action-level results generated
            for the CRUD scaffold.

    Returns:
        str: Styled multi-line success summary for the route section.

    Examples:
        >>> summary = _crud_route_summary(route_result, action_results)
        >>> "Added route functions" in summary
        True

    Notes:
    - File creation and blueprint registration lines are only rendered when the
      route directory was created during the current scaffold run.
    """
    added_route_functions = [
        action_result.action
        for action_result in action_results
        if action_result.route_status == ScaffoldStatus.ADDED
    ]

    heading = (
        "✅ Success: Created New Route Directory\n"
        if route_result.directory_status == ScaffoldStatus.ADDED
        else "✅ Success: Updated Existing Route Directory\n"
    )

    message = click.style(heading, fg="green", bold=True)

    if route_result.directory_status == ScaffoldStatus.ADDED:
        if route_result.route_init_path:
            message += click.style(
                f"    - Created __init__.py at {route_result.route_init_path}\n",
                fg="green",
            )
        if route_result.route_file_path:
            message += click.style(
                f"    - Created routes.py at {route_result.route_file_path}\n",
                fg="green",
            )
        if route_result.blueprint_name and route_result.blueprint_registration_file_path:
            message += click.style(
                f"    - Registered the new route directory as {route_result.blueprint_name} "
                f"at {route_result.blueprint_registration_file_path}\n",
                fg="green",
            )

    if added_route_functions:
        message += click.style(
            f"    - Added route functions: {', '.join(added_route_functions)}\n",
            fg="green",
        )

    return message

def _crud_wiring(action_results: list[ActionResult]) -> str:
    """
    Build the consolidated CRUD action wiring presentation block.

    This formatter renders the per-action summary rows for the RESTful action set.
    For each action it may include:
    - action name and HTTP method
    - generated view file path for GET actions
    - route visit example for GET actions
    - `url_for(...)` reference example for successfully added routes

    Args:
        action_results (list[ActionResult]): Action-level results for the CRUD scaffold.

    Returns:
        str: Styled multi-line success summary for the CRUD wiring section.

    Examples:
        >>> summary = _crud_wiring(action_results)
        >>> "Generated CRUD Wiring" in summary
        True

    Notes:
    - POST actions do not render a “Visit the new route at ...” line.
    - View file lines are only rendered for GET actions whose view status is
      `ADDED`.
    """
    message = click.style("✅ Success: Generated CRUD Wiring\n", fg="green", bold=True)

    for action_result in action_results:
        message += click.style(
            f"    - {action_result.action} ({action_result.http_method})\n",
            fg="green",
        )

        if (
            action_result.http_method == "GET"
            and action_result.view_status == ScaffoldStatus.ADDED
            and action_result.view_file_path
        ):
            message += click.style(
                f"      Added view file at {action_result.view_file_path}\n",
                fg="green",
            )

        if action_result.route_status == ScaffoldStatus.ADDED:
            if action_result.http_method == "GET":
                message += click.style(
                    f"      {action_result.visit_example}\n",
                    fg="green",
                )

            if action_result.url_for_example:
                message += click.style(
                    f"      {action_result.url_for_example}\n",
                    fg="green",
                )

    return message

def _generated_from_flags(info_updates: list[str]) -> str:
    """
    Build the informational output block for flag-driven generation choices.

    This private helper formats the cyan summary shown when CLI flags such as
    `--flat` or `--nest` influenced how models were generated.

    Args:
        info_updates (list[str]): Human-readable informational lines collected
            during command setup.

    Returns:
        str: Styled multi-line info block ready for terminal output.

    Examples:
        >>> block = _generated_from_flags(
        ...     ["Using --flat. Generated model(s): UserComment"]
        ... )
        >>> "Generated From Flags" in block
        True

    Notes:
    - Each item in `info_updates` is rendered as its own indented bullet line.
    - When no updates exist, callers should skip invoking this helper.
    """
    return (
        click.style("💡 Info: Generated From Flags\n", fg="cyan", bold=True) +
        "".join(
            click.style(f"    - {update}\n", fg="cyan")
            for update in info_updates
        )
    )

