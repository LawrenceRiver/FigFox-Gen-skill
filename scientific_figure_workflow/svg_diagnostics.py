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
from io import BytesIO
from pathlib import Path
from typing import Any

import tinycss2
from defusedxml import ElementTree as DefusedElementTree
from tinycss2.color3 import parse_color

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
    r"data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/]*={0,2})\Z",
    re.IGNORECASE,
)
_NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?(?:px)?$")
_NUMBER_TOKEN = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
_PATH_DRAW_COMMAND = re.compile(r"[AaCcHhLlQqSsTtVv]")
_CURSOR_KEYWORDS = frozenset({"auto", "default", "none", "inherit", "initial", "unset"})
_MAX_RASTER_BYTES = 5 * 1024 * 1024
_MAX_RASTER_PIXELS = 25_000_000
_RASTER_FORMATS = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}
_STYLESHEET_ELIGIBILITY_PROPERTIES = frozenset({
    "display", "visibility", "opacity", "fill", "fill-opacity", "stroke",
    "stroke-opacity", "stroke-width", "transform", "clip-path", "mask", "filter",
})
_PRESENTATION_PROPERTIES = frozenset({
    "display", "visibility", "opacity", "fill", "fill-opacity", "stroke",
    "stroke-opacity", "stroke-width", "font-size", "transform", "clip-path", "mask", "filter",
})


def _local_name(tag: object) -> str:
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def _validate_url(reference: str) -> None:
    if not _FRAGMENT.fullmatch(reference.strip()):
        raise ValueError("SVG1 resource URLs must be internal fragment references")


def _walk_css_tokens(tokens: list[Any]) -> None:
    """Inspect decoded tinycss2 tokens, including nested blocks and functions."""

    for token in tokens:
        token_type = getattr(token, "type", "")
        if token_type == "error":
            raise ValueError("SVG1 contains malformed CSS resource syntax")
        if token_type == "url":
            _validate_url(token.value)
            continue
        if token_type == "function":
            if token.lower_name == "url":
                arguments = [item for item in token.arguments if item.type not in {"whitespace", "comment"}]
                if len(arguments) != 1 or arguments[0].type not in {"string", "url", "ident", "hash"}:
                    raise ValueError("SVG1 contains an invalid CSS resource URL")
                argument = arguments[0]
                reference = f"#{argument.value}" if argument.type == "hash" else argument.value
                _validate_url(reference)
            else:
                _walk_css_tokens(token.arguments)
            continue
        content = getattr(token, "content", None)
        if isinstance(content, list):
            _walk_css_tokens(content)


def _parse_declarations(tokens_or_text: Any) -> tuple[dict[str, str], bool]:
    declarations = tinycss2.parse_declaration_list(
        tokens_or_text, skip_comments=True, skip_whitespace=True
    )
    properties: dict[str, str] = {}
    eligibility_uncertain = False
    for declaration in declarations:
        if declaration.type == "error":
            raise ValueError("SVG1 contains malformed CSS declarations")
        if declaration.type == "at-rule":
            if declaration.lower_at_keyword == "import":
                raise ValueError("SVG1 CSS must not contain @import")
            raise ValueError("SVG1 style declarations must not contain at-rules")
        if declaration.type != "declaration":
            raise ValueError("SVG1 contains unsupported CSS declarations")
        _walk_css_tokens(declaration.value)
        properties[declaration.lower_name] = tinycss2.serialize(declaration.value).strip()
        eligibility_uncertain = eligibility_uncertain or declaration.lower_name in _STYLESHEET_ELIGIBILITY_PROPERTIES
    return properties, eligibility_uncertain


def _validate_stylesheet(value: str) -> bool:
    rules = tinycss2.parse_stylesheet(value, skip_comments=True, skip_whitespace=True)
    eligibility_uncertain = False
    for rule in rules:
        if rule.type == "error":
            raise ValueError("SVG1 contains malformed CSS stylesheet syntax")
        if rule.type == "at-rule":
            if rule.lower_at_keyword == "import":
                raise ValueError("SVG1 CSS must not contain @import")
            _walk_css_tokens(rule.prelude)
            if rule.content is not None:
                _walk_css_tokens(rule.content)
                eligibility_uncertain = True
            continue
        if rule.type != "qualified-rule":
            raise ValueError("SVG1 contains unsupported CSS rules")
        _walk_css_tokens(rule.prelude)
        _, affects_eligibility = _parse_declarations(rule.content)
        eligibility_uncertain = eligibility_uncertain or affects_eligibility
    return eligibility_uncertain


def _is_allowed_raster_data(value: str) -> bool:
    match = _DATA_IMAGE.fullmatch(value)
    if match is None or not match.group(2):
        return False
    encoded = match.group(2)
    if len(encoded) > ((_MAX_RASTER_BYTES + 2) // 3) * 4:
        return False
    try:
        decoded = base64.b64decode(encoded, validate=True)
        if not decoded or len(decoded) > _MAX_RASTER_BYTES:
            return False
        from PIL import Image

        with Image.open(BytesIO(decoded)) as image:
            expected_format = _RASTER_FORMATS[match.group(1).casefold()]
            if image.format != expected_format or image.width <= 0 or image.height <= 0:
                return False
            if image.width * image.height > _MAX_RASTER_PIXELS:
                return False
            image.verify()
    except (binascii.Error, ValueError, OSError, KeyError):
        return False
    return True


def _validate_resources(element: Any, tag: str) -> bool:
    stylesheet_uncertain = False
    for attribute, raw_value in element.attrib.items():
        if attribute == _XML_BASE:
            raise ValueError("SVG1 must not contain xml:base")
        if not isinstance(raw_value, str):
            continue
        name = _local_name(attribute).casefold()
        if name.startswith("on"):
            raise ValueError("SVG1 must not contain event handler attributes")
        value = raw_value.strip()
        if name in _DIRECT_RESOURCE_ATTRIBUTES:
            if _FRAGMENT.fullmatch(value):
                continue
            if tag == "image" and name == "href" and _is_allowed_raster_data(value):
                continue
            raise ValueError("SVG1 resource attributes must use internal fragments or approved raster data")
        if name == "style":
            _parse_declarations(value)
        else:
            _walk_css_tokens(tinycss2.parse_component_value_list(value, skip_comments=True))
        if name == "cursor" and value.casefold() not in _CURSOR_KEYWORDS and "url" not in value.casefold():
            raise ValueError("SVG1 cursor resources must not name external files")
    if tag == "style":
        stylesheet_uncertain = _validate_stylesheet("".join(element.itertext()))
    return stylesheet_uncertain


def _style_properties(element: Any) -> dict[str, str]:
    properties: dict[str, str] = {}
    style = element.attrib.get("style")
    if isinstance(style, str):
        properties.update(_parse_declarations(style)[0])
    for name in _PRESENTATION_PROPERTIES:
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


def _viewport(root: Any) -> tuple[float, float, float, float] | None:
    view_box = root.attrib.get("viewBox")
    if isinstance(view_box, str):
        values = [float(value) for value in _NUMBER_TOKEN.findall(view_box)]
        if len(values) == 4 and values[2] > 0 and values[3] > 0:
            return values[0], values[1], values[0] + values[2], values[1] + values[3]
    width = _length(root.attrib.get("width"))
    height = _length(root.attrib.get("height"))
    if width is not None and height is not None and width > 0 and height > 0:
        return 0.0, 0.0, width, height
    return None


def _points(element: Any) -> list[tuple[float, float]]:
    value = element.attrib.get("points")
    if not isinstance(value, str):
        return []
    numbers = [float(number) for number in _NUMBER_TOKEN.findall(value)]
    return list(zip(numbers[::2], numbers[1::2])) if len(numbers) >= 4 and len(numbers) % 2 == 0 else []


def _geometry_measure(
    element: Any, tag: str, viewport: tuple[float, float, float, float] | None
) -> tuple[bool, bool, tuple[float, float, float, float] | None, bool]:
    """Return positive, meaningful, bounds, and whether the shape has area."""

    if viewport:
        canvas_width, canvas_height = viewport[2] - viewport[0], viewport[3] - viewport[1]
    else:
        canvas_width, canvas_height = 1.0, 1.0
    canvas_area = canvas_width * canvas_height
    diagonal = math.hypot(canvas_width, canvas_height)

    def attr(name: str, axis: float | None = None, default: float | None = None) -> float | None:
        value = _length(element.attrib.get(name), axis)
        return default if value is None and name not in element.attrib else value

    area = 0.0
    span = 0.0
    bounds: tuple[float, float, float, float] | None = None
    if tag == "rect":
        width, height = attr("width", canvas_width), attr("height", canvas_height)
        if width is None or height is None or width <= 0 or height <= 0:
            return False, False, None, False
        x, y = attr("x", canvas_width, 0.0), attr("y", canvas_height, 0.0)
        if x is None or y is None:
            return False, False, None, False
        area = width * height
        bounds = (x, y, x + width, y + height)
    elif tag == "circle":
        radius = attr("r", min(canvas_width, canvas_height))
        if radius is None or radius <= 0:
            return False, False, None, False
        cx, cy = attr("cx", canvas_width, 0.0), attr("cy", canvas_height, 0.0)
        if cx is None or cy is None:
            return False, False, None, False
        area = math.pi * radius * radius
        bounds = (cx - radius, cy - radius, cx + radius, cy + radius)
    elif tag == "ellipse":
        rx = attr("rx", canvas_width)
        ry = attr("ry", canvas_height)
        if rx is None or ry is None or rx <= 0 or ry <= 0:
            return False, False, None, False
        cx, cy = attr("cx", canvas_width, 0.0), attr("cy", canvas_height, 0.0)
        if cx is None or cy is None:
            return False, False, None, False
        area = math.pi * rx * ry
        bounds = (cx - rx, cy - ry, cx + rx, cy + ry)
    elif tag == "line":
        x1, y1 = attr("x1", canvas_width, 0.0), attr("y1", canvas_height, 0.0)
        x2, y2 = attr("x2", canvas_width, 0.0), attr("y2", canvas_height, 0.0)
        if None in (x1, y1, x2, y2):
            return False, False, None, False
        span = math.hypot(x2 - x1, y2 - y1)
        if span <= 0:
            return False, False, None, False
        bounds = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
    elif tag in {"polyline", "polygon"}:
        points = _points(element)
        minimum = 2 if tag == "polyline" else 3
        if len(set(points)) < minimum:
            return False, False, None, False
        xs, ys = zip(*points)
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        span = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
        bounds = (min(xs), min(ys), max(xs), max(ys))
    elif tag == "path":
        data = element.attrib.get("d")
        if not isinstance(data, str) or not _PATH_DRAW_COMMAND.search(data):
            return False, False, None, False
        numbers = [float(number) for number in _NUMBER_TOKEN.findall(data)]
        if len(numbers) < 4:
            return False, False, None, False
        xs, ys = numbers[::2], numbers[1::2]
        if not ys:
            return False, False, None, False
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        span = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
        if area <= 0 and span <= 0:
            return False, False, None, False
        bounds = (min(xs), min(ys), max(xs), max(ys))
    meaningful = area >= canvas_area * 0.001 or span >= diagonal * 0.01
    return True, meaningful, bounds, area > 0


def _text_measure(
    element: Any, properties: Mapping[str, str]
) -> tuple[bool, bool, tuple[float, float, float, float] | None]:
    font_size = properties.get("font-size")
    size = _length(font_size) if font_size is not None else 16.0
    if size is None or size <= 0:
        return False, False, None
    text = " ".join("".join(element.itertext()).split())
    if not text:
        return False, False, None
    x = _length(element.attrib.get("x")) if "x" in element.attrib else 0.0
    y = _length(element.attrib.get("y")) if "y" in element.attrib else 0.0
    if x is None or y is None:
        return False, False, None
    bounds = (x, y - size, x + max(size * 0.6 * len(text), size * 0.5), y)
    return True, len(re.sub(r"[^\w]+", "", text, flags=re.UNICODE)) >= 2, bounds


def _image_bounds(
    element: Any, viewport: tuple[float, float, float, float] | None
) -> tuple[float, float, float, float] | None:
    if viewport:
        canvas_width, canvas_height = viewport[2] - viewport[0], viewport[3] - viewport[1]
    else:
        canvas_width, canvas_height = 1.0, 1.0
    width = _length(element.attrib.get("width"), canvas_width)
    height = _length(element.attrib.get("height"), canvas_height)
    if width is None or height is None or width <= 0 or height <= 0:
        return None
    x = _length(element.attrib.get("x"), canvas_width) if "x" in element.attrib else 0.0
    y = _length(element.attrib.get("y"), canvas_height) if "y" in element.attrib else 0.0
    if x is None or y is None:
        return None
    return x, y, x + width, y + height


def _intersects(bounds: tuple[float, float, float, float], viewport: tuple[float, float, float, float]) -> bool:
    return not (
        bounds[2] < viewport[0] or bounds[0] > viewport[2]
        or bounds[3] < viewport[1] or bounds[1] > viewport[3]
    )


def _clipped_bounds(
    bounds: tuple[float, float, float, float], viewport: tuple[float, float, float, float]
) -> tuple[float, float, float, float]:
    return (
        max(bounds[0], viewport[0]), max(bounds[1], viewport[1]),
        min(bounds[2], viewport[2]), min(bounds[3], viewport[3]),
    )


def _visible_bounds_meaningful(
    bounds: tuple[float, float, float, float],
    viewport: tuple[float, float, float, float] | None,
    use_area: bool,
) -> tuple[tuple[float, float, float, float], bool]:
    if viewport is None:
        return bounds, True
    clipped = _clipped_bounds(bounds, viewport)
    width = max(0.0, clipped[2] - clipped[0])
    height = max(0.0, clipped[3] - clipped[1])
    canvas_width = viewport[2] - viewport[0]
    canvas_height = viewport[3] - viewport[1]
    if use_area:
        meaningful = width * height >= canvas_width * canvas_height * 0.001
    else:
        meaningful = math.hypot(width, height) >= math.hypot(canvas_width, canvas_height) * 0.01
    return clipped, meaningful


def _intersection_area(
    first: tuple[float, float, float, float], second: tuple[float, float, float, float]
) -> float:
    width = max(0.0, min(first[2], second[2]) - max(first[0], second[0]))
    height = max(0.0, min(first[3], second[3]) - max(first[1], second[1]))
    return width * height


def _contains(outer: tuple[float, float, float, float], inner: tuple[float, float, float, float]) -> bool:
    return (
        outer[0] <= inner[0] and outer[1] <= inner[1]
        and outer[2] >= inner[2] and outer[3] >= inner[3]
    )


def _number_property(properties: Mapping[str, str], name: str, default: float) -> float | None:
    value = properties.get(name)
    if value is None:
        return default
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def _paint_value_visible(value: str) -> bool:
    candidate = value.strip().casefold()
    if candidate.startswith("url("):
        return True
    if candidate in {"none", "transparent"} or candidate.startswith("var("):
        return False
    parsed = parse_color(candidate)
    return parsed not in {None, "currentColor"} and parsed.alpha > 0


def _has_visible_paint(
    tag: str, has_area: bool, properties: Mapping[str, str]
) -> bool:
    opacity = _number_property(properties, "opacity", 1.0)
    fill_opacity = _number_property(properties, "fill-opacity", 1.0)
    stroke_opacity = _number_property(properties, "stroke-opacity", 1.0)
    stroke_width = _length(properties.get("stroke-width", "1"))
    if opacity is None or opacity <= 0:
        return False
    fill_visible = (
        has_area and fill_opacity is not None and fill_opacity > 0
        and _paint_value_visible(properties.get("fill", "black"))
    )
    stroke_visible = (
        stroke_opacity is not None and stroke_opacity > 0
        and stroke_width is not None and stroke_width > 0
        and _paint_value_visible(properties.get("stroke", "none"))
    )
    if tag in {"line", "polyline"}:
        return stroke_visible
    return fill_visible or stroke_visible


def _paint_eligibility_certain(properties: Mapping[str, str]) -> bool:
    for name in ("fill", "stroke"):
        value = properties.get(name, "").casefold()
        if "url(" in value or "var(" in value:
            return False
    return True


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
    canvas_area = (viewport[2] - viewport[0]) * (viewport[3] - viewport[1]) if viewport else None
    text_nodes = vector_nodes = raster_nodes = visible_raster_nodes = 0
    large_raster_nodes = full_canvas_raster_nodes = 0
    dominant_raster = False
    uncertain_dominant_raster = False
    stylesheet_uncertain = False
    paint_order = 0
    candidates: list[tuple[int, tuple[float, float, float, float], bool, bool]] = []
    dominant_rasters: list[tuple[int, tuple[float, float, float, float]]] = []
    inherited_names = {
        "fill", "fill-opacity", "stroke", "stroke-opacity", "stroke-width", "font-size"
    }

    def visit(
        element: Any,
        hidden: bool = False,
        non_rendering: bool = False,
        inherited_properties: Mapping[str, str] | None = None,
        transformed: bool = False,
        uncertain_effect: bool = False,
    ) -> None:
        nonlocal text_nodes, vector_nodes, raster_nodes, visible_raster_nodes
        nonlocal large_raster_nodes, full_canvas_raster_nodes, dominant_raster
        nonlocal uncertain_dominant_raster, stylesheet_uncertain, paint_order
        if not isinstance(element.tag, str) or not element.tag.startswith(f"{{{_SVG_NAMESPACE}}}"):
            raise ValueError("SVG1 child elements must use only the SVG namespace")
        tag = _local_name(element.tag).casefold()
        if tag in _BANNED_TAGS:
            raise ValueError(f"SVG1 must not contain {tag}")
        stylesheet_uncertain = _validate_resources(element, tag) or stylesheet_uncertain
        local_properties = _style_properties(element)
        properties = dict(inherited_properties or {})
        properties.update(local_properties)
        hidden = _is_hidden(element, hidden)
        non_rendering = non_rendering or tag in _NON_RENDERING_TAGS
        transform_value = local_properties.get("transform", element.attrib.get("transform", "none"))
        transformed = (
            transformed or str(transform_value).strip().casefold() not in {"", "none"}
            or (tag == "svg" and element is not root)
        )
        uncertain_effect = uncertain_effect or any(
            name in local_properties and local_properties[name].strip().casefold() not in {"", "none"}
            for name in ("clip-path", "mask", "filter")
        )
        structurally_rendered = not hidden and not non_rendering
        proof_eligible = structurally_rendered and not transformed
        order = paint_order
        if tag in _VECTOR_TAGS or tag in {"text", "image"}:
            paint_order += 1
        if tag == "text" and structurally_rendered:
            positive, meaningful, bounds = _text_measure(element, properties)
            visible = positive and bounds is not None and _has_visible_paint("text", True, properties)
            structurally_visible = visible and (
                transformed or viewport is None or _intersects(bounds, viewport)
            )
            if structurally_visible:
                text_nodes += 1
                if proof_eligible:
                    candidate_bounds, visible_meaningful = _visible_bounds_meaningful(bounds, viewport, True)
                    candidates.append((
                        order, candidate_bounds, meaningful and visible_meaningful,
                        not uncertain_effect and not any(
                            name in element.attrib
                            for name in ("dx", "dy", "rotate", "textLength", "lengthAdjust", "text-anchor")
                        ) and _paint_eligibility_certain(properties),
                    ))
        elif tag in _VECTOR_TAGS and structurally_rendered:
            positive, meaningful, bounds, has_area = _geometry_measure(element, tag, viewport)
            visible = positive and bounds is not None and _has_visible_paint(tag, has_area, properties)
            structurally_visible = visible and (
                transformed or viewport is None or _intersects(bounds, viewport)
            )
            if structurally_visible:
                vector_nodes += 1
        elif tag == "image":
            raster_nodes += 1
            if not hidden and not non_rendering:
                bounds = _image_bounds(element, viewport)
                if bounds is not None and (viewport is None or _intersects(bounds, viewport)):
                    if canvas_area is not None:
                        fraction = _intersection_area(bounds, viewport) / canvas_area
                        if transformed:
                            uncertain_dominant_raster = uncertain_dominant_raster or fraction >= 0.60
                        else:
                            visible_raster_nodes += 1
                            large_raster_nodes += int(fraction >= 0.25)
                            full_canvas_raster_nodes += int(fraction >= 0.95)
                            dominant_raster = dominant_raster or fraction >= 0.60
                            if fraction >= 0.60:
                                dominant_rasters.append((order, bounds))
        if tag in _VECTOR_TAGS and proof_eligible and visible and (
            viewport is None or _intersects(bounds, viewport)
        ):
            candidate_bounds, visible_meaningful = _visible_bounds_meaningful(bounds, viewport, has_area)
            candidates.append((
                order, candidate_bounds, meaningful and visible_meaningful,
                tag != "path" and not uncertain_effect and _paint_eligibility_certain(properties),
            ))
        child_properties = {name: properties[name] for name in inherited_names if name in properties}
        for child in element:
            visit(child, hidden, non_rendering, child_properties, transformed, uncertain_effect)

    visit(root)
    editable_nodes = text_nodes + vector_nodes
    meaningful_editable_nodes = 0
    if not stylesheet_uncertain and not uncertain_dominant_raster:
        for order, bounds, meaningful, eligibility_certain in candidates:
            occluded = any(
                raster_order > order and _contains(raster_bounds, bounds)
                for raster_order, raster_bounds in dominant_rasters
            )
            meaningful_editable_nodes += int(meaningful and eligibility_certain and not occluded)
    dominant_raster = dominant_raster or uncertain_dominant_raster
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
