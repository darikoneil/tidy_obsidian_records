import math
import tkinter as tk
from datetime import datetime
from itertools import product
from pathlib import Path
from tkinter import ttk
from typing import TYPE_CHECKING, Any, KeysView, Literal

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticUndefined

from sub_code.imaging.meta import load_metadata
from sub_code.records.files import select_file

if TYPE_CHECKING:
    from sub_code.records.templates import RecordsTemplate

"""
////////////////////////////////////////////////////////////////////////////////////////
// Records Table Registry
////////////////////////////////////////////////////////////////////////////////////////
"""


class TableRegistry:
    """
    A registry for all records tables. This class allows us to dynamically retrieve
    a table by its name or alias
    """

    #: A dictionary to store all records tables
    __registry: dict = {}

    @classmethod
    def register(cls, alias: str | None = None):
        """
        A decorator to register a new records table

        :param alias: An alias for the table used as an additional key for retrieval
        """

        def register_table(table):
            nonlocal alias
            if alias:
                cls.__registry[alias] = table
            cls.__registry[table.__name__] = table
            return table

        return register_table

    @classmethod
    def get(cls, key: str) -> BaseModel:
        """
        Retrieve a table by its name or alias

        :param key: The name or alias of the table
        :return: The table class
        """
        return cls.__registry.get(key)

    @classmethod
    def tables(cls) -> KeysView:
        """
        Retrieve all keys for the registered tables

        :return: The names and aliases of all registered tables
        """
        return cls.__registry.keys()


def collect_tables(records_template: "RecordsTemplate") -> list[BaseModel | None]:
    """
    Collect all records tables from the table registry

    :param records_template: The records template
    :return: A list of records tables
    """
    return [TableRegistry.get(table) for table in records_template.tables or []]


"""
////////////////////////////////////////////////////////////////////////////////////////
// Records Tables
////////////////////////////////////////////////////////////////////////////////////////
"""


@TableRegistry.register(alias="mouse-information")
class MouseInformation(BaseModel):
    title: str = Field("Mouse Information", frozen=True)
    subject: str = "E000"
    cage: str = "000000"
    dob: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    gender: Literal["Male", "Female"] = "Female"
    headplate_id: str = "Plain"
    condition: str = "N/A"
    physical_id: str = "N/A"
    genotype: str = "Wildtype"
    transnetyx: str = "N/A"

    @field_validator("cage", mode="before")
    @classmethod
    def validate_cage(cls, value: Any):
        if isinstance(value, int):
            value = f"{value:06d}"
        if isinstance(value, str):
            while len(value) < 6:
                value = f"0{value}"
        if all(char.isdigit() for char in value):
            return value
        else:
            raise ValueError("Cage number must be a 6-digit integer")


@TableRegistry.register(alias="head-fixation")
class HeadFixation(BaseModel):
    title: str = Field("Head-Fixation", frozen=True)
    subject: str = "E000"
    procedure_date: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d")
    )
    procedure_time: str = Field(
        default_factory=lambda: datetime.now().strftime("%H:%M")
    )
    headplate_id: str = "N/A"
    cement_formulation: str = "2 Scoops Powder, 4 Drops Liquid, 1 Drop Catalyst"
    silicone_cover: bool = False


@TableRegistry.register(alias="cranial-window")
class CranialWindow(BaseModel):
    title: str = Field("Cranial Window", frozen=True)
    subject: str = "E000"
    procedure_date: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d")
    )
    procedure_time: str = Field(
        default_factory=lambda: datetime.now().strftime("%H:%M")
    )
    headplate_id: str = "N/A"
    window_size: str = "2mm x 1.6mm"
    window_location: str = "-2.75 mm AP, -1.75 mm ML"
    window_quality: str = "Average"
    reused_window: bool = False
    window_adheson: str = "Kwil-Sil Barrier & Cement"


@TableRegistry.register(alias="tamoxifen-injection")
class TamoxifenInjection(BaseModel):
    title: str = Field("Tamoxifen Injection", frozen=True)
    subject: str = "E000"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M"))
    concentration: float = 10.0
    dose: float = 100.0
    weight: float = 30.0
    volume: float = 0.30


@TableRegistry.register(alias="imaging-session")
class MicroscopeSession(BaseModel):
    title: str = Field("Imaging Session", frozen=True)
    subject: str = "E000"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M"))
    relative_humidity: float = 5.0
    imaging_wavelength: str = "920 nm"
    stimulation_wavelength: str = "None"
    slm: bool = True


@TableRegistry.register(alias="imaging-fov")
class ImagingFOV(BaseModel):
    title: str = Field("Imaging Field of View", frozen=True)
    subject: str = "E000"
    use_meta_file: bool = True
    meta_file: Path | str | None = ""
    objective_lens: str | None = ""
    laser_power: float | None = 0.0
    pmt_gain: int | None = 0
    preamp_filter: str | None = "None"
    optical_zoom: float | None = 1.0
    lines_per_frame: int | None = 0
    pixels_per_line: int | None = 0
    microns_per_pixel: float | None = 0.0
    planes: int | None = 0
    channels: int | None = 0
    frame_rate: float | None = 0.0
    effective_frame_rate: float | None = 0.0
    x: float | None = 0.0
    y: float | None = 0.0
    z: float | None = 0.0

    @model_validator(mode="after")
    @classmethod
    def validate_imaging_fov(cls, imaging_fov: "ImagingFOV") -> "ImagingFOV":
        if imaging_fov.use_meta_file:
            if imaging_fov.meta_file == "":
                imaging_fov.meta_file = select_file(title="Select Imaging Meta File")
            meta = load_metadata(imaging_fov.meta_file)
            imaging_meta = meta.imaging_meta
            imaging_fov.objective_lens = imaging_meta.objective_lens
            imaging_fov.laser_power = imaging_meta.laser_power.imaging
            imaging_fov.pmt_gain = imaging_meta.pmt_gain.pmt_2_green
            imaging_fov.preamp_filter = imaging_meta.preamp_filter
            imaging_fov.optical_zoom = imaging_meta.optical_zoom
            imaging_fov.lines_per_frame = imaging_meta.lines_per_frame
            imaging_fov.pixels_per_line = imaging_meta.pixels_per_line
            imaging_fov.microns_per_pixel = imaging_meta.microns_per_pixel
            imaging_fov.frame_rate = (1 / imaging_meta.frame_period) * 1000
            imaging_fov.x = imaging_meta.position_current.x_axis
            imaging_fov.y = imaging_meta.position_current.y_axis
            imaging_fov.z = imaging_meta.position_current.z_axis_z_focus
            imaging_fov.planes = meta.sequence_meta.num_planes
            imaging_fov.channels = meta.sequence_meta.num_channels
            imaging_fov.effective_frame_rate = (
                imaging_fov.frame_rate / imaging_fov.planes
            )

        return imaging_fov


@TableRegistry.register(alias="imaging-roadmap")
class ImagingRoadmap(BaseModel):
    title: str = Field("Imaging Roadmap", frozen=True)
    subject: str = "E000"
    landmark_meta_file: Path | str | None = ""
    imaging_meta_file: Path | str | None = ""
    relative_x_position: float = 0.0
    relative_y_position: float = 0.0
    relative_z_position: float = 0.0

    @model_validator(mode="after")
    @classmethod
    def validate_imaging_roadmap(
        cls, imaging_roadmap: "ImagingRoadmap"
    ) -> "ImagingRoadmap":
        if imaging_roadmap.landmark_meta_file == "":
            imaging_roadmap.landmark_meta_file = select_file(
                title="Select Landmark Meta File"
            )
        if imaging_roadmap.imaging_meta_file == "":
            imaging_roadmap.imaging_meta_file = select_file(
                title="Select Imaging Meta File"
            )
        imaging_meta = load_metadata(imaging_roadmap.imaging_meta_file, "imaging_meta")
        landmark_meta = load_metadata(
            imaging_roadmap.landmark_meta_file, "imaging_meta"
        )
        imaging_roadmap.relative_x_position = (
            imaging_meta.position_current.x_axis - landmark_meta.position_current.x_axis
        )
        imaging_roadmap.relative_y_position = (
            imaging_meta.position_current.y_axis - landmark_meta.position_current.y_axis
        )
        imaging_roadmap.relative_z_position = (
            imaging_meta.position_current.z_axis_z_focus
            - landmark_meta.position_current.z_axis_z_focus
        )
        return imaging_roadmap


"""
////////////////////////////////////////////////////////////////////////////////////////
// Interactive Filling of Records Tables
////////////////////////////////////////////////////////////////////////////////////////
"""


def find_optimal_grid(num_fields: int) -> tuple[int, int]:
    """
    Find the optimal number of rows and columns for a given number of fields.

    :param num_fields: Number of total fields to display
    :returns: The number of rows and columns for the grid
    """
    cols = math.ceil(num_fields / 16)
    rows = 16
    return rows, cols


def initialize_fields(fields: dict, app: tk.Tk, rows: int, columns: int):

    frames = {}
    entries = {}
    for name, value in fields.items():
        frames[name] = ttk.Frame(app)
        frame = frames[name]
        label = ttk.Label(frame, text=name, width=25)
        label.pack(side="left")
        entry = ttk.Entry(frame)
        entry.insert(0, value)
        entry.pack(side="left", fill="x", expand=True)
        entries[name] = entry
    fields_iter = iter(entries.items())
    for col, row in product(range(columns), range(rows)):
        field_name, field_value = next(fields_iter, (None, None))
        if field_name == (None, None) or field_name is None:
            pass
        else:
            frames[field_name].grid(row=row, column=col, padx=5, pady=2)
    return app, entries


def submit_entries(app: tk.Tk, entries: dict, fields: dict) -> None:
    fields_iter = iter(entries.items())
    for _, row in entries.items():
        if row:
            field_name, field_value = next(fields_iter, (None, None))
            if field_name == (None, None) or field_name is None:
                pass
            else:
                fields[field_name] = field_value.get()
    app.quit()


def make_fields_container(table: BaseModel) -> dict:
    fields = dict(table.model_fields)
    for key, value in fields.items():
        if key == "title":
            continue
        elif callable(value.default_factory):
            fields[key] = value.default_factory()
        elif value.default == PydanticUndefined:
            fields[key] = "N/A"
        else:
            fields[key] = value.default
    return fields


# noinspection PyUnusedLocal
def fill_tables(subject: str, tables: list[BaseModel | None]) -> list[dict | None]:
    """
    Fill all records tables with interactive GUI

    :param subject: The name of the subject
    :param tables: The list of records tables
    :return: A list of dictionaries containing the filled records tables
    """
    filled_tables = []
    for table in tables:
        fields = make_fields_container(table)
        rows, columns = find_optimal_grid(sum([2 for _ in fields]))
        app = tk.Tk()
        app.title(f"{fields.get('title').default}: {subject}")
        _ = fields.pop("title", None)
        fields["subject"] = subject
        app, entries = initialize_fields(fields, app, rows, columns)
        submit_button = ttk.Button(
            app, text="Submit", command=lambda: submit_entries(app, entries, fields)
        )
        submit_button.grid(row=rows, column=columns, padx=5, pady=5)
        app.mainloop()

        # noinspection PyCallingNonCallable
        filled_tables.append(table(**fields).model_dump())
    return filled_tables
