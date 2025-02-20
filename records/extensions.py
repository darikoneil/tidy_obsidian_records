from pathlib import Path
from typing import Any, Callable

from jinja2 import nodes
from jinja2.environment import Environment
from jinja2.ext import Extension

from sub_code.records.misc import select_file


class CallFunctionExtension(Extension):
    tags = {"call_function"}

    __registry = {}

    @classmethod
    def register(cls, alias: str | None = None):  # noqa: ANN001, ANN201, ANN206
        def wrapper(func):  # noqa: ANN001, ANN201, ANN206
            cls.__registry[alias or func.__name__] = func
            return func

        return wrapper

    @classmethod
    def get(cls, name: str) -> Callable:
        return cls.__registry.get(name)

    def parse(self, parser: Any) -> Any:
        lineno = next(parser.stream).lineno
        target = parser.parse_assign_target()  # Parse the variable to set
        parser.stream.expect("assign")  # Expect the '=' token
        args = [parser.parse_expression()]  # Parse the function name
        return nodes.Assign(target, self.call_method("_render", args)).set_lineno(
            lineno
        )

    # noinspection PyMethodMayBeStatic
    def _render(self, func_name: str) -> Any:
        func = self.get(func_name)
        if func:
            return func()
        return ""


@CallFunctionExtension.register()
def get_imaging_meta_file() -> Path:
    return select_file(title="Select the imaging metadata file")


@CallFunctionExtension.register()
def get_landmark_meta_file() -> Path:
    return select_file(title="Select the landmark metadata file")


@CallFunctionExtension.register()
def get_num_planes(planes: list[str]) -> int:
    return len(planes)


def add_extensions(environment: Environment) -> Environment:
    """
    Add custom extensions to the Jinja2 environment

    :param environment: The Jinja2 environment
    :returns: The Jinja2 environment with custom extensions added
    """
    environment.add_extension(CallFunctionExtension)
    return environment
