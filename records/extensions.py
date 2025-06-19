from collections.abc import Callable
from pathlib import Path
from typing import Any

from jinja2 import nodes
from jinja2.environment import Environment
from jinja2.ext import Extension

from darik_code.records.misc import select_file


class CallFunctionExtension(Extension):
    """
    Jinja2 extension to allow calling registered Python functions from templates.

    Functions can be registered with an alias and called from within Jinja2 templates
    using the ``call_function`` tag.
    """

    tags = {"call_function"}

    __registry = {}

    @classmethod
    def register(cls, alias: str | None = None):
        """
        Decorator to register a function for use in Jinja2 templates.

        :param alias: Optional alias for the function. If not provided, uses the function's name.
        :returns: The decorator for function registration.
        """
        def wrapper(func):
            cls.__registry[alias or func.__name__] = func
            return func

        return wrapper

    @classmethod
    def get(cls, name: str) -> Callable:
        """
        Retrieve a registered function by name or alias.

        :param name: The name or alias of the registered function.
        :returns: The registered function or None if not found.
        """
        return cls.__registry.get(name)

    def parse(self, parser: Any) -> Any:
        """
        Parse the custom ``call_function`` tag in a Jinja2 template.

        :param parser: The Jinja2 parser.
        :returns: The parsed node for assignment.
        """
        lineno = next(parser.stream).lineno
        target = parser.parse_assign_target()  # Parse the variable to set
        parser.stream.expect("assign")  # Expect the '=' token
        args = [parser.parse_expression()]  # Parse the function name
        return nodes.Assign(target, self.call_method("_render", args)).set_lineno(
            lineno
        )

    def _render(self, func_name: str) -> Any:
        """
        Render the result of the registered function.

        :param func_name: The name or alias of the registered function.
        :returns: The result of the function call, or an empty string if not found.
        """
        func = self.get(func_name)
        if func:
            return func()
        return ""


@CallFunctionExtension.register()
def get_imaging_meta_file() -> Path:
    """
    Prompt the user to select the imaging metadata file.

    :returns: The selected file path.
    """
    return select_file(title="Select the imaging metadata file")


@CallFunctionExtension.register()
def get_landmark_meta_file() -> Path:
    """
    Prompt the user to select the landmark metadata file.

    :returns: The selected file path.
    """
    return select_file(title="Select the landmark metadata file")


@CallFunctionExtension.register()
def get_num_planes(planes: list[str]) -> int:
    """
    Get the number of imaging planes.

    :param planes: List of plane identifiers.
    :returns: The number of planes.
    """
    return len(planes)


def add_extensions(environment: Environment) -> Environment:
    """
    Add custom extensions to the Jinja2 environment.

    :param environment: The Jinja2 environment.
    :returns: The Jinja2 environment with custom extensions added.
    """
    environment.add_extension(CallFunctionExtension)
    return environment
