# vpype-gcode
Vpype plugin to generate gcode and other text output.
See: https://github.com/abey79/vpype


Gcode vpype plugin. Write gcode files for the vpype pipeline. The output format can be customized by the user heavily to an extend that you can also output non gcode ascii text files. 

* `gwrite` write geometries as gcode to a file


# Installing
`$ pip install vpype-gcode`

# Usage

```
Usage: vpype gwrite [OPTIONS] FILENAME

Options:
  -p, --profile TEXT  gcode writer profile from the vpype configuration file
                      subsection 'gwrite'

  --help              Show this message and exit.
```

# Profiles
This plugin supports different output profiles which configure the way the resulting output is formatted. Output profiles are flexible in a way that they can also be used to generate non gcode files, i.e. JSON or CSV files. 

## Predefined Profiles
There are several predefined output profiles as part of the release:

 - `ninja`
 - `gcode`
 - `gcode_relative`
 - `csv`
 - `json`
 - `isvg`

Check the [source code](vpype_gcode/bundled_configs.toml) for how these profiles are defined.

## Defining Your Own Profiles
In case you want to define your own output format to make the suit your needs, it is possible to define your own profiles either in `~/.vpype.toml` or any other file. In the latter case, you must instruct vpype to load the configuration using the [`--config`](https://vpype.readthedocs.io/en/latest/reference.html#cmdoption-vpype-c) global option.

Inside the configuration file you can specify a new output profile using the following format:
```toml
[gwrite.my_own_plotter]
unit = "mm"
invert_y = true
document_start = "M3 G21\n"
layer_start = "(Start Layer)\n"
linecollection_start = "(Start Block)\n"
segment_first = """G00 Z5
G00 X{x:.4f}f Y{y:.4f}
M3 S1000
G4 P0.3
G01 Z1 F3500
"""
segment = """G01 X{x:.4f} Y{y:.4f} Z1\n"""
linecollection_end = """G00 Z 5.0000
M5 S0
G4 P0.5\n"""
document_end = """M5
G00 X0.0000 Y0.0000
M2"""
```

You can use the following options inside a profile. You only need to provide the options where you need to change the default. If you want a newline character in an option, you can either use escape sequences (`\n`) or you use TOML multi line strings wrapped in `""""`.


### Output Control
- `unit`:  Defines the [vpype unit](https://vpype.readthedocs.io/en/stable/fundamentals.html#units) which should be used in the output format. Defaults to `mm`.
- `invert_x`: Inverts/Mirrors the output relative to the middle point of the x axis when set to `true`. Defaults to `false`.
- `invert_y`: Inverts/Mirrors the output relative to the middle point of the y axis when set to `true`. Defaults to `false`. This option can be helpful if your output does not have the x=0, y=0 coordinates at the top left (the default) but instead at the bottom left.

### Output Format
All of the options below default to an empty text which means no output is generated. However, if `segment_first` or `segment_last` is omitted the code from `segment` is used. If there is only one segment. `segment_first` takes priority over `segment_last`.
- `document_start`: Output to be generated at the start of the file as a document_start
- `document_end`: Output to be generated at the end of the file as a document_end
- `layer_start`: Output to be generated before a layer is started
- `layer_end`: Output to be generated after a layer is finished.
- `layer_join`: Output to be generated between two layers.
- `linecollection_start`: Output to be generated before a linecollection is started
- `linecollection_end`: Output to be generated after a linecollection is finished.
- `linecollection_join`: Output to be generated between two linecollections.
- `segment_first`: Output to be generated at the first coordinate pair.
- `segment_last`: Output to be generated at the last coordinate pair.
- `segment`: Output to be generated to all subsequent coordinate pairs of a linecollection.

### Segment formatting
`gwrite` uses `.format()` encoding which means that data elements must be encasulated in `{}` brackets. This provides a particular syntax token which differs from between elements.
For example every element except `layer_join` and `segment_join` accepts the value of `index`. You would encode that in the text as `{index:d}` the d denotes an integer value. If you need to have a `{` value in your text you would encode that as `{{` likewise you would encode a `}` as `}}`.
- `layer_start`: Accepts `index` the current layer number.
- `layer_end`: Accepts `index` the current layer number.
- `linecollection_start`: Accepts `index` the current linecollection number.
- `linecollection_end`: Accepts `index` the current linecollection number.
  
The segments accept a lot of values that may be useful statistics for various formats:
* `index`: index of the particular coordinate pair. eg `{index:d}`
* `x` absolute position x in floating point number. eg `{x:.4f}`
* `y` absolute position y in floating point number. eg `{y:g}`
* `dx` relative position x in floating point number. eg `{dx:f}`
* `dy` relative position y in floating point number. eg `{dy:.2f}`
* `_x` negated absolute position x in floating point number. eg `{_x:.4f}`
* `_y` negated absolute position y in floating point number. eg `{_y:g}`
* `_dx` negated relative position x in floating point number. eg `{_dx:f}`
* `_dy` negated relative position y in floating point number. eg `{_dy:.2f}`
* `ix` absolute position x in integer number. eg `{ix:d}`
* `iy` absolute position y in integer number. eg `{iy:d}`
* `idx` relative position x in integer number. eg `{idx:d}`
* `idy` relative position y in integer number. eg `{idy:d}`

Note: `idx` and `idy` are properly guarded against compounding fractional rounding errors. Moving 0.1 units 1000 times results in a location 100 units away and not zero.


## Output structure
The gwrite command gives you access to write to a variety of formats that fit the given outline. We're writing generic ascii. Since gcode can have more flavors than a Baskin Robbins™, it's best to simply draw broad strokes as to what ascii output should look like. Here we define the various elements without any regard to the gcode it will largely be producing.
```
<document_start>
  <layer_start>
    <linecollection_start>
      <segment_first>
      <segment>
      <segment>
      <segment>
      <segment>
      <segment_last>
    <linecollection_end>
    <linecollection_start>
      <segment_first>
      <segment>
      <segment>
      <segment>
      <segment>
      <segment_last>
    <linecollection_end>
    <linecollection_start>
      <segment_first>
      <segment>
      <segment>
      <segment>
      <segment>
      <segment_last>
    <linecollection_end>
 <layer_end>
 <layer_start>
    <linecollection_start>
      <segment_first>
      <segment>
      <segment>
      <segment>
      <segment>
      <segment_last>
    <linecollection_end>
    <linecollection_start>
      <segment_first>
      <segment>
      <segment>
      <segment>
      <segment>
      <segment_last>
    <linecollection_end>
    <linecollection_start>
      <segment_first>
      <segment>
      <segment>
      <segment>
      <segment>
      <segment_last>
    <linecollection_end>
 <layer_end>
<document_end>
```
## Default Profile
To prevent having to provide the profile on every invocation of the gcode plugin, you can define a default profile which will be used when no other profile is provided on the command line. You can do so by setting the `default_profile` configuration variable inside the `gcode` section of the vpype configuration file:
```
[gcode]
default_profile = "gcode"
```

# Examples
## Convert SVG -> GCode
Loads up a svg and writes it in default gcode.:
`vpype read butterfly.svg gwrite --profile gcode butterfly.gcode`

Create a grid of circles, then we are `gwrite` using the `ninja` profile:
`vpype begin grid -o 25 25 10 10 circle 0 0 100 end gwrite --profile ninja test.gcode`


## Convert SVG -> CSV
The `csv` profile is bundled with this package and defined as follows:
```
[gwrite.csv]
document_start = "#Operation, X-value, Y-value\n"
segment_first = "Move, %f, %f\n"
segment = "Line-to, %f, %f\n"
```

Using this profile you can generate a CSV for a given input into vpype:
`vpype begin grid -o 25 25 10 10 circle 0 0 100 end gwrite -p csv test.csv`

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
Giving it a simpler example, this produces a plain text CSV file of the rectangle.
`vpype rect 0 0 100 100 gwrite -p csv test.csv`

```csv
#Operation, X-value, Y-value
Move, 0, 0
Line-to, 0, 100
Line-to, 100, 100
Line-to, 100, 0
Line-to, 0, 0
```
This is the secret sauce of gwrite, it writes generic ascii which can be themed as functional gcode.

## Convert SVG -> JSON
The `json` profile is already bundled with this package. It is defined as following:
```toml
[gwrite.json]
document_start = "{{"
document_end = "}}\n"
linecollection_join = ","
layer_join = ","
layer_start = "\n\t\"Layer\": {{"
layer_end = "\t}}\n"
linecollection_start = "\n\t\t\"LineCollection{index:d}\": [\n"
linecollection_end = "\n\t\t]"
segment = "\t\t{{\n\t\t\t\"X\": {ix:d},\n\t\t\t\"Y\": {iy:d}\n\t\t}},\n"
segment_last = "\t\t{{\n\t\t\t\"X\": {ix:d},\n\t\t\t\"Y\": {iy:d}\n\t\t}}"
```
Using this profile, you can generate JSON for the rectangle:
`vpype rect 0 0 100 100 gwrite -p json test.json`

```json
{
	"Layer": {
		"LineCollection0": [
		{
			"X": 0,
			"Y": 0
		},
		{
			"X": 0,
			"Y": 26
		},
		{
			"X": 26,
			"Y": 26
		},
		{
			"X": 26,
			"Y": 0
		},
		{
			"X": 0,
			"Y": 0
		}
		]	}
}
```

Which is valid JSON.


