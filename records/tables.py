import math
import tkinter as tk
from collections.abc import KeysView
from datetime import datetime
from itertools import product
from pathlib import Path
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticUndefined

from darik_code.imaging.meta import load_metadata

if TYPE_CHECKING:
    from darik_code.records.templates import RecordsTemplate


"""
////////////////////////////////////////////////////////////////////////////////////////
// Records Table Registry
////////////////////////////////////////////////////////////////////////////////////////
"""


def _gen_field_alias(field_name: str) -> str:
    """
    Convert a snake_case field name to a plain English alias.

    :param field_name: The snake_case field name.
    :returns: The plain English alias.
    """
    parts = field_name.split("_")
    return " ".join([part.capitalize() for part in parts])


class Table(BaseModel):
    """
    Base class for all records tables.

    Provides a title and configuration for alias generation.
    """

    title: str
    model_config = ConfigDict(
        alias_generator=_gen_field_alias, populate_by_name=True, extra="ignore"
    )

    def __str__(self):
        return self.title


class TableRegistry:
    """
    A registry for all records tables.

    Allows dynamic retrieval and registration of tables by name or alias.
    """

    #: A dictionary to store all records tables
    __registry: dict = {}

    @classmethod
    def register(cls, alias: str | None = None):  # noqa: ANN206
        """
        Decorator to register a new records table.

        :param alias: An alias for the table used as an additional key for retrieval.
        :returns: The decorator for table registration.
        """

        def register_table(table):  # noqa: ANN001
            cls.__registry[alias or table.__name__] = table
            return table

        return register_table

    @classmethod
    def get(cls, key: str) -> Table:
        """
        Retrieve a table by its name or alias.

        :param key: The name or alias of the table.
        :returns: The table class.
        """
        return cls.__registry.get(key)

    @classmethod
    def tables(cls) -> KeysView:
        """
        Retrieve all keys for the registered tables.

        :returns: The names and aliases of all registered tables.
        """
        return cls.__registry.keys()


def collect_tables(records_template: "RecordsTemplate") -> list[Table | None]:
    """
    Collect all table implementations used in the records template from the table registry.

    :param records_template: The records template.
    :returns: A list of records tables (or an empty list).
    """
    return [TableRegistry.get(table) for table in records_template.tables or []]


"""
////////////////////////////////////////////////////////////////////////////////////////
// SPECIAL
////////////////////////////////////////////////////////////////////////////////////////
"""


def collect_special(records_template: "RecordsTemplate") -> list[Any | None]:
    """
    Collect all special table implementations used in the records template from the table registry.

    :param records_template: The records template.
    :returns: A list of special records tables (or an empty list).
    """
    return [TableRegistry.get(special) for special in records_template.special or []]


"""
////////////////////////////////////////////////////////////////////////////////////////
// Records Tables (GENERAL)
////////////////////////////////////////////////////////////////////////////////////////
"""


@TableRegistry.register(alias="mouse-information")
class MouseInformation(Table):
    title: str = Field("Mouse Information", frozen=True)
    subject: str = "E000"
    cage: str = "000000"
    dob: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"), alias="DOB"
    )
    gender: Literal["Male", "Female"] = "Female"
    headplate_id: str = Field(default="Plain", alias="Headplate ID")
    condition: str = "N/A"
    physical_id: str = Field(default="N/A", alias="Physical ID")
    genotype: str = "Wildtype"
    transnetyx: str = "N/A"

    @field_validator("cage", mode="before")
    @classmethod
    def validate_cage(cls, value: Any) -> Any:
        if isinstance(value, int):
            value = f"{value:06d}"
        if isinstance(value, str):
            while len(value) < 6:
                value = f"0{value}"
        if all(char.isdigit() for char in value):
            return value
        raise ValueError("Cage number must be a 6-digit integer")


"""
////////////////////////////////////////////////////////////////////////////////////////
// SURGICAL
////////////////////////////////////////////////////////////////////////////////////////
"""


@TableRegistry.register(alias="head-fixation")
class HeadFixation(Table):
    title: str = Field("Head-Fixation", frozen=True)
    subject: str = "E000"
    procedure_date: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d")
    )
    procedure_time: str = Field(
        default_factory=lambda: datetime.now().strftime("%H:%M")
    )
    headplate_id: str = Field(default="Plain", alias="Headplate ID")
    cement_formulation: str = "2 Scoops Powder, 4 Drops Liquid, 1 Drop Catalyst"
    silicone_cover: bool = False


@TableRegistry.register(alias="cranial-window")
class CranialWindow(Table):
    title: str = Field("Cranial Window", frozen=True)
    subject: str = "E000"
    procedure_date: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d")
    )
    procedure_time: str = Field(
        default_factory=lambda: datetime.now().strftime("%H:%M")
    )
    headplate_id: str = Field(default="Plain", alias="Headplate ID")
    window_size: str = "2mm x 1.6mm"
    window_location: str = "-2.75 mm AP, -1.75 mm ML"
    window_quality: str = "Average"
    reused_window: bool = False
    window_adhesion: str = "Kwil-Sil Barrier & Cement"


@TableRegistry.register(alias="tamoxifen-injection")
class TamoxifenInjection(Table):
    title: str = Field("Tamoxifen Injection", frozen=True)
    subject: str = "E000"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M"))
    concentration: float = 10.0
    dose: float = 100.0
    weight: float = 30.0
    volume: float = 0.30


"""
////////////////////////////////////////////////////////////////////////////////////////
// IMAGING
////////////////////////////////////////////////////////////////////////////////////////
"""


@TableRegistry.register(alias="microscope-session")
class MicroscopeSession(Table):
    title: str = Field("Imaging Session", frozen=True)
    subject: str = "E000"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M"))
    relative_humidity: str = "5%"
    imaging_wavelength: str = "920 nm"
    stimulation_wavelength: str = "None"
    slm: bool = True


@TableRegistry.register(alias="imaging-fov")
class ImagingFOV(Table):
    title: str = Field("Imaging Field of View", frozen=True)
    subject: str = "E000"
    metadata_file: Path | str | None = ""
    objective_lens: str | None = ""
    laser_power: float | None = 0.0
    pmt_gain: int | float | None = 0
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
        meta = load_metadata(imaging_fov.metadata_file)
        imaging_meta = meta.imaging_meta
        imaging_fov.objective_lens = imaging_meta.objective_lens
        imaging_fov.laser_power = imaging_meta.laser_power.imaging
        imaging_fov.pmt_gain = imaging_meta.pmt_gain[0]
        imaging_fov.preamp_filter = imaging_meta.preamp_filter
        imaging_fov.optical_zoom = imaging_meta.optical_zoom
        imaging_fov.lines_per_frame = imaging_meta.lines_per_frame
        imaging_fov.pixels_per_line = imaging_meta.pixels_per_line
        imaging_fov.microns_per_pixel = imaging_meta.microns_per_pixel
        imaging_fov.frame_rate = 1 / imaging_meta.frame_period
        imaging_fov.x = imaging_meta.position_current.x_axis
        imaging_fov.y = imaging_meta.position_current.y_axis
        imaging_fov.z = imaging_meta.position_current[2]
        imaging_fov.planes = meta.sequence_meta.num_planes
        imaging_fov.channels = meta.sequence_meta.num_channels
        fr = (imaging_fov.frame_rate - 4.0 * imaging_fov.planes) / imaging_fov.planes
        imaging_fov.effective_frame_rate = fr
        return imaging_fov

    @field_serializer(
        "laser_power",
        "microns_per_pixel",
        "pmt_gain",
        "optical_zoom",
        "frame_rate",
        "effective_frame_rate",
        "x",
        "y",
        "z",
        mode="plain",
    )
    @classmethod
    def serialize_float(cls, value: float | tuple) -> str:
        if value is not None:
            if isinstance(value, tuple):
                values = [f"{v:.2f}" for v in value]
                return "(" + ", ".join(values) + ")"
            return f"{value:.2f}"


@TableRegistry.register(alias="imaging-roadmap")
class ImagingRoadmap(Table):
    title: str = Field("Imaging Roadmap", frozen=True)
    subject: str = "E000"
    landmark_metadata_file: Path | str | None = ""
    imaging_metadata_file: Path | str | None = ""
    relative_x_position: float = 0.0
    relative_y_position: float = 0.0
    relative_z_position: float = 0.0

    @model_validator(mode="after")
    @classmethod
    def validate_imaging_roadmap(
        cls, imaging_roadmap: "ImagingRoadmap"
    ) -> "ImagingRoadmap":
        imaging_meta = load_metadata(
            imaging_roadmap.imaging_metadata_file, "imaging_meta"
        )
        landmark_meta = load_metadata(
            imaging_roadmap.landmark_metadata_file, "imaging_meta"
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

    @field_serializer(
        "relative_x_position",
        "relative_y_position",
        "relative_z_position",
        mode="plain",
    )
    @classmethod
    def serialize_float(cls, value: float | tuple) -> str:
        if value is not None:
            if isinstance(value, tuple):
                values = [f"{v:.2f}" for v in value]
                return "(" + ", ".join(values) + ")"
            return f"{value:.2f}"


@TableRegistry.register(alias="multiplane-slm")
class MultiplaneSLM(Table):
    title: str = Field("Multiplane SLM", frozen=True)
    idx: int = Field(default=0, alias="Plane #")
    pattern: int = Field(default=0, alias="Pattern #")
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    i_targ: float = Field(default=1.0, alias="Target Intensity")
    i_est: float = Field(default=1.0, alias="Estimated Intensity")
    w_est: float = Field(default=1.0, alias="Weight Estimate")

    @field_serializer("x", "y", "z", "i_targ", "i_est", "w_est", mode="plain")
    @classmethod
    def serialize_float(cls, value: float | tuple) -> str:
        if value is not None:
            if isinstance(value, tuple):
                values = [f"{v:.2f}" for v in value]
                return "(" + ", ".join(values) + ")"
            return f"{value:.2f}"


@TableRegistry.register(alias="photostimulation")
class Photostimulation(Table):
    title: str = Field("Photostimulation", frozen=True)
    wavelength: float = Field(default=1064, alias="Wavelength (nm)")
    power: float = Field(default=0.0, alias="Power (a.u.)")
    duration: float = Field(default=30.0, alias="Duration (ms)")
    reps: int = 3
    interval: float = Field(default=30.0, alias="Interval (ms)")
    spiral_diameter: float = Field(default=8.0, alias="Spiral Diameter (um)")


"""
////////////////////////////////////////////////////////////////////////////////////////
// BEHAVIORAL
////////////////////////////////////////////////////////////////////////////////////////
"""


@TableRegistry.register(alias="burrow-session")
class BurrowSession(Table):
    title: str = Field("Burrow Session", frozen=True)
    subject: str = "E000"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M"))
    stage: Literal["Pre-Exposure", "Training", "Testing"] = "Pre-Exposure"
    condition: Literal["CS+ LOW", "CS+ HIGH"] = "CS+ LOW"

    @computed_field(return_type=bool, alias="Delivered UCS")
    def delivered_ucs(self) -> bool:
        return self.condition == "Training"


@TableRegistry.register(alias="burrow-parameters")
class BurrowParameters(Table):
    title: str = Field("Burrow Parameters", frozen=True)
    subject: str = "E000"
    rail_pressure: str = "60 psi"
    air_puff_intensity: str = Field(default="80 psi", alias="Air-Puff Intensity")
    air_puf_duration: str = Field(default="300 ms", alias="Air-Puff Duration")
    premature_threshold: str = "4.0 V"
    cue_intensity: str = "70 dB"
    cue_duration: str = "15 s"
    low_frequency: str = "10 kHz"
    low_style: str = "Sine"
    low_volume: float = 0.0180
    high_frequency: str = "15 kHz"
    high_style: str = "Sine"
    high_volume: float = 0.2100
    ucs_frequency: str = Field(default="1 Hz", alias="UCS Frequency")
    ucs_cycles: int = Field(default=5, alias="UCS Cycles")
    ucs_duration: str = Field(default="5 s", alias="UCS Duration")
    trials_per_cs: int = Field(default=10, alias="Trials per CS")
    habituation_duration: str = "15 min"
    pre_trial_duration: str = Field(default="15 s", alias="Pre-Trial Duration")
    trace_duration: str = "10 s"
    response_duration: str = "10 s"
    iti_duration: str = Field("90 s", alias="ITI Duration")


@TableRegistry.register(alias="startle-session")
class StartleSession(Table):
    title: str = Field("Burrow Session", frozen=True)
    subject: str = "E000"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M"))


@TableRegistry.register(alias="startle-parameters")
class StartleParameters(Table):
    title: str = Field("Startle Parameters", frozen=True)
    subject: str = "E000"
    habituation_duration: str = "10 min"
    iti_duration: str = Field(default="15 s", alias="ITI Duration")
    stimulus_trial_duration: str = "1 sec"
    stimulus_delivery_duration: str = "40 ms"
    stimulus_style: str = "White Noise"
    trials_per_intensity: int = 5
    baseline_intensity: str = "60 dB"
    threshold_intensities: str = "70, 80, 90, 100, & 110 dB"


@TableRegistry.register(alias="ppi-session")
class PPISession(Table):
    title: str = Field("PPI Session", frozen=True)
    subject: str = "E000"
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    time: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M"))


@TableRegistry.register(alias="ppi-parameters")
class PPIParameters(Table):
    title: str = Field("PPI Parameters", frozen=True)
    subject: str = "E000"
    habituation_duration: str = "1 min"
    pre_pulse_duration: str = "20 ms"
    gap_duration: str = "100 ms"
    post_pulse_duration: str = "40 ms"
    ppi_trial_duration: str = "1 s"
    iti_duration: str = Field(default="15 s", alias="ITI Duration")
    stimulus_style: str = "White Noise"
    trials_per_intensity: int = 5
    baseline_intensity: str = "60 dB"
    threshold_intensities: str = "70, 80, & 90 dB"


"""
////////////////////////////////////////////////////////////////////////////////////////
// Interactive Filling of Records Tables
////////////////////////////////////////////////////////////////////////////////////////
"""


def find_optimal_grid(num_fields: int) -> tuple[int, int]:
    """
    Find the optimal number of rows and columns for a given number of fields.

    :param num_fields: Number of total fields to display.
    :returns: The number of rows and columns for the grid.
    """
    cols = math.ceil(num_fields / 16)
    rows = 16
    return rows, cols


def initialize_fields(
    fields: dict, app: tk.Tk, rows: int, columns: int
) -> tuple[tk.Tk, dict]:
    """
    Initialize the GUI fields for interactive table filling.

    :param fields: Dictionary of field names and default values.
    :param app: The Tkinter root application.
    :param rows: Number of rows in the grid.
    :param columns: Number of columns in the grid.
    :returns: The Tkinter app and a dictionary of entry widgets.
    """
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
    """
    Submit the entries from the GUI and update the fields dictionary.

    :param app: The Tkinter root application.
    :param entries: Dictionary of entry widgets.
    :param fields: Dictionary to update with user input.
    """
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
    """
    Create a dictionary of fields for a given table, populating with default values.

    :param table: The table model.
    :returns: Dictionary of field names and default values.
    """
    fields = dict(table.model_fields)
    for key, value in fields.items():
        if key == "title":
            continue
        if callable(value.default_factory):
            fields[key] = value.default_factory()
        elif value.default == PydanticUndefined:
            fields[key] = "N/A"
        else:
            fields[key] = value.default
    return fields


# noinspection PyUnusedLocal
def fill_tables(subject: str, tables: list[BaseModel | None]) -> list[dict | None]:
    """
    Fill all records tables with interactive GUI.

    :param subject: The name of the subject.
    :param tables: The list of records tables.
    :returns: A list of dictionaries containing the filled records tables.
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
        filled_tables.append(table(**fields).model_dump(by_alias=True))
    return filled_tables
