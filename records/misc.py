from itertools import chain
from pathlib import Path
from shutil import copy2
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from records.templates import RecordsTemplate

#: Default initial directory for file selection
_INITIAL_DIRECTORY: Path = Path.cwd()

#: Placeholders Type Alias
Placeholders: TypeAlias = list[str | None]


def select_file(**kwargs) -> Path | list[Path] | None:
    """
    Interactive tool for file/files selection. All keyword arguments are
    passed to
    `tkinter.filedialog.askopenfilename <https://docs.python.org/3/library/tk.html>`_

    :param kwargs: keyword arguments passed to tkinter.filedialog.askdirectory

    :return: absolute path to file, list of absolute paths to files, or None
    """
    global _INITIAL_DIRECTORY

    root = Tk()
    file = askopenfilenames(initialdir=_INITIAL_DIRECTORY, **kwargs)
    if str(file) == "." or len(file) == 0:
        file = None
    elif len(file) > 1:
        _INITIAL_DIRECTORY = Path(file[0]).parent
        file = [Path(file_).resolve() for file_ in file]
    else:
        # noinspection PyTypeChecker
        file = Path(file[0])
        _INITIAL_DIRECTORY = file.parent
        # noinspection PyTypeChecker
        file = file.resolve()
    root.destroy()
    return file


def _copy_files(files: Path | list[Path], exported_file_directory: Path):
    if isinstance(files, Path):
        copy2(files, exported_file_directory.joinpath(files.name))
    elif isinstance(files, list):
        for file in files:
            _copy_files(file, exported_file_directory)


def collect_files(
    subject: str, records_template: "RecordsTemplate", exports_directory: Path
) -> tuple[list[Path | None], list[Path | None], list[Path | None]]:
    """
    Collect files for the subject using the provided records template

    :param subject:
    :param records_template:
    :param exports_directory:
    :return: The list of files of relevant documents, images, and files
    """
    exported_file_directory = exports_directory.joinpath(subject, "files")
    exported_file_directory.mkdir(exist_ok=True, parents=True)

    documents = {
        description: select_file(title=description)
        for description in records_template.documents or []
    }
    images = {
        description: select_file(title=description)
        for description in records_template.images or []
    }
    files = {
        description: select_file(title=description)
        for description in records_template.files or []
    }

    for files_ in chain.from_iterable(
        [documents.values(), images.values(), files.values()]
    ):
        _copy_files(files, exported_file_directory)

    return list(documents.values()), list(images.values()), list(files.values())

