# vpype-gcode
Vpype plugin for gcode
See: https://github.com/abey79/vpype


Gcode vpype plugin. Write gcode files for the vpype pipeline.

* `gwrite` write gcode geometries to disk


# Installing
`$ pip install vpype-gcode`

# vpype gwrite --help
Usage: vpype gwrite [OPTIONS] FILENAME

Options:
  -v, --version TEXT    version to write
  -h, --header TEXT     header to write
  -m, --move TEXT       move to write
  -l, --line TEXT       header to write
  -b, --preblock TEXT   preblock to write
  -B, --postblock TEXT  postblock to write
  -c, --prelayer TEXT   prelayer to write
  -C, --postlayer TEXT  postlayer to write
  -h, --footer TEXT     header to write
  -s, --scale FLOAT     scale factor
  -x, --flip_x          flip_x from native
  -y, --flip_y          flip_y from native
  -r, --relative        use relative coordinates
  --help                Show this message and exit.

# Versions
```python
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
```


# Examples

## Convert SVG -> GCode

`vpype read butterfly.svg gwrite --version default butterfly.gcode`

