import argparse
from pathlib import Path
from typing import Any

from sub_code.records.tables import collect_special
from sub_code.records.misc import collect_files
from sub_code.records.tables import collect_tables, fill_tables
from sub_code.records.templates import RecordsTemplateRegistry, render

#: Default templates directory
DEFAULT_TEMPLATES_DIRECTORY: Path = Path(__file__).parents[2].joinpath("templates")


#: Default exports directory
DEFAULT_EXPORTS_DIRECTORY: Path = Path(__file__).parents[2].joinpath("exports")


def generate_records(
    key: str,
    subject: str,
    templates_directory: Path,
    exports_directory: Path,
) -> None:
    """
    Generate records for a subject using a template from the template directory. The
    generated records will be saved in the exports directory within a folder named after
    the subject. Any relevant documents, images, and files will be collected and
    copied to a sub-folder named 'files' within the subject folder.

    :param key:
    :param subject:
    :param templates_directory:
    :param exports_directory:
    :return:
    """
    with RecordsTemplateRegistry() as registry:
        records_template = registry.get(key)

    documents, images, files = collect_files(
        subject, records_template, exports_directory
    )
    tables = collect_tables(records_template)
    tables = fill_tables(subject, tables)
    special = collect_special(records_template)
    records = render(
        templates_directory,
        key,
        documents,
        images,
        files,
        tables,
        special
    )
    records_filename = exports_directory.joinpath(f"{subject}", f"{subject}_{key}.md")
    with open(records_filename, "w") as file:
        file.write(records)


"""
////////////////////////////////////////////////////////////////////////////////////////
// Entry Point
////////////////////////////////////////////////////////////////////////////////////////
"""


def arg_parser() -> dict[str, Any]:
    """
    Parse command line arguments

    :returns: The key of the template, the name of the subject, and the path to save the
        generated records
    """
    parser = argparse.ArgumentParser(
        description="Generate records for a subject using " "stored templates"
    )
    parser.add_argument("key", help="The key of the template to use")
    parser.add_argument("subject", help="The name of the subject")
    parser.add_argument(
        "--templates_directory",
        "--t",
        type=Path,
        default=DEFAULT_TEMPLATES_DIRECTORY,
        help="The path to the templates directory",
    )
    parser.add_argument(
        "--exports_directory",
        "--e",
        type=Path,
        default=DEFAULT_EXPORTS_DIRECTORY,
        help="The path to save the generated records",
    )
    args_ = parser.parse_args()
    return {
        "key": args_.key,
        "subject": args_.subject,
        "templates_directory": args_.templates_directory,
        "exports_directory": args_.exports_directory,
    }


if __name__ == "__main__":
    generate_records(**arg_parser())
