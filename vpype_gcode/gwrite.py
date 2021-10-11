import copy
import typing
from pathlib import Path

import click
import vpype as vp

# Load the default config
from vpype import LayerType

vp.CONFIG_MANAGER.load_config_file(str(Path(__file__).parent / "bundled_configs.toml"))


def invert_axis(
    document: vp.Document,
    invert_x: bool,
    invert_y: bool
):
    """ Inverts none, one or borth axis of the document.
    This applies a relative scale operation with factors of 1 or -1
    on the two axis to all layers. The invertion happens relative to
    the center of the bounds.
    """

    layer_ids = vp.multiple_to_layer_ids(LayerType.ALL, document)
    bounds = document.bounds(layer_ids)

    if not bounds:
        return document

    origin = (
        0.5 * (bounds[0] + bounds[2]),
        0.5 * (bounds[1] + bounds[3]),
    )

    for vid in layer_ids:
        lc = document[vid]
        lc.translate(-origin[0], -origin[1])
        lc.scale(-1 if invert_x else 1, -1 if invert_y else 1)
        lc.translate(origin[0], origin[1])

    return document

@click.command()
@click.argument("output", type=click.File("w"))
@click.option(
    "-p",
    "--profile",
    nargs=1,
    default=None,
    type=str,
    help="gcode writer profile from the vpype configuration file subsection 'gwrite'",
)
@vp.global_processor
def gwrite(document: vp.Document, output: typing.TextIO, profile: str):
    gwrite_config = vp.CONFIG_MANAGER.config["gwrite"]

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

    # process file
    filename = output.name
    if document_start is not None:
        output.write(document_start.format(filename=filename))
    last_x = 0
    last_y = 0
    xx = 0
    yy = 0
    lastlayer_index = len(document.layers.values()) - 1
    for layer_index, layer_id in enumerate(document.layers):
        layer = document.layers[layer_id]
        if layer_start is not None:
            output.write(
                layer_start.format(
                    index=layer_index,
                    index1=layer_index + 1,
                    layer_index=layer_index,
                    layer_index1=layer_index + 1,
                    layer_id=layer_id,
                    filename=filename,
                )
            )
        lastlines_index = len(layer) - 1
        for lines_index, line in enumerate(layer):
            if line_start is not None:
                output.write(
                    line_start.format(
                        index=lines_index,
                        index1=lines_index + 1,
                        lines_index=lines_index,
                        lines_index1=lines_index + 1,
                        layer_index=layer_index,
                        layer_index1=layer_index + 1,
                        layer_id=layer_id,
                        filename=filename,
                    )
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
                if seg_write is not None:
                    output.write(
                        seg_write.format(
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
                    )
                last_x = x
                last_y = y
            if line_end is not None:
                output.write(
                    line_end.format(
                        index=lines_index,
                        index1=lines_index + 1,
                        lines_index=lines_index,
                        lines_index1=lines_index + 1,
                        layer_index=layer_index,
                        layer_index1=layer_index + 1,
                        layer_id=layer_id,
                        filename=filename,
                    )
                )
            if line_join is not None and lines_index != lastlines_index:
                output.write(line_join)
        if layer_end is not None:
            output.write(
                layer_end.format(
                    index=layer_index,
                    index1=layer_index + 1,
                    layer_index=layer_index,
                    layer_index1=layer_index + 1,
                    layer_id=layer_id,
                    filename=filename,
                )
            )
        if layer_join is not None and layer_index != lastlayer_index:
            output.write(layer_join)
    if document_end is not None:
        output.write(document_end.format(filename=filename))
    output.flush()
    output.close()

    return orig_document


gwrite.help_group = "Output"
