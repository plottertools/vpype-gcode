import click
from pathlib import Path
import vpype as vp
from vpype.layers import LayerType

# Load the default config
vp.CONFIG_MANAGER.load_config_file(str(Path(__file__).parent / "bundled_configs.toml"))


def invert_axis(
    document: vp.Document,
    invert_x: bool,
    invert_y: bool
):
    """ Inverts none, one or both axis of the document.

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
@click.argument('filename', type=click.Path(exists=False))
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
    move = config.get("move", None)
    line = config.get("line", None)
    preblock = config.get("preblock", None)
    postblock = config.get("postblock", None)
    prelayer = config.get("prelayer", None)
    postlayer = config.get("postlayer", None)
    footer = config.get("footer", None)
    unit = config.get("unit", "mm")

    relative = config.get("relative", False)
    negate_x = config.get("negate_x", False)
    negate_y = config.get("negate_y", False)
    invert_x = config.get("invert_x", False)
    invert_y = config.get("invert_y", False)

    scale = 1 / vp.convert_length(unit)

    if invert_x or invert_y:
        document = invert_axis(document, invert_x, invert_y)

    with open(filename, 'w') as f:
        if header is not None:
            f.write(header)
        last_x = 0
        last_y = 0
        for layer in document.layers.values():
            if prelayer is not None:
                f.write(prelayer)
            for p in layer:
                m = p * scale
                first = True
                if preblock is not None:
                    f.write(preblock)
                for v in m:
                    x = v.real
                    if negate_x:
                        x = -x
                    y = v.imag
                    if negate_y:
                        y = -y
                    if relative:
                        dx = x - last_x
                        dy = y - last_y
                        if first:
                            if move is not None:
                                f.write(move % (dx, dy))
                            first = False
                        else:
                            if line is not None:
                                f.write(line % (dx, dy))
                    else:
                        if first:
                            if move is not None:
                                f.write(move % (x, y))
                            first = False
                        else:
                            if line is not None:
                                f.write(line % (x, y))
                    last_x = x
                    last_y = y
                if postblock is not None:
                    f.write(postblock)
            if postlayer is not None:
                f.write(postlayer)
        if footer is not None:
            f.write(footer)

    return document


gwrite.help_group = "Gcode"
