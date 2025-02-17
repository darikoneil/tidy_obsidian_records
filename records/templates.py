import json
from functools import partial
from pathlib import Path
from textwrap import indent

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

"""
////////////////////////////////////////////////////////////////////////////////////////
// Records Template Impementation
////////////////////////////////////////////////////////////////////////////////////////
"""


class RecordsTemplate(BaseModel):
    """
    Template dataclass for storing template information
    """

    #: Template name
    key: str
    #: Documents included in the template
    documents: list[str] | None
    #: Images included in the template
    images: list[str] | None
    #: Notebooks included in the template
    notebooks: list[str] | None
    #: Tables included in the template
    tables: list[str] | None


class RecordsTemplateRegistry:
    """
    Registry of templates for generating records in Markdown format to paste into
    Obsidian

    :cvar __registry: Registry of templates
    :cvar __path: Path to the file containing the registry
    :cvar __new_template: Whether a new template has been added to the registry
    """

    #: dict: Registry of templates
    __registry: dict = {}
    #: Path: Path to the file containing the registry
    __path = Path(__file__).parents[2].joinpath("templates", "templates.json")
    #: bool: Whether a new template has been added to the registry
    __new_template: bool = False

    @classmethod
    def _save(cls) -> None:
        """
        Save the registry to a file
        """
        with open(cls.__path, "r+") as file:
            file.write("{\n")
            for idx, (key, template_) in enumerate(cls.__registry.items()):
                serial_template = json.dumps(key)
                serial_template += (
                    f":{template_.model_dump_json(exclude_defaults=True, indent=4)}"
                )
                serial_template = indent(serial_template, " " * 4)
                serial_template += ",\n" if idx < len(cls.__registry) - 1 else "\n"
                file.write(serial_template)
            file.write("}\n")
        cls.__new_template = False

    @classmethod
    def _load(cls) -> None:
        """
        Load the registry from a file
        """
        with open(cls.__path, "r+") as file:
            cls.__registry = {
                key: RecordsTemplate.model_validate(template_)
                for key, template_ in json.load(file).items()
            }

    @classmethod
    def has(cls, key: str) -> bool:
        """
        Check if the registry contains a template with the given key

        :param key: The key of the template
        :returns: True if the registry contains a template with the given key,
         False otherwise
        """
        return key in cls.__registry

    @classmethod
    def get(cls, key: str) -> "RecordsTemplate":
        """
        Get the template with the given key

        :param key: The key of the template
        :returns: Instantiated template
        """
        return cls.__registry[key]

    @classmethod
    def register(cls, template_: "RecordsTemplate") -> None:
        if cls.has(template_.key):
            raise ValueError(f"Template with key {template_.key} already exists")
        cls.__registry[template_.key] = template_
        cls.__new_template = True

    @classmethod
    def __enter__(cls) -> "RecordsTemplateRegistry":
        cls._load()
        return cls()

    @classmethod
    def __exit__(cls, exc_type, exc_val, exc_tb):  # noqa: ANN206, ANN001
        if cls.__new_template:
            cls._save()


"""
////////////////////////////////////////////////////////////////////////////////////////
// Rendering the templated records
////////////////////////////////////////////////////////////////////////////////////////
"""


def _set_html_value_types(rendering: str) -> str:
    lines = rendering.split("<tr>")
    for idx, line in enumerate(lines):
        lowered = line.lower()
        if "time" in lowered:
            lines[idx] = line.replace('type="text"', 'type="time"')
        elif "date" in lowered or "dob" in lowered:
            lines[idx] = line.replace('type="text"', 'type="date"')
    return "<tr>".join(lines)


def render_links(link: Path | None, header_level: int = 5) -> str:
    header = "#" * header_level
    if isinstance(link, list):
        links = "\n"
        for link_ in link:
            links += f"{header} {link_.stem}\n"
            links += f"![[files/{link_.name}]]\n"
        return links
    return f"![[files/{link.name}]]"


def render_table(environment: Environment, records: dict) -> str:
    template = environment.get_template("table.html")
    rendered_table = template.render(records=records)
    return _set_html_value_types(rendered_table)


def render(
    templates_directory: Path,
    key: str,
    documents: list[Path | None],
    images: list[Path | None],
    notebooks: list[str | None],
    tables: list[dict | None],
) -> str:
    environment = Environment(
        loader=FileSystemLoader(str(templates_directory)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = environment.get_template(f"{key}.md")
    render_table_ = partial(render_table, environment=environment)
    return template.render(
        documents=[render_links(document) for document in documents],
        images=[render_links(image) for image in images],
        notebooks=[render_links(notebook) for notebook in notebooks],
        tables=[render_table_(records=table) for table in tables],
    )
