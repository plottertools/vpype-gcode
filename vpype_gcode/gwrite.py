from __future__ import annotations

import collections
import copy
import sys
import typing
from pathlib import Path

import click
import vpype as vp
import vpype_cli

# Load the default config
vp.config_manager.load_config_file(str(Path(__file__).parent / "bundled_configs.toml"))


def invert_axis(document: vp.Document, invert_x: bool, invert_y: bool):
    """Inverts none, one or both axis of the document.
    This applies a relative scale operation with factors of 1 or -1
    on the two axis to all layers. The inversion happens relative to
    the center of the bounds.
    """

    bounds = document.bounds()
    if not bounds:
        return document

    origin = (
        0.5 * (bounds[0] + bounds[2]),
        0.5 * (bounds[1] + bounds[3]),
    )

    document.translate(-origin[0], -origin[1])
    document.scale(-1 if invert_x else 1, -1 if invert_y else 1)
    document.translate(origin[0], origin[1])

    return document


@click.command()
@click.argument("output", type=vpype_cli.FileType("w"))
@click.option(
    "-p",
    "--profile",
    type=vpype_cli.TextType(),
    help="gcode writer profile from the vpype configuration file subsection 'gwrite'",
)
@click.option(
    "-d",
    "--default",
    nargs=2,
    multiple=True,
    type=vpype_cli.TextType(),
    help="set a default value for a variable in case it is not found as property",
)
@vpype_cli.global_processor
def gwrite(
    document: vp.Document, output: typing.TextIO, profile: str, default: tuple[tuple[str, str]]
):
    """
    Write gcode or other ascii files for the vpype pipeline.

    The output format can be customized by the user heavily to an extent that you can also
    output most known non-gcode ascii text files.
    """
    gwrite_config = vp.config_manager.config["gwrite"]

    # If no profile was provided, try to use a default
    if not profile:
        # Try to get the default profile from the config
        if "default_profile" in gwrite_config:
            profile = gwrite_config["default_profile"]
        else:
            raise click.BadParameter(
                "no gwrite profile provided on the commandline and no default gwrite "
                + "profile configured in the vpype configuration. This can be done using "
                + 'the "default_default" key in the "gwrite" section'
            )

    # Check that the profile is actually there, we can be sure that the `gwrite`
    # part exists as there are several default profiles.
    if profile not in gwrite_config:
        profiles = [p for p in gwrite_config.keys() if p != "default_profile"]
        raise click.BadParameter(
            "gwrite profile "
            + profile
            + " not found in vpype configuration. Available gwrite profiles: "
            + ", ".join(profiles)
        )

    # Read the config for the profile from the main vpype
    config = gwrite_config[profile]
    document_start = config.get("document_start", None)
    document_end = config.get("document_end", None)
    layer_start = config.get("layer_start", None)
    layer_end = config.get("layer_end", None)
    layer_join = config.get("layer_join", None)
    line_start = config.get("line_start", None)
    line_end = config.get("line_end", None)
    line_join = config.get("line_join", None)
    segment_first = config.get("segment_first", None)
    segment = config.get("segment", None)
    segment_last = config.get("segment_last", None)
    unit = config.get("unit", "mm")

    offset_x = config.get("offset_x", 0.0)
    offset_y = config.get("offset_y", 0.0)
    scale_x = config.get("scale_x", 1.0)
    scale_y = config.get("scale_y", 1.0)

    # transform the document according to the desired parameters
    orig_document = document
    document = copy.deepcopy(document)  # do NOT affect the pipeline's document
    unit_scale = vp.convert_length(unit)
    document.scale(scale_x / unit_scale, scale_y / unit_scale)
    document.translate(offset_x, offset_y)

    invert_x = config.get("invert_x", False)
    invert_y = config.get("invert_y", False)
    # transform the document according to inversion parameters
    if invert_x or invert_y:
        document = invert_axis(document, invert_x, invert_y)

    # prepare
    current_layer: vp.LineCollection | None = None

    def write_template(template: str | None, **context_vars: typing.Any):
        """Expend a user-provided template using `format()`-style substitution."""
        if template is None:
            return
        dicts = [context_vars, document.metadata]
        if current_layer is not None:
            dicts.append(current_layer.metadata)
        dicts.append(dict(default))
        if "default_values" in config:
            dicts.append(config["default_values"])

        try:
            output.write(template.format_map(collections.ChainMap(*dicts)))
        except KeyError as exc:
            raise click.BadParameter(
                f"key {exc.args[0]!r} not found in context variables or properties"
            )

    # process file
    filename = output.name
    write_template(document_start, filename=filename)

    last_x = 0
    last_y = 0
    xx = 0
    yy = 0
    lastlayer_index = len(document.layers.values()) - 1

    for layer_index, (layer_id, layer) in enumerate(document.layers.items()):
        current_layer = layer  # used by write_template()

        write_template(
            layer_start,
            x=last_x,
            y=last_y,
            ix=xx,
            iy=yy,
            index=layer_index,
            index1=layer_index + 1,
            layer_index=layer_index,
            layer_index1=layer_index + 1,
            layer_id=layer_id,
            filename=filename,
        )
        lastlines_index = len(layer) - 1
        for lines_index, line in enumerate(layer):
            write_template(
                line_start,
                x=last_x,
                y=last_y,
                ix=xx,
                iy=yy,
                index=lines_index,
                index1=lines_index + 1,
                lines_index=lines_index,
                lines_index1=lines_index + 1,
                layer_index=layer_index,
                layer_index1=layer_index + 1,
                layer_id=layer_id,
                filename=filename,
            )

            segment_last_index = len(line) - 1
            for segment_index, seg in enumerate(line):
                x = seg.real
                y = seg.imag
                dx = x - last_x
                dy = y - last_y
                idx = int(round(x - xx))
                idy = int(round(y - yy))
                xx += idx
                yy += idy
                if segment_first is not None and segment_index == 0:
                    seg_write = segment_first
                elif segment_last is not None and segment_index == segment_last_index:
                    seg_write = segment_last
                else:
                    seg_write = segment

                write_template(
                    seg_write,
                    x=x,
                    y=y,
                    dx=dx,
                    dy=dy,
                    _x=-x,
                    _y=-y,
                    _dx=-dx,
                    _dy=-dy,
                    ix=xx,
                    iy=yy,
                    idx=idx,
                    idy=idy,
                    index=segment_index,
                    index1=segment_index + 1,
                    segment_index=segment_index,
                    segment_index1=segment_index + 1,
                    lines_index=lines_index,
                    lines_index1=lines_index + 1,
                    layer_index=layer_index,
                    layer_index1=layer_index + 1,
                    layer_id=layer_id,
                    filename=filename,
                )

                last_x = x
                last_y = y

            write_template(
                line_end,
                x=last_x,
                y=last_y,
                ix=xx,
                iy=yy,
                index=lines_index,
                index1=lines_index + 1,
                lines_index=lines_index,
                lines_index1=lines_index + 1,
                layer_index=layer_index,
                layer_index1=layer_index + 1,
                layer_id=layer_id,
                filename=filename,
            )

            if lines_index != lastlines_index:
                write_template(
                    line_join,
                    x=last_x,
                    y=last_y,
                    ix=xx,
                    iy=yy,
                    index=lines_index,
                    index1=lines_index + 1,
                    lines_index=lines_index,
                    lines_index1=lines_index + 1,
                    layer_index=layer_index,
                    layer_index1=layer_index + 1,
                    layer_id=layer_id,
                    filename=filename,
                )
        write_template(
            layer_end,
            x=last_x,
            y=last_y,
            ix=xx,
            iy=yy,
            index=layer_index,
            index1=layer_index + 1,
            layer_index=layer_index,
            layer_index1=layer_index + 1,
            layer_id=layer_id,
            filename=filename,
        )
        if layer_index != lastlayer_index:
            write_template(
                layer_join,
                x=last_x,
                y=last_y,
                ix=xx,
                iy=yy,
                index=layer_index,
                index1=layer_index + 1,
                layer_index=layer_index,
                layer_index1=layer_index + 1,
                layer_id=layer_id,
                filename=filename,
            )
        current_layer = None

    write_template(document_end, filename=filename)

    # handle info string
    info = config.get("info", None)
    if info:
        print(info, file=sys.stderr)

    return orig_document


gwrite.help_group = "Output"
