#!/usr/bin/env python3
"""Optional final raster composition, without another generation-model call.

The user/Harness chooses the actual pixel slots and supplies source/permission
evidence. This tool does not download images, decide licenses, select slots or
infer whether an image depicts this study's results. Original files are retained.
"""
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path

from PIL import Image, ImageOps


def _path(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('paths must be nonempty run-relative strings')
    relative = Path(value)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('paths must stay inside the run')
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('symlink paths are forbidden: ' + value)
    resolved = current.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError('paths must stay inside the run')
    return resolved


def _decode(path):
    try:
        data = path.read_bytes()
        with Image.open(BytesIO(data)) as image:
            if getattr(image, 'n_frames', 1) != 1:
                raise ValueError('animated images require an explicitly selected still')
            image.load()
            result = image.convert('RGBA')
        return result, hashlib.sha256(data).hexdigest()
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ValueError(f'cannot decode image {path}: {exc}') from exc


def _ints(value, count, name):
    if not isinstance(value, list) or len(value) != count or any(type(n) is not int for n in value):
        raise ValueError(f'{name} needs {count} integer pixel coordinates')
    return value


def place_raster_insets(run, manifest='input/raster-inserts.json'):
    """Validate all inputs, then contain/cover paste and save a provenance receipt.

    Output is a new PNG; its sibling ``*.raster-receipt.json`` records the actual
    composition. Neither existing outputs nor any input file is overwritten.
    Source and permission strings are recorded declarations, not license checks.
    """
    supplied_root = Path(run).absolute()
    if supplied_root.is_symlink():
        raise ValueError('run must not be a symlink')
    root = supplied_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('run must be a directory')
    manifest_path = _path(root, manifest)
    data = json.loads(manifest_path.read_text())
    if not isinstance(data, dict):
        raise ValueError('manifest must be an object')
    canvas = _ints(data.get('canvas'), 2, 'canvas')
    if min(canvas) <= 0:
        raise ValueError('canvas dimensions must be positive')
    background = _path(root, data.get('background'))
    output = _path(root, data.get('output'))
    if output.suffix.lower() != '.png':
        raise ValueError('output must be a PNG path')
    receipt_path = output.with_suffix('.raster-receipt.json')
    _path(root, str(receipt_path.relative_to(root)))
    for path in (output, receipt_path):
        if path.exists():
            raise ValueError('output already exists: ' + str(path))
    image, background_hash = _decode(background)
    if list(image.size) != canvas:
        raise ValueError('canvas must equal the actual background dimensions')
    insets = data.get('insets')
    if not isinstance(insets, list) or not insets:
        raise ValueError('insets must be a nonempty list')
    prepared = []
    records = []
    inputs = {manifest_path, background}
    for inset in insets:
        if not isinstance(inset, dict):
            raise ValueError('each inset must be an object')
        for key in ('target_component_id', 'source', 'permission_evidence'):
            if not isinstance(inset.get(key), str) or not inset[key].strip():
                raise ValueError('inset requires nonempty ' + key)
        if not isinstance(inset.get('attribution', ''), str):
            raise ValueError('attribution must be text')
        path = _path(root, inset.get('path')); inputs.add(path)
        x, y, w, h = _ints(inset.get('box'), 4, 'box')
        if min(x, y) < 0 or min(w, h) <= 0 or x+w > canvas[0] or y+h > canvas[1]:
            raise ValueError('inset box must stay inside canvas')
        for old in records:
            ox, oy, ow, oh = old['requested_box']
            if x < ox+ow and x+w > ox and y < oy+oh and y+h > oy:
                raise ValueError('inset boxes overlap')
        fit = inset.get('fit', 'contain')
        if fit not in ('contain', 'cover'):
            raise ValueError('fit must be contain or cover')
        source, source_hash = _decode(path)
        if fit == 'contain':
            placed = ImageOps.contain(source, (w, h), Image.Resampling.LANCZOS)
            actual = [x+(w-placed.width)//2, y+(h-placed.height)//2, placed.width, placed.height]
        else:
            placed = ImageOps.fit(source, (w, h), Image.Resampling.LANCZOS, centering=(.5, .5))
            actual = [x, y, w, h]
        prepared.append((placed, actual[:2]))
        records.append({**inset, 'fit': fit, 'sha256': source_hash,
                        'original_size': list(source.size), 'requested_box': [x, y, w, h],
                        'actual_box': actual})
    if inputs.intersection((output, receipt_path)):
        raise ValueError('composition cannot overwrite any input')
    for placed, position in prepared:
        image.alpha_composite(placed, tuple(position))
    encoded = BytesIO(); image.save(encoded, format='PNG')
    png = encoded.getvalue()
    receipt = {'format': 'figfox-raster-inserts-v1',
               'step': 'optional final deterministic raster composition; no model call',
               'canvas': canvas, 'background': data['background'],
               'background_sha256': background_hash, 'output': data['output'],
               'output_sha256': hashlib.sha256(png).hexdigest(), 'insets': records}
    # All image, path, provenance and overlap checks precede any output writes.
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as handle:
        handle.write(png)
    with receipt_path.open('x') as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--manifest', default='input/raster-inserts.json')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(place_raster_insets(args.run, args.manifest), ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f'Raster composition failed: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
