import click
import vpype as vp
from vpype.layers import LayerType

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
        logging.warning("no geometry available, cannot compute origin")
        raise ValueError

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
    "-v",
    "--version",
    nargs=1,
    default=None,
    type=str,
    help="version to write",
)
@click.option(
    "-h",
    "--header",
    nargs=1,
    default=None,
    type=str,
    help="header to write",
)
@click.option(
    "-m",
    "--move",
    nargs=1,
    default=None,
    type=str,
    help="move to write",
)
@click.option(
    "-l",
    "--line",
    nargs=1,
    default=None,
    type=str,
    help="header to write",
)
@click.option(
    "-b",
    "--preblock",
    nargs=1,
    default=None,
    type=str,
    help="preblock to write",
)
@click.option(
    "-B",
    "--postblock",
    nargs=1,
    default=None,
    type=str,
    help="postblock to write",
)
@click.option(
    "-c",
    "--prelayer",
    nargs=1,
    default=None,
    type=str,
    help="prelayer to write",
)
@click.option(
    "-C",
    "--postlayer",
    nargs=1,
    default=None,
    type=str,
    help="postlayer to write",
)
@click.option(
    "-h",
    "--footer",
    nargs=1,
    default=None,
    type=str,
    help="header to write",
)
@click.option(
    "-u",
    "--unit",
    nargs=1,
    default="px",
    type=str,
    help="unit for coordinates",
)
@click.option(
    "--negate_x",
    is_flag=True,
    nargs=1,
    default=None,
    type=bool,
    help="change the sign of the x coordinates by multiplying them with -1",
)
@click.option(
    "--negate_y",
    is_flag=True,
    nargs=1,
    default=None,
    type=bool,
    help="change the sign of the y coordinates by multiplying them with -1",
)
@click.option(
    "--invert_x",
    is_flag=True,
    nargs=1,
    default=None,
    type=bool,
    help="invert or mirror all points on the middle of the x axis",
)
@click.option(
    "--invert_y",
    is_flag=True,
    nargs=1,
    default=None,
    type=bool,
    help="invert or mirror all points on the middle of the y axis",
)
@click.option(
    "-r",
    "--relative",
    is_flag=True,
    nargs=1,
    default=None,
    type=bool,
    help="use relative coordinates",
)
@vp.global_processor
def gwrite(document: vp.Document, filename: str, version: str,
           header: str,
           move: str,
           line: str,
           preblock: str,
           postblock: str,
           prelayer: str,
           postlayer: str,
           footer: str,
           unit: str,
           negate_x: bool,
           negate_y: bool,
           invert_x: bool,
           invert_y: bool,
           relative: bool):
    if version is None and header is None and move is None \
            and line is None and preblock is None and postblock is None \
            and prelayer is None and postlayer is None and footer is None:
        version = "gcode"
    writers = {
        'ninja':
            {
                'header': 'G20\nG17\nG90\n',
                'move': 'M380\nG00 X%.4f Y%.4f\nM381\n',
                'line': 'G01 X%.4f Y%.4f\n',
                'footer': 'M2\n',
                'unit': 'mm'
            },
        'gcode':
            {
                'header': 'G20\nG17\nG90\n',
                'move': 'G00 X%.4f Y%.4f\n',
                'line': 'G01 X%.4f Y%.4f\n',
                'footer': 'M2\n',
                'unit': 'mm'
            },
        'gcode_relative':
            {
                'header': 'G20\nG17\nG91\n',
                'move': 'G00 X%.4f Y%.4f\n',
                'line': 'G01 X%.4f Y%.4f\n',
                'footer': 'M2\n',
                'relative': True,
                'unit': 'mm'
            },
        'csv':
            {
                'header': "#Operation, X-value, Y-value\n",
                'move': "Move, %f, %f\n",
                'line': "Line-to, %f, %f\n"
            },
        'json':
            {
                'header': '{\n',
                'footer': '}\n',
                'prelayer': '\t"Layer": {\n',
                'preblock': '\t\t"Block": [\n',
                'move': '\t\t{\n\t\t\t"X": %d,\n\t\t\t"Y": %d\n\t\t}',
                'line': ',\n\t\t{\n\t\t\t"X": %d,\n\t\t\t"Y": %d\n\t\t}',
                'postblock': '\n\t\t],\n',
                'postlayer': '\t},\n',
            }  # Json is nearly validated has extra ',' on the last post-block and post-layer.

    }
    if version in writers:
        writer = writers[version]
        if 'header' in writer and header is None:
            header = writer['header']
        if 'move' in writer and move is None:
            move = writer['move']
        if 'line' in writer and line is None:
            line = writer['line']
        if 'preblock' in writer and preblock is None:
            preblock = writer['preblock']
        if 'postblock' in writer and postblock is None:
            postblock = writer['postblock']
        if 'prelayer' in writer and prelayer is None:
            prelayer = writer['prelayer']
        if 'postlayer' in writer and postlayer is None:
            postlayer = writer['postlayer']
        if 'footer' in writer and footer is None:
            footer = writer['footer']
        if 'unit' in writer and unit is None:
            unit = writer['unit']
        if 'negate_x' in writer and negate_x is None:
            negeate_x = writer['negate_x']
        if 'negate_y' in writer and negate_y is None:
            negate_y = writer['negate_y']
        if 'invert_x' in writer and invert_x is None:
            invert_x = writer['invert_x']
        if 'invert_y' in writer and invert_y is None:
            invert_y = writer['invert_y']
        if 'relative' in writer and relative is None:
            relative = writer['relative']
    if header is not None:
        header = header.replace('\\n', '\n')
    if move is not None:
        move = move.replace('\\n', '\n')
    if line is not None:
        line = line.replace('\\n', '\n')
    if preblock is not None:
        preblock = preblock.replace('\\n', '\n')
    if postblock is not None:
        postblock = postblock.replace('\\n', '\n')
    if prelayer is not None:
        prelayer = prelayer.replace('\\n', '\n')
    if postlayer is not None:
        postlayer = postlayer.replace('\\n', '\n')
    if footer is not None:
        footer = footer.replace('\\n', '\n')
    if relative is None:
        relative = False
    if negate_x is None:
        negate_x = False
    if negate_y is None:
        negate_y = False
    if invert_x is None:
        invert_x = False
    if invert_y is None:
        invert_y = False

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
