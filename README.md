# vpype-gcode
Vpype plugin for gcode
See: https://github.com/abey79/vpype


Gcode vpype plugin. Write gcode files for the vpype pipeline.

* `gwrite` write gcode geometries to disk


# Installing
`$ pip install vpype-gcode`

# vpype gwrite --help

```Usage: vpype gwrite [OPTIONS] FILENAME

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
```

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
        'gcode':
            {
                'header': 'G20\nG17\nG90\n',
                'move': 'G00 X%.4f Y%.4f\n',
                'line': 'G01 X%.4f Y%.4f\n',
                'footer': 'M2\n',
                'scale': 0.2645833333333333  # G20 scale.
            },
        'gcode_relative':
            {
                'header': 'G20\nG17\nG91\n',
                'move': 'G00 X%.4f Y%.4f\n',
                'line': 'G01 X%.4f Y%.4f\n',
                'footer': 'M2\n',
                'relative': True,
                'scale': 0.2645833333333333  # G20 scale.
            }
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
            }
```


# Examples

## Convert SVG -> GCode

`vpype read butterfly.svg gwrite --version gcode butterfly.gcode`

Loads up a svg and writes it in default gcode.

`vpype begin grid -o 25 25 10 10 circle 0 0 100 end gwrite --version ninja -y --footer M99 test.gcode`

Here we are creating a grid of circles then we are `gwrite` in version `ninja` with a flipped y-axis and a footer of M99 rather than our default footer in `ninja` that is `M2\n`

Let's say our gcode is so different that it's an CSV file.

`vpype begin grid -o 25 25 10 10 circle 0 0 100 end gwrite --header "#Operation, X-value, Y-value\n" --move "Move, %d, %d\n" --line "Line-to, %d, %d\n" test.csv`

This produces:
```csv
#Operation, X-value, Y-value
Move, 26, 0
Line-to, 26, 0
Line-to, 26, -1
Line-to, 26, -2
Line-to, 26, -3
Line-to, 25, -4
Line-to, 25, -5
Line-to, 25, -6
...
```

Giving it a simplier example:
`vpype rect 0 0 100 100 gwrite --header "#Operation, X-value, Y-value\n" --move "Move, %d, %d\n" --line "Line-to, %d, %d\n"  test.csv`

```csv
#Operation, X-value, Y-value
Move, 0, 0
Line-to, 0, 100
Line-to, 100, 100
Line-to, 100, 0
Line-to, 0, 0
```

This produces a plain text CSV file of the rectangle.

Now using versions we could have done `--version csv` for this, but you can simply give the parts needed to perform your output.


# Formatting

The gwrite command gives you access to write to a variety of formats that fit the given outline. We're writing generic ascii. Since gcode can have more flavors than a Baskin Robbins™, it's best to simply draw broad strokes as to what ascii output should look like. Here we define the various elements without any regard to the gcode it will largely be producing.

```
<header>
  <prelayer>
    <preblock>
      <move>
      <line>
      <line>
      <line>
      <line>
    <postblock>
    <preblock>
      <move>
      <line>
      <line>
      <line>
      <line>
    <postblock>
    <preblock>
      <move>
      <line>
      <line>
      <line>
      <line>
    <postblock>
 <postlayer>
 <prelayer>
    <preblock>
      <move>
      <line>
      <line>
      <line>
      <line>
    <postblock>
    <preblock>
      <move>
      <line>
      <line>
      <line>
      <line>
    <postblock>
    <preblock>
      <move>
      <line>
      <line>
      <line>
      <line>
    <postblock>
 <postlayer>
<footer>
```

This is the secret sauce of gwrite, it writes generic ascii which can be themed as functional gcode.

For example if you write version `json`:
```python
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
            }
```

Sending our rectangle to Json:

`vpype rect 0 0 100 100 gwrite --version json test.json`

```json
{
	"Layer": {
		"Block": [
		{
			"X": 0,
			"Y": 0
		},
		{
			"X": 0,
			"Y": 100
		},
		{
			"X": 100,
			"Y": 100
		},
		{
			"X": 100,
			"Y": 0
		},
		{
			"X": 0,
			"Y": 0
		}
		],
	},
}
```

Strictly speaking json shouldn't have the last 2 commas there, but it's for demonstration purposes.
