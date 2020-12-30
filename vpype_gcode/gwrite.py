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
    "-o",
    "--premove",
    nargs=1,
    default=None,
    type=str,
    help="premove to write",
)
@click.option(
    "-O",
    "--postmove",
    nargs=1,
    default=None,
    type=str,
    help="postmove to write",
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
@vp.global_processor
def gwrite(document: vp.Document, filename: str, version: str,
           header: str,
           move: str,
           line: str,
           preblock: str,
           postblock: str,
           premove: str,
           postmove: str,
           prelayer: str,
           postlayer: str,
           footer: str,
           scale: float):
    writers = {
        'ninja':
            {
                'header': 'G20\nG17\nG90\n',
                'move': 'G00 X%.4f Y%.4f\n',
                'line': 'G01 X%.4f Y%.4f\n',
                'premove': 'M380\n',
                'postmove': 'M381\n',
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
            }

    }
    if version in writers:
        writer = writers[version]
        if 'header' in writer:
            header = writer['header']
        if 'move' in writer:
            move = writer['move']
        if 'line' in writer:
            line = writer['line']
        if 'preblock' in writer:
            preblock = writer['preblock']
        if 'postblock' in writer:
            postblock = writer['postblock']
        if 'premove' in writer:
            premove = writer['premove']
        if 'postmove' in writer:
            postmove = writer['postmove']
        if 'prelayer' in writer:
            prelayer = writer['prelayer']
        if 'postlayer' in writer:
            postlayer = writer['postlayer']
        if 'footer' in writer:
            footer = writer['footer']
        if 'scale' in writer:
            scale = writer['scale']
    with open(filename, 'w') as f:
        if header is not None:
            f.write(header)
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
                    y = v.imag
                    if first:
                        if premove is not None:
                            f.write(premove)
                        if move is not None:
                            f.write(move % (x, y))
                        if postmove is not None:
                            f.write(postmove)
                        first = False
                    else:
                        if line is not None:
                            f.write(line % (x, y))
                if postblock is not None:
                    f.write(postblock)
            if postlayer is not None:
                f.write(postlayer)
        if footer is not None:
            f.write(footer)

    return document


gwrite.help_group = "Gcode"
