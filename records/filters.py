import re
from collections.abc import Callable, ItemsView
from pathlib import Path

from jinja2 import Environment

from darik_code.records.misc import select_file
from darik_code.slm.patterns import load_imaging_planes

"""
Called filters by jinja convention, really like functions that operate on a value.
Extensions in the extensions module operate on a value adn return something new.
"""


class FilterRegistry:
    """
    Registry for custom Jinja2 filters.

    Allows registration and retrieval of filter functions by alias.
    """
    __registry = {}

    @classmethod
    def register(cls, alias: str | None = None):
        """
        Decorator to register a filter function.

        :param alias: Optional alias for the filter. If not provided, uses the function's name.
        :returns: The decorator for filter registration.
        """
        def wrapper(func):
            cls.__registry[alias or func.__name__] = func
            return func

        return wrapper

    @classmethod
    def get_filters(cls) -> ItemsView[str, Callable]:
        """
        Retrieve all registered filters.

        :returns: ItemsView of filter aliases and functions.
        """
        return cls.__registry.items()


def _set_html_value_types(rendering: str) -> str:
    """
    Set HTML input types for date and time fields in rendered tables.

    :param rendering: The HTML string to process.
    :returns: The HTML string with input types set.
    """
    lines = rendering.split("<tr>")
    for idx, line in enumerate(lines):
        lowered = line.lower()
        if "time" in lowered:
            lines[idx] = line.replace('type="text"', 'type="time"')
        elif "date" in lowered or "dob" in lowered:
            lines[idx] = line.replace('type="text"', 'type="date"')
    return "<tr>".join(lines)


@FilterRegistry.register()
def render_table(records: dict, environment: Environment) -> str:
    """
    Render a records table using a Jinja2 template.

    :param records: The records data to render.
    :param environment: The Jinja2 environment.
    :returns: The rendered HTML table as a string.
    """
    template = environment.get_template("table.html")
    rendered_table = template.render(records=records)
    return _set_html_value_types(rendered_table)


@FilterRegistry.register()
def render_links(link: str | Path | list | None, header_level: int = 5) -> str:
    """
    Render links or images for Markdown/Obsidian.

    :param link: The link(s) to render.
    :param header_level: The Markdown header level for multiple links.
    :returns: The rendered Markdown string.
    """
    if isinstance(link, str):
        link = Path(link)
    if isinstance(link, list):
        header = "#" * header_level
        links = "\n"
        for link_ in link:
            links += f"{header} {link_.stem}\n"
            links += f"![[files/{link_.name}]]\n"
        return links
    return f"![[files/{link.name}]]"


@FilterRegistry.register()
def special_multiplane_slm(implementation, environment) -> list[str]:
    """
    Render multiplane SLM tables using metadata file selection.

    :param implementation: The table implementation class.
    :param environment: The Jinja2 environment.
    :returns: List of rendered tables as strings.
    """
    metadata_file = select_file(title="Select the multiplane slm metadata file")
    plane_metadata = load_imaging_planes(metadata_file)
    filled_tables = [
        implementation(**metadata.model_dump()).model_dump(by_alias=True)
        for metadata in plane_metadata
    ]
    rendered_tables = [render_table(table, environment) for table in filled_tables]
    return rendered_tables


@FilterRegistry.register()
def special_imaging_fov(implementation, metadata_file, environment) -> str:
    """
    Render an imaging FOV table using the provided metadata file.

    :param implementation: The table implementation class.
    :param metadata_file: The metadata file path.
    :param environment: The Jinja2 environment.
    :returns: The rendered table as a string.
    """
    filled_table = implementation(metadata_file=metadata_file).model_dump(by_alias=True)
    return render_table(filled_table, environment)


@FilterRegistry.register()
def special_imaging_roadmap(
    implementation, imaging_metadata_file, landmark_metadata_file, environment
) -> str:
    """
    Render an imaging roadmap table using provided metadata files.

    :param implementation: The table implementation class.
    :param imaging_metadata_file: The imaging metadata file path.
    :param landmark_metadata_file: The landmark metadata file path.
    :param environment: The Jinja2 environment.
    :returns: The rendered table as a string.
    """
    filled_table = implementation(
        imaging_metadata_file=imaging_metadata_file,
        landmark_metadata_file=landmark_metadata_file,
    ).model_dump(by_alias=True)
    return render_table(filled_table, environment)


@FilterRegistry.register()
def debug(value) -> None:
    """
    Print the value for debugging purposes.

    :param value: The value to print.
    """
    print(f"{value=}")


@FilterRegistry.register()
def split_rendered_images(images: str) -> list[str]:
    """
    Split a rendered images string into a list of Markdown image links.

    :param images: The rendered images string.
    :returns: List of Markdown image links.
    """
    return [f"![[{image}]]" for image in re.findall(r"!\[\[(.*?)]]", images)]


def add_filters(environment: Environment) -> Environment:
    """
    Add custom filters to the Jinja2 environment.

    :param environment: The Jinja2 environment.
    :returns: The Jinja2 environment with custom filters added.
    """
    for key, func in FilterRegistry.get_filters():
        environment.filters[key] = func
    return environment
