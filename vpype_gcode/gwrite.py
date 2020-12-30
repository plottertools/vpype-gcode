import click
import vpype as vp


@click.command()
@click.argument('filename', type=click.Path(exists=False))
@click.option(
    "-v",
    "--version",
    nargs=1,
    default='default',
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
    "-s",
    "--scale",
    nargs=1,
    default=None,
    type=float,
    help="scale factor",
)
@click.option(
    "-x",
    "--flip_x",
    is_flag=True,
    nargs=1,
    default=None,
    type=bool,
    help="flip_x from native",
)
@click.option(
    "-y",
    "--flip_y",
    is_flag=True,
    nargs=1,
    default=None,
    type=bool,
    help="flip_y from native",
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
           scale: float,
           flip_x: bool,
           flip_y: bool,
           relative: bool):
    writers = {
        'ninja':
            {
                'header': 'G20\nG17\nG90\n',
                'move': 'M380\nG00 X%.4f Y%.4f\nM381\n',
                'line': 'G01 X%.4f Y%.4f\n',
                'footer': 'M2\n',
                'scale': 0.2645833333333333  # G20 scale.
            },
        'default':
            {
                'header': 'G20\nG17\nG90\n',
                'move': 'G00 X%.4f Y%.4f\n',
                'line': 'G01 X%.4f Y%.4f\n',
                'footer': 'M2\n',
                'scale': 0.2645833333333333  # G20 scale.
            },
        'default_relative':
            {
                'header': 'G20\nG17\nG91\n',
                'move': 'G00 X%.4f Y%.4f\n',
                'line': 'G01 X%.4f Y%.4f\n',
                'footer': 'M2\n',
                'relative': True,
                'scale': 0.2645833333333333  # G20 scale.
            }
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
        if 'scale' in writer and scale is None:
            scale = writer['scale']
        if 'flip_x' in writer and flip_x is None:
            flip_x = writer['flip_x']
        if 'flip_y' in writer and flip_y is None:
            flip_y = writer['flip_y']
        if 'relative' in writer and relative is None:
            relative = writer['relative']
    if relative is None:
        relative = False
    if flip_x is None:
        flip_x = False
    if flip_y is None:
        flip_y = False
    with open(filename, 'w') as f:
        if header is not None:
            f.write(header)
        last_x = 0
        last_y = 0
        for layer in document.layers.values():
            if prelayer is not None:
                f.write(prelayer)
            for p in layer:
                if scale is not None:
                    m = p * scale
                else:
                    m = p
                first = True
                if preblock is not None:
                    f.write(preblock)
                for v in m:
                    x = v.real
                    if flip_x:
                        x = -x
                    y = v.imag
                    if flip_y:
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
