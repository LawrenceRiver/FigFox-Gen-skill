"""Safe inspection, rendering, and diagnosis-gated crops for submitted SVG1.

The functions in this module validate, render, and crop existing artifacts only.
They never create, rewrite, or repair SVG source.
"""

from __future__ import annotations

import base64
import binascii
import math
import os
import re
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from defusedxml import ElementTree as DefusedElementTree

from .artifacts import validate_diagnosis


_SVG_NAMESPACE = "http://www.w3.org/2000/svg"
_SVG_ROOT = f"{{{_SVG_NAMESPACE}}}svg"
_XML_BASE = "{http://www.w3.org/XML/1998/namespace}base"
_VECTOR_TAGS = frozenset({"rect", "circle", "ellipse", "line", "polyline", "polygon", "path"})
_BANNED_TAGS = frozenset({"script", "foreignobject"})
_NON_RENDERING_TAGS = frozenset({"defs", "clippath", "mask", "marker", "pattern", "symbol"})
_DIRECT_RESOURCE_ATTRIBUTES = frozenset({"href", "src", "poster"})
_APPROVED_VERDICTS = frozenset({"keep", "accept_variation", "patch"})
_CANONICAL_CROP_SUFFIX = ("svg-diagnostic", "approved-crops")
_CROP_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_FRAGMENT = re.compile(r"#[^\s\"'()<>]+\Z")
_DATA_IMAGE = re.compile(
    r"data:image/(?:png|jpeg|webp);base64,([A-Za-z0-9+/]*={0,2})\Z",
    re.IGNORECASE,
)
_URL_START = re.compile(r"url\s*\(", re.IGNORECASE)
_URL_FUNCTION = re.compile(r"url\s*\(([^)]*)\)", re.IGNORECASE | re.DOTALL)
_CSS_IMPORT = re.compile(r"@import\b", re.IGNORECASE)
_NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?(?:px)?$")
_NUMBER_TOKEN = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
_PATH_DRAW_COMMAND = re.compile(r"[AaCcHhLlQqSsTtVv]")
_CURSOR_KEYWORDS = frozenset({"auto", "default", "none", "inherit", "initial", "unset"})


def _local_name(tag: object) -> str:
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def _validate_css_resources(value: str) -> None:
    """Allow CSS fragment paint-server references and nothing external."""

    if _CSS_IMPORT.search(value):
        raise ValueError("SVG1 CSS must not contain @import")
    starts = list(_URL_START.finditer(value))
    matches = list(_URL_FUNCTION.finditer(value))
    if len(starts) != len(matches):
        raise ValueError("SVG1 contains a malformed CSS resource URL")
    for match in matches:
        reference = match.group(1).strip()
        if len(reference) >= 2 and reference[0] == reference[-1] and reference[0] in "'\"":
            reference = reference[1:-1].strip()
        if not _FRAGMENT.fullmatch(reference):
            raise ValueError("SVG1 resource URLs must be internal fragment references")


def _is_allowed_raster_data(value: str) -> bool:
    match = _DATA_IMAGE.fullmatch(value)
    if match is None or not match.group(1):
        return False
    try:
        base64.b64decode(match.group(1), validate=True)
    except (binascii.Error, ValueError):
        return False
    return True


def _validate_resources(element: Any, tag: str) -> None:
    for attribute, raw_value in element.attrib.items():
        if attribute == _XML_BASE:
            raise ValueError("SVG1 must not contain xml:base")
        if not isinstance(raw_value, str):
            continue
        value = raw_value.strip()
        _validate_css_resources(value)
        name = _local_name(attribute).casefold()
        if name in _DIRECT_RESOURCE_ATTRIBUTES:
            if _FRAGMENT.fullmatch(value):
                continue
            if tag == "image" and name == "href" and _is_allowed_raster_data(value):
                continue
            raise ValueError("SVG1 resource attributes must use internal fragments or approved raster data")
        if name == "cursor" and not _URL_START.search(value) and value.casefold() not in _CURSOR_KEYWORDS:
            raise ValueError("SVG1 cursor resources must not name external files")
    if tag == "style":
        _validate_css_resources("".join(element.itertext()))


def _style_properties(element: Any) -> dict[str, str]:
    properties: dict[str, str] = {}
    style = element.attrib.get("style")
    if isinstance(style, str):
        for declaration in style.split(";"):
            if ":" in declaration:
                name, value = declaration.split(":", 1)
                properties[name.strip().casefold()] = value.strip()
    for name in ("display", "visibility", "opacity", "font-size"):
        value = element.attrib.get(name)
        if isinstance(value, str):
            properties.setdefault(name, value.strip())
    return properties


def _is_hidden(element: Any, inherited_hidden: bool) -> bool:
    if inherited_hidden:
        return True
    properties = _style_properties(element)
    if properties.get("display", "").casefold() == "none":
        return True
    if properties.get("visibility", "").casefold() in {"hidden", "collapse"}:
        return True
    opacity = properties.get("opacity")
    if opacity is not None:
        try:
            if float(opacity) <= 0:
                return True
        except ValueError:
            return True
    return False


def _length(value: Any, axis: float | None = None) -> float | None:
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if candidate.endswith("%"):
        if axis is None:
            return None
        try:
            return float(candidate[:-1]) * axis / 100.0
        except ValueError:
            return None
    if not _NUMBER.fullmatch(candidate):
        return None
    if candidate.casefold().endswith("px"):
        candidate = candidate[:-2]
    try:
        number = float(candidate)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def _viewport(root: Any) -> tuple[float, float] | None:
    view_box = root.attrib.get("viewBox")
    if isinstance(view_box, str):
        values = [float(value) for value in _NUMBER_TOKEN.findall(view_box)]
        if len(values) == 4 and values[2] > 0 and values[3] > 0:
            return values[2], values[3]
    width = _length(root.attrib.get("width"))
    height = _length(root.attrib.get("height"))
    if width is not None and height is not None and width > 0 and height > 0:
        return width, height
    return None


def _points(element: Any) -> list[tuple[float, float]]:
    value = element.attrib.get("points")
    if not isinstance(value, str):
        return []
    numbers = [float(number) for number in _NUMBER_TOKEN.findall(value)]
    return list(zip(numbers[::2], numbers[1::2])) if len(numbers) >= 4 and len(numbers) % 2 == 0 else []


def _geometry_measure(element: Any, tag: str, viewport: tuple[float, float] | None) -> tuple[bool, bool]:
    """Return (positive geometry, structurally meaningful geometry)."""

    canvas_width, canvas_height = viewport or (1.0, 1.0)
    canvas_area = canvas_width * canvas_height
    diagonal = math.hypot(canvas_width, canvas_height)

    def attr(name: str, axis: float | None = None, default: float | None = None) -> float | None:
        value = _length(element.attrib.get(name), axis)
        return default if value is None and name not in element.attrib else value

    area = 0.0
    span = 0.0
    if tag == "rect":
        width, height = attr("width", canvas_width), attr("height", canvas_height)
        if width is None or height is None or width <= 0 or height <= 0:
            return False, False
        area = width * height
    elif tag == "circle":
        radius = attr("r", min(canvas_width, canvas_height))
        if radius is None or radius <= 0:
            return False, False
        area = math.pi * radius * radius
    elif tag == "ellipse":
        rx = attr("rx", canvas_width)
        ry = attr("ry", canvas_height)
        if rx is None or ry is None or rx <= 0 or ry <= 0:
            return False, False
        area = math.pi * rx * ry
    elif tag == "line":
        x1, y1 = attr("x1", canvas_width, 0.0), attr("y1", canvas_height, 0.0)
        x2, y2 = attr("x2", canvas_width, 0.0), attr("y2", canvas_height, 0.0)
        if None in (x1, y1, x2, y2):
            return False, False
        span = math.hypot(x2 - x1, y2 - y1)
        if span <= 0:
            return False, False
    elif tag in {"polyline", "polygon"}:
        points = _points(element)
        minimum = 2 if tag == "polyline" else 3
        if len(set(points)) < minimum:
            return False, False
        xs, ys = zip(*points)
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        span = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
    elif tag == "path":
        data = element.attrib.get("d")
        if not isinstance(data, str) or not _PATH_DRAW_COMMAND.search(data):
            return False, False
        numbers = [float(number) for number in _NUMBER_TOKEN.findall(data)]
        if len(numbers) < 4:
            return False, False
        xs, ys = numbers[::2], numbers[1::2]
        if not ys:
            return False, False
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        span = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
        if area <= 0 and span <= 0:
            return False, False
    meaningful = area >= canvas_area * 0.001 or span >= diagonal * 0.01
    return True, meaningful


def _text_measure(element: Any) -> tuple[bool, bool]:
    properties = _style_properties(element)
    font_size = properties.get("font-size")
    if font_size is not None:
        size = _length(font_size)
        if size is None or size <= 0:
            return False, False
    text = " ".join("".join(element.itertext()).split())
    if not text:
        return False, False
    return True, len(re.sub(r"[^\w]+", "", text, flags=re.UNICODE)) >= 2


def _image_area(element: Any, viewport: tuple[float, float] | None) -> float:
    canvas_width, canvas_height = viewport or (1.0, 1.0)
    width = _length(element.attrib.get("width"), canvas_width)
    height = _length(element.attrib.get("height"), canvas_height)
    if width is None or height is None or width <= 0 or height <= 0:
        return 0.0
    return width * height


def inspect_editable_svg(path: str | Path) -> dict[str, int | bool]:
    """Fail closed on unsafe resources, namespaces, and raster wrappers."""

    source = Path(path)
    if not source.is_file():
        raise ValueError("SVG1 requires an existing file")
    try:
        root = DefusedElementTree.parse(source).getroot()
    except Exception as error:
        raise ValueError("SVG1 must be well-formed safe XML") from error
    if root.tag != _SVG_ROOT:
        raise ValueError("SVG1 root must be an SVG element in the SVG namespace")

    viewport = _viewport(root)
    canvas_area = viewport[0] * viewport[1] if viewport else None
    text_nodes = vector_nodes = raster_nodes = visible_raster_nodes = 0
    meaningful_editable_nodes = large_raster_nodes = full_canvas_raster_nodes = 0
    dominant_raster = False

    def visit(element: Any, hidden: bool = False, non_rendering: bool = False) -> None:
        nonlocal text_nodes, vector_nodes, raster_nodes, visible_raster_nodes
        nonlocal meaningful_editable_nodes, large_raster_nodes, full_canvas_raster_nodes, dominant_raster
        if not isinstance(element.tag, str) or not element.tag.startswith(f"{{{_SVG_NAMESPACE}}}"):
            raise ValueError("SVG1 child elements must use only the SVG namespace")
        tag = _local_name(element.tag).casefold()
        if tag in _BANNED_TAGS:
            raise ValueError(f"SVG1 must not contain {tag}")
        _validate_resources(element, tag)
        hidden = _is_hidden(element, hidden)
        non_rendering = non_rendering or tag in _NON_RENDERING_TAGS
        rendered = not hidden and not non_rendering
        if tag == "text" and rendered:
            positive, meaningful = _text_measure(element)
            if positive:
                text_nodes += 1
                meaningful_editable_nodes += int(meaningful)
        elif tag in _VECTOR_TAGS and rendered:
            positive, meaningful = _geometry_measure(element, tag, viewport)
            if positive:
                vector_nodes += 1
                meaningful_editable_nodes += int(meaningful)
        elif tag == "image":
            raster_nodes += 1
            if rendered:
                area = _image_area(element, viewport)
                if area > 0:
                    visible_raster_nodes += 1
                    if canvas_area is not None:
                        fraction = area / canvas_area
                        large_raster_nodes += int(fraction >= 0.25)
                        full_canvas_raster_nodes += int(fraction >= 0.95)
                        dominant_raster = dominant_raster or fraction >= 0.60
        for child in element:
            visit(child, hidden, non_rendering)

    visit(root)
    editable_nodes = text_nodes + vector_nodes
    raster_only = raster_nodes > 0 and (
        editable_nodes == 0 or (dominant_raster and meaningful_editable_nodes < 2)
    )
    if raster_only:
        raise ValueError("SVG1 raster wrapper is not an editable SVG")
    if editable_nodes == 0:
        raise ValueError("SVG1 requires one or more visible nonzero editable text or vector nodes")
    return {
        "editable_nodes": editable_nodes,
        "text_nodes": text_nodes,
        "vector_nodes": vector_nodes,
        "raster_nodes": raster_nodes,
        "visible_raster_nodes": visible_raster_nodes,
        "meaningful_editable_nodes": meaningful_editable_nodes,
        "large_raster_nodes": large_raster_nodes,
        "full_canvas_raster_nodes": full_canvas_raster_nodes,
        "dominant_raster": dominant_raster,
        "raster_only": False,
    }


def _remove_regular_file(path: Path) -> None:
    if path.is_symlink():
        return
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _verify_png(path: Path, failure_message: str) -> None:
    from PIL import Image

    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(failure_message)
    try:
        with Image.open(path) as image:
            if image.format != "PNG" or image.size[0] <= 0 or image.size[1] <= 0:
                raise RuntimeError(failure_message)
            image.verify()
    except RuntimeError:
        raise
    except Exception as error:
        raise RuntimeError(failure_message) from error


def render_svg(svg_path: str | Path, png_path: str | Path) -> Path:
    """Render validated SVG1 to an exclusively staged, atomically published PNG."""

    import cairosvg

    target = Path(png_path)
    if target.is_symlink():
        raise ValueError("PNG1.5 target must not be a symlink")
    if target.parent.is_symlink():
        raise ValueError("PNG1.5 target parent must not be a symlink")
    temporary: Path | None = None
    try:
        inspect_editable_svg(svg_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.parent.is_symlink() or target.is_symlink():
            raise ValueError("PNG1.5 target path must not contain a symlink destination")
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
        os.close(descriptor)
        temporary = Path(temporary_name)
        cairosvg.svg2png(url=str(Path(svg_path)), write_to=str(temporary))
        _verify_png(temporary, "SVG rendering did not produce a real nonempty PNG1.5")
        if target.is_symlink():
            raise ValueError("PNG1.5 target must not be a symlink")
        os.replace(temporary, target)
        temporary = None
        return target
    except Exception:
        if temporary is not None:
            _remove_regular_file(temporary)
        _remove_regular_file(target)
        raise


def _string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} requires a non-empty string")
    return value.strip()


def _normalized_bounds(value: Any, location: str) -> tuple[float, float, float, float]:
    if not isinstance(value, Mapping) or set(value) != {"x", "y", "width", "height"}:
        raise ValueError(f"{location} requires normalized x, y, width, and height")
    numbers: dict[str, float] = {}
    for key in ("x", "y", "width", "height"):
        raw = value[key]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(raw):
            raise ValueError(f"{location} {key} must be a finite number")
        numbers[key] = float(raw)
    x, y, width, height = (numbers[key] for key in ("x", "y", "width", "height"))
    if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 1 or y + height > 1:
        raise ValueError(f"{location} must stay within normalized PNG1.5 bounds")
    return x, y, width, height


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _reject_crop_symlinks(run_root: Path, destination: Path) -> None:
    current = run_root
    for part in destination.relative_to(run_root).parts:
        if current.is_symlink():
            raise ValueError("approved SVG crop paths must not contain symlinks")
        current = current / part
    if current.is_symlink():
        raise ValueError("approved SVG crop paths must not contain symlinks")


def _run_root_for_crop_directory(output_dir: Path) -> tuple[Path, Path]:
    destination = _absolute_lexical(output_dir)
    if tuple(destination.parts[-2:]) != _CANONICAL_CROP_SUFFIX:
        raise ValueError("approved SVG crop output_dir must end with svg-diagnostic/approved-crops")
    run_root = destination.parents[1]
    _reject_crop_symlinks(run_root, destination)
    return run_root, destination


def _diagnosis_records(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw_diagnosis = manifest.get("diagnosis")
    if not isinstance(raw_diagnosis, Mapping):
        raise ValueError("crop manifest requires a diagnosis object")
    expected_ids = manifest.get("component_ids")
    if not isinstance(expected_ids, list) or not expected_ids or not all(
        isinstance(item, str) and item.strip() for item in expected_ids
    ):
        raise ValueError("crop manifest requires a non-empty complete component_ids list from Context 2")
    expected_ids = [item.strip() for item in expected_ids]
    if len(expected_ids) != len(set(expected_ids)):
        raise ValueError("crop manifest component_ids must be unique")
    normalized = validate_diagnosis(raw_diagnosis, expected_ids)
    records: dict[str, Mapping[str, Any]] = {}
    for record in normalized["verdicts"]:
        diagnosis_id = record.get("id", record["component_id"])
        if not isinstance(diagnosis_id, str) or not diagnosis_id.strip() or diagnosis_id.strip() in records:
            raise ValueError("diagnosis records require unique non-empty ids")
        records[diagnosis_id.strip()] = record
    return records


def _crop_records(manifest: Mapping[str, Any], diagnosis_records: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    raw_crops = manifest.get("crops")
    if not isinstance(raw_crops, list) or not raw_crops:
        raise ValueError("crop manifest requires one or more crops")
    normalized: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for index, crop in enumerate(raw_crops):
        location = f"crop manifest crops[{index}]"
        if not isinstance(crop, Mapping):
            raise ValueError(f"{location} must be an object")
        crop_id = _string(crop.get("crop_id"), f"{location} crop_id")
        if not _CROP_ID.fullmatch(crop_id):
            raise ValueError(f"{location} crop_id is not a safe filename")
        target_component_id = _string(crop.get("target_component_id"), f"{location} target_component_id")
        diagnosis_id = _string(crop.get("diagnosis_id"), f"{location} diagnosis_id")
        diagnosis = diagnosis_records.get(diagnosis_id)
        if diagnosis is None:
            raise ValueError(f"{location} must cite a real diagnosis record")
        if diagnosis["component_id"] != target_component_id:
            raise ValueError(f"{location} diagnosis must target the same Context 2 component")
        if diagnosis["verdict"] not in _APPROVED_VERDICTS:
            raise ValueError(f"{location} requires an approved diagnosis verdict")
        output_name = f"{crop_id}.png"
        if output_name in seen_paths:
            raise ValueError("crop manifest crop_id values must be unique")
        seen_paths.add(output_name)
        normalized.append({
            "output_name": output_name,
            "target_component_id": target_component_id,
            "diagnosis": diagnosis,
            "bounds": _normalized_bounds(crop.get("bounds"), f"{location} bounds"),
        })
    return normalized


def apply_svg_crop_manifest(rendered_png: Path, manifest: Mapping[str, Any], output_dir: Path) -> dict[str, Any]:
    """Atomically materialize Context-2-anchored crops from canonical PNG1.5."""

    from PIL import Image

    if not isinstance(manifest, Mapping):
        raise ValueError("crop manifest must be an object")
    run_root, destination = _run_root_for_crop_directory(Path(output_dir))
    rendered = _absolute_lexical(Path(rendered_png))
    if Path(rendered_png).is_symlink():
        raise ValueError("PNG1.5 source must not be a symlink")
    if rendered != run_root / "svg-diagnostic" / "png1.5.png":
        raise ValueError("approved SVG crops must be made from the same run's svg-diagnostic/png1.5.png")
    _reject_crop_symlinks(run_root, rendered.parent)
    if not rendered.is_file():
        raise ValueError("PNG1.5 requires an existing file")
    diagnosis_records = _diagnosis_records(manifest)
    crops = _crop_records(manifest, diagnosis_records)
    destination.mkdir(parents=True, exist_ok=True)
    _reject_crop_symlinks(run_root, destination)
    for crop in crops:
        if (destination / crop["output_name"]).is_symlink():
            raise ValueError("approved SVG crop destination must not be a symlink")

    temporary_files: list[tuple[Path, Path, dict[str, Any]]] = []
    try:
        with Image.open(rendered) as image:
            if image.format != "PNG" or image.size[0] <= 0 or image.size[1] <= 0:
                raise ValueError("PNG1.5 must be a real PNG with positive dimensions")
            width, height = image.size
            for crop in crops:
                x, y, crop_width, crop_height = crop["bounds"]
                left, top = math.floor(x * width), math.floor(y * height)
                right, bottom = math.ceil((x + crop_width) * width), math.ceil((y + crop_height) * height)
                if right <= left or bottom <= top:
                    raise ValueError("normalized crop bounds produced an empty PNG1.5 crop")
                target = destination / crop["output_name"]
                descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=destination)
                os.close(descriptor)
                temporary = Path(temporary_name)
                temporary_files.append((temporary, target, crop))
                image.crop((left, top, right, bottom)).save(temporary, format="PNG")
                _verify_png(temporary, "SVG crop did not produce a real nonempty PNG")

        attachments: list[dict[str, Any]] = []
        for temporary, target, crop in temporary_files:
            if target.is_symlink():
                raise ValueError("approved SVG crop destination must not be a symlink")
            os.replace(temporary, target)
            diagnosis = crop["diagnosis"]
            reason = diagnosis.get("reason", "diagnosis-approved SVG component")
            attachments.append({
                "path": f"svg-diagnostic/approved-crops/{crop['output_name']}",
                "target_component_id": crop["target_component_id"],
                "diagnosis": f"{diagnosis['verdict']}: {_string(reason, 'diagnosis reason')}",
            })
        return {"crops": attachments}
    finally:
        for temporary, _, _ in temporary_files:
            _remove_regular_file(temporary)
