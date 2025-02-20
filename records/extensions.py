from jinja2 import nodes
from jinja2.ext import Extension
from sub_code.records.misc import select_file


class CallFunctionExtension(Extension):
    tags = {"call_function"}

    __registry = {}

    @classmethod
    def register(cls, name):
        def wrapper(func):
            cls.__registry[name] = func.__name__
            return func

        return wrapper

    @classmethod
    def get(cls, name: str):
        return cls.__registry.get(name)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        target = parser.parse_assign_target()  # Parse the variable to set
        parser.stream.expect("assign")  # Expect the '=' token
        args = [parser.parse_expression()]  # Parse the function name
        return nodes.Assign(target, self.call_method("_render", args)).set_lineno(
            lineno
        )

    # noinspection PyMethodMayBeStatic
    def _render(self, func_name):
        func = self.get(func_name)
        if func:
            return func()
        return ""


@CallFunctionExtension.register
def get_imaging_meta_file():
    return select_file(title="Select the imaging metadata file")


@CallFunctionExtension.register
def get_landmark_meta_file():
    return select_file(title="Select the landmark metadata file")


def add_extensions(environment):
    """
    Add custom extensions to the Jinja2 environment

    :param environment: The Jinja2 environment
    :returns: The Jinja2 environment with custom extensions added
    """
    environment.add_extension(CallFunctionExtension)
    return environment
