import json
from pathlib import Path
from textwrap import indent
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from darik_code.records.extensions import add_extensions
from darik_code.records.filters import add_filters
from darik_code.records.misc import Placeholders

if TYPE_CHECKING:
    from darik_code.records.tables import Table

"""
////////////////////////////////////////////////////////////////////////////////////////
// Records Template Impementation
////////////////////////////////////////////////////////////////////////////////////////
"""


class RecordsTemplate(BaseModel):
    """
    Template dataclass for storing template information.

    Stores the key, documents, files, images, special placeholders, and tables
    associated with a records template.
    """

    #: Template name
    key: str
    #: Documents included in the template
    documents: Placeholders | None
    #: Files included in the template
    files: Placeholders | None
    #: Images included in the template
    images: Placeholders | None
    #: Special placeholders for the template
    special: Placeholders | None
    #: Tables included in the template
    tables: Placeholders | None


class RecordsTemplateRegistry:
    """
    Registry of templates for generating records in Markdown format to paste into Obsidian.

    Handles loading, saving, and registering templates from/to a JSON file.
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
        Save the registry to a file.
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
        Load the registry from a file.
        """
        with open(cls.__path, "r+") as file:
            cls.__registry = {
                key: RecordsTemplate.model_validate(template_)
                for key, template_ in json.load(file).items()
            }

    @classmethod
    def has(cls, key: str) -> bool:
        """
        Check if the registry contains a template with the given key.

        :param key: The key of the template.
        :returns: True if the registry contains a template with the given key, False otherwise.
        """
        return key in cls.__registry

    @classmethod
    def get(cls, key: str) -> "RecordsTemplate":
        """
        Get the template with the given key.

        :param key: The key of the template.
        :returns: Instantiated template.
        """
        return cls.__registry[key]

    @classmethod
    def register(cls, template_: "RecordsTemplate") -> None:
        """
        Register a new template in the registry.

        :param template_: The RecordsTemplate instance to register.
        :raises ValueError: If a template with the same key already exists.
        :raises FileNotFoundError: If the corresponding Markdown file does not exist.
        """
        if cls.has(template_.key):
            raise ValueError(f"Template with key {template_.key} already exists")
        try:
            assert cls.__path.exists()
        except AssertionError:
            cls.__path.mkdir(parents=True)

        markdown_file = cls.__path.parents[1].joinpath(f"{template_.key}.md")
        if not markdown_file.exists():
            raise FileNotFoundError(
                f"Markdown file for template {template_.key} does not exist"
            )

        cls.__registry[template_.key] = template_
        cls.__new_template = True

    @classmethod
    def __enter__(cls) -> "RecordsTemplateRegistry":
        """
        Context manager entry: loads the registry from file.
        """
        cls._load()
        return cls()

    @classmethod
    def __exit__(cls, exc_type, exc_val, exc_tb):  # noqa: ANN206, ANN001
        """
        Context manager exit: saves the registry if a new template was added.
        """
        if cls.__new_template:
            cls._save()


def add_template(
    key: str,
    documents: Placeholders | None = None,
    files: Placeholders | None = None,
    images: Placeholders | None = None,
    tables: Placeholders | None = None,
    special: Placeholders | None = None,
) -> None:
    """
    Add a new template to the registry.

    :param key: The key for the template.
    :param documents: List of document placeholders.
    :param files: List of file placeholders.
    :param images: List of image placeholders.
    :param tables: List of table placeholders.
    :param special: List of special placeholders.
    """
    with RecordsTemplateRegistry() as registry:
        template = RecordsTemplate(
            key=key,
            documents=documents,
            images=images,
            files=files,
            tables=tables,
            special=special,
        )
        registry.register(template)


"""
////////////////////////////////////////////////////////////////////////////////////////
// Rendering the templated records
////////////////////////////////////////////////////////////////////////////////////////
"""


def render(
    templates_directory: Path,
    key: str,
    documents: list[Path | None],
    images: list[Path | None],
    files: list[Path | None],
    tables: list["Table"] | list[None],
    special: list["Table"] | list[None],
) -> str:
    """
    Render the records template using Jinja2.

    :param templates_directory: Path to the templates directory.
    :param key: The key of the template to render.
    :param documents: List of document paths.
    :param images: List of image paths.
    :param files: List of file paths.
    :param tables: List of table data.
    :param special: List of special table data.
    :returns: Rendered template as a string.
    """
    environment = Environment(
        loader=FileSystemLoader(str(templates_directory)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment = add_filters(environment)
    environment = add_extensions(environment)
    template = environment.get_template(f"{key}.md")
    return template.render(
        documents=documents,
        images=images,
        files=files,
        tables=tables,
        special=special,
        environment=environment,
    )
