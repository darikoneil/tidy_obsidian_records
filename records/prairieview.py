from collections import namedtuple
from pathlib import Path
from typing import Any, Literal

import numpy as np
from lxml import etree as ET
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from pydantic.alias_generators import to_camel, to_snake
from scipy.io import loadmat


def _custom_camel_alias(snake: str) -> str:
    return to_camel(snake).replace(" ", "_")


def _custom_snake_alias(camel: str) -> str:
    return to_snake(camel).replace(" ", "_")


def _form_descriptive_field_name(element: ET.Element) -> str:
    for key in ("description", "subindex", "index"):
        if (value := element.get(key)) is not None:
            return _custom_snake_alias(f"{value}")
    raise KeyError(f"No descriptive field found for {element.tag}")


def _extract_index_meta(parent: ET.Element, *nested_elements: ET.Element) -> namedtuple:
    name = parent.get("key", "ANONYMOUS")
    field_names = [_form_descriptive_field_name(element) for element in nested_elements]
    values = [element.get("value") for element in nested_elements]
    return namedtuple(name, field_names, rename=True)(
        *(float(value) for value in values)
    )


def _extract_subindex_meta(
    parent: ET.Element, *nested_elements: ET.Element
) -> namedtuple:
    name = parent.get("key", "ANONYMOUS")
    field_names = []
    values = []
    for nested_element in nested_elements:
        if len(nested_element) == 1:
            field_names.append(_form_descriptive_field_name(nested_element))
            values.append(nested_element[0].get("value"))
        else:
            for subindex_element in nested_element:
                field_names.append(
                    "".join(
                        [
                            _form_descriptive_field_name(nested_element),
                            "_",
                            _form_descriptive_field_name(subindex_element),
                        ]
                    )
                )
                values.append(subindex_element.get("value"))
    return namedtuple(name, field_names, rename=True)(
        *(float(value) for value in values)
    )


def _collect_frame_times(sequence: ET.Element, key: str) -> list[float]:
    return [
        float(frame.attrib.get(key))
        for frame in sequence.findall("Frame")
        if key in frame.attrib
    ]


class PVSession(BaseModel):
    version: str
    date: str
    notes: str | None = None
    model_config = ConfigDict(extra="ignore")


class PVSystemID(BaseModel):
    serial_id: str = Field(alias="SystemIDs")
    model_config = ConfigDict(extra="ignore", alias_generator=_custom_camel_alias)


class PVImagingMeta(BaseModel):
    active_mode: str
    bit_depth: int
    current_scan_amplitude: Any
    current_scan_center: Any
    daq_gain: Any
    frame_period: float
    dwell_time: float
    interlaced_scan_track_count: int
    laser_power: Any
    lines_per_frame: int
    max_voltage: Any
    microns_per_pixel: Any
    min_voltage: Any
    objective_lens: str
    objective_lens_mag: int
    # needs special alias because of NA being split
    objective_lens_na: float = Field(..., alias="objectiveLensNA")
    optical_zoom: float
    pixels_per_line: int
    pmt_gain: Any
    position_current: Any
    preamp_filter: str
    preamp_gain: Any
    preamp_offset: Any
    rotation: int
    samples_per_pixel: int
    scan_line_period: float
    use_interlaced_scan_pattern: bool
    x_y_stage_grid_index: int
    x_y_stage_grid_x_index: int
    x_y_stage_grid_y_index: int
    y_aspect_expansion: int
    z_device: int
    model_config = ConfigDict(extra="ignore", alias_generator=_custom_camel_alias)

    @field_validator(
        "laser_power",
        "microns_per_pixel",
        "pmt_gain",
        "position_current",
        "current_scan_amplitude",
        "current_scan_center",
        "daq_gain",
        "max_voltage",
        "min_voltage",
        "preamp_gain",
        "preamp_offset",
        mode="after",
    )
    @classmethod
    def validate_named_tuple(cls, field: Any) -> Any:
        if not isinstance(field, tuple):  # close enough
            raise TypeError(f"Field must be a NamedTuple, not {type(field)}")

        return field

    @field_serializer(
        "laser_power",
        "microns_per_pixel",
        "pmt_gain",
        "position_current",
        "current_scan_amplitude",
        "current_scan_center",
        "daq_gain",
        "max_voltage",
        "min_voltage",
        "preamp_gain",
        "preamp_offset",
        mode="plain",
        when_used="always",
    )
    @classmethod
    def serialize_named_tuple(cls, field: Any) -> Any:
        return field


class PVSequenceMeta(BaseModel):
    num_planes: int
    num_channels: int
    relative_frame_times: list[list[float]]
    absolute_frames_times: list[list[float]]
    model_config = ConfigDict(extra="ignore")


class PrairieViewMeta(BaseModel):
    session: PVSession
    system_id: PVSystemID
    imaging_meta: PVImagingMeta | None = None
    sequence_meta: PVSequenceMeta | None = None


def get_pv_session_meta(root: ET.Element) -> PVSession:
    return PVSession(**dict(root.items()))


def get_pv_system_id(root: ET.Element) -> PVSystemID:
    system_id = root.find("SystemIDs")
    pv_meta = {system_id.tag: system_id.get("SystemID")}
    pv_meta.update(
        {
            system_id.tag: system_id.get("SystemID")
            for system_id in system_id.iterfind("SystemID")
        }
    )
    return PVSystemID(**pv_meta)


def get_pv_imaging_meta(root: ET.Element) -> PVImagingMeta | None:
    pv_meta_elements = root.find("PVStateShard").findall("PVStateValue")
    pv_meta = {
        pv_meta.attrib["key"]: pv_meta.attrib["value"]
        for pv_meta in pv_meta_elements
        if "value" in pv_meta.attrib
    }
    for meta_element in pv_meta_elements:
        if len((indexed_values := meta_element.findall("IndexedValue"))) > 0:
            pv_meta[meta_element.get("key", meta_element.tag)] = _extract_index_meta(
                meta_element, *indexed_values
            )
        if len((subindexed_values := meta_element.findall("SubindexedValues"))) > 0:
            pv_meta[meta_element.get("key", meta_element.tag)] = _extract_subindex_meta(
                meta_element, *subindexed_values
            )
    return PVImagingMeta(**pv_meta) if pv_meta else None


def get_pv_sequence_meta(root: ET.Element) -> PVSequenceMeta:
    first_stack = root.find("Sequence").find("Frame")
    num_planes = len(first_stack)
    num_channels = len(first_stack.findall("File"))
    # lmao
    relative_frame_times = np.vstack(
        [
            _collect_frame_times(sequence, "relativeTime")
            for sequence in root.find("Sequence")
        ]
    ).tolist()
    absolute_frame_times = np.vstack(
        [
            _collect_frame_times(sequence, "absoluteTime")
            for sequence in root.find("Sequence")
        ]
    ).tolist()
    return PVSequenceMeta(
        num_planes=num_planes,
        num_channels=num_channels,
        relative_frame_times=relative_frame_times,
        absolute_frames_times=absolute_frame_times,
    )


def get_num_planes_num_channels(root: ET.Element) -> tuple[int, int]:
    pv_sequence = root.find("Sequence").findall("Frame")
    return len(pv_sequence), len(pv_sequence[0].findall("File"))


def load_plane_metadata(file: Path) -> dict:
    """
    Load the plane metadata from a multiplane file.

    :param file:
    :return:
    """
    metadata = loadmat(str(file))
    planes = metadata["scan_data"]["planes"]
    num_planes = len(planes[0][0])
    plane_metadata = {}
    for p in range(num_planes):
        plane = planes[0][0][p]
        plane_metadata[p] = {
            "idx": plane[0][0][0][0][0][0],
            "pattern": plane[0][0][0][1][0][0],
            "x": plane[0][0][0][2][0][0],
            "y": plane[0][0][0][3][0][0],
            "z": plane[0][0][0][4][0][0],
            "i_targ": plane[0][0][0][5][0][0],
            "i_est": plane[0][0][0][6][0][0],
            "w_est": plane[0][0][0][7][0][0],
        }
    return plane_metadata


def load_metadata(
    xml_file: Path,
    component: Literal[
        "session", "system_id", "imaging_meta", "sequence_meta", None
    ] = None,
) -> PrairieViewMeta:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    match component:
        case "session":
            return get_pv_session_meta(root)
        case "system_id":
            return get_pv_system_id(root)
        case "imaging_meta":
            return get_pv_imaging_meta(root)
        case "sequence_meta":
            return get_pv_sequence_meta(root)
        case _:
            return PrairieViewMeta(
                session=get_pv_session_meta(root),
                system_id=get_pv_system_id(root),
                imaging_meta=get_pv_imaging_meta(root),
                sequence_meta=get_pv_sequence_meta(root),
            )
