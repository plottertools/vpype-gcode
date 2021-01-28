import click
from pathlib import Path
import vpype as vp
from vpype.layers import LayerType

# Load the default config
vp.CONFIG_MANAGER.load_config_file(str(Path(__file__).parent / "bundled_configs.toml"))


def invert_axis(document: vp.Document, invert_x: bool, invert_y: bool):
    """Inverts none, one or both axis of the document.

    This applies a relative scale operation with factors of 1 or -1
    on the two axis to all layers. The inversion happens relative to
    the center of the bounds.
    """

    layer_ids = vp.multiple_to_layer_ids(LayerType.ALL, document)
    bounds = document.bounds(layer_ids)

    if not bounds:
        raise ValueError("no geometry available, cannot compute origin")

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
@click.argument("filename", type=click.Path(exists=False))
@click.option(
    "-p",
    "--profile",
    nargs=1,
    default=None,
    type=str,
    help="gcode writer profile from the vpype configuration file subsection 'gwrite'",
)
@vp.global_processor
def gwrite(document: vp.Document, filename: str, profile: str):
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
    header = config.get("header", None)
    firstsegment = config.get("firstsegment", None)
    segment = config.get("segment", None)
    lastsegment = config.get("lastsegment", None)
    prelayer = config.get("prelayer", None)
    postlayer = config.get("postlayer", None)
    layerjoin = config.get("layerjoin", None)
    preline = config.get("preline", None)
    postline = config.get("postline", None)
    linejoin = config.get("linejoin", None)
    footer = config.get("footer", None)
    unit = config.get("unit", "mm")

    invert_x = config.get("invert_x", False)
    invert_y = config.get("invert_y", False)

    scale = 1 / vp.convert_length(unit)

    if invert_x or invert_y:
        document = invert_axis(document, invert_x, invert_y)

    with open(filename, "w") as f:
        if header is not None:
            f.write(header.format(filename=filename))
        last_x = 0
        last_y = 0
        xx = 0
        yy = 0
        lastlayer_index = len(document.layers.values()) - 1
        for layer_index, layer in enumerate(document.layers.values()):
            if prelayer is not None:
                f.write(prelayer.format(index=layer_index))
            lastlines_index = len(layer) - 1
            for lines_index, lines in enumerate(layer):
                lines_scaled = lines * scale
                if preline is not None:
                    f.write(preline.format(index=lines_index))
                lastsegment_index = len(lines_scaled) - 1
                for segment_index, seg in enumerate(lines_scaled):
                    x = seg.real
                    y = seg.imag
                    dx = x - last_x
                    dy = y - last_y
                    idx = int(round(x - xx))
                    idy = int(round(y - yy))
                    xx += idx
                    yy += idy
                    if firstsegment is not None and segment_index == 0:
                        seg_write = firstsegment
                    elif lastsegment is not None and segment_index == lastsegment_index:
                        seg_write = lastsegment
                    else:
                        seg_write = segment
                    f.write(
                        seg_write.format(
                            x=x,
                            y=y,
                            dx=dx,
                            dy=dy,
                            _x=-x,
                            _y=-y,
                            _dx=dx,
                            _dy=dy,
                            ix=xx,
                            iy=yy,
                            idx=idx,
                            idy=idy,
                            index=segment_index,
                        )
                    )
                    last_x = x
                    last_y = y
                if postline is not None:
                    f.write(postline.format(index=lines_index))
                if linejoin is not None and lines_index != lastlines_index:
                    f.write(linejoin)
            if postlayer is not None:
                f.write(postlayer.format(index=layer_index))
            if layerjoin is not None and layer_index != lastlayer_index:
                f.write(layerjoin)
        if footer is not None:
            f.write(footer.format(filename=filename))

    return document


gwrite.help_group = "Gcode"
