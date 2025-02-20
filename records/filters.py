from pathlib import Path

from jinja2 import Environment

from sub_code.imaging.meta import load_plane_metadata
from sub_code.records.misc import select_file


class FilterRegistry:
    __registry = {}

    @classmethod
    def register(cls, name):
        def wrapper(func):
            cls.__registry[name] = func
            return func

        return wrapper

    @classmethod
    def get_filters(cls):
        return cls.__registry.items()


def _set_html_value_types(rendering: str) -> str:
    lines = rendering.split("<tr>")
    for idx, line in enumerate(lines):
        lowered = line.lower()
        if "time" in lowered:
            lines[idx] = line.replace('type="text"', 'type="time"')
        elif "date" in lowered or "dob" in lowered:
            lines[idx] = line.replace('type="text"', 'type="date"')
    return "<tr>".join(lines)


@FilterRegistry.register("render_table")
def render_table(records: dict, environment: Environment) -> str:
    template = environment.get_template("table.html")
    rendered_table = template.render(records=records)
    return _set_html_value_types(rendered_table)


@FilterRegistry.register("render_links")
def render_links(link: Path | list | None, header_level: int = 5) -> str:
    if isinstance(link, list):
        header = "#" * header_level
        links = "\n"
        for link_ in link:
            links += f"{header} {link_.stem}\n"
            links += f"![[files/{link_.name}]]\n"
        return links
    else:
        return f"![[files/{link.name}]]"


@FilterRegistry.register("special_multiplane_slm")
def special_multiplane_slm(implementation, environment) -> str:
    metadata_file = select_file(title="Select the multiplane slm metadata file")
    plane_metadata = load_plane_metadata(metadata_file)
    filled_tables = [
        implementation(metadata_file=metadata_file, **metadata).model_dump(
            by_alias=True
        )
        for metadata in plane_metadata.values()
    ]
    rendered_tables = [render_table(table, environment) for table in filled_tables]
    return "\n".join(rendered_tables)


@FilterRegistry.register("special_imaging_fov")
def special_imaging_fov(implementation, metadata_file, environment) -> str:
    filled_table = implementation(metadata_file=metadata_file).model_dump(by_alias=True)
    return render_table(filled_table, environment)


@FilterRegistry.register("special_imaging_roadmap")
def special_imaging_roadmap(
    implementation, imaging_metadata_file, landmark_metadata_file, environment
) -> str:
    filled_table = implementation(
        imaging_metadata_file=imaging_metadata_file,
        landmark_metadata_file=landmark_metadata_file,
    ).model_dump(by_alias=True)
    return render_table(filled_table, environment)


@FilterRegistry.register("split_to_list")
def split_to_list(string: str) -> list:
    return string.split("\n")


def add_filters(environment: Environment) -> Environment:
    """
    Add custom filters to the Jinja2 environment

    :param environment: The Jinja2 environment
    :returns: The Jinja2 environment with custom filters added
    """
    for key, func in FilterRegistry.get_filters():
        environment.filters[key] = func
    return environment
