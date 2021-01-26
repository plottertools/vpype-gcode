# vpype-gcode
Vpype plugin to generate gcode and other text output.
See: https://github.com/abey79/vpype


Gcode vpype plugin. Write gcode files for the vpype pipeline. The output format can be customized by the user heavily to an extend that you can also output non gcode ascii text files. 

* `gwrite` write geometries as gcode to a file


# Installing
`$ pip install vpype-gcode`

# Usage

```
Usage: vpype gwrite [OPTIONS] OUTPUT

Options:
  -p, --profile TEXT  gcode writer profile from the vpype configuration file
                      subsection 'gwrite'

  --help              Show this message and exit.
```

You can provide the path to a file for the `OUTPUT` parameter or you can use `-` to output the result to the standard output.

# Profiles
This plugin supports different output profiles which configure the way the resulting output is formatted. Output profiles are flexible in a way that they can also be used to generate non gcode files, i.e. JSON or CSV files. 

## Predefined Profiles
There are several predefined output profiles as part of the release:

 - `ninja`
 - `gcode`
 - `gcode_relative`
 - `csv`
 - `json`

Check the [source code](vpype_gcode/bundled_configs.toml) for how these profiles are defined.

## Defining Your Own Profiles
In case you want to define your own output format to make the suit your needs, it is possible to define your own profiles either in `~/.vpype.toml` or any other file. In the latter case, you must instruct vpype to load the configuration using the [`--config`](https://vpype.readthedocs.io/en/latest/reference.html#cmdoption-vpype-c) global option.

Inside the configuration file you can specify a new output profile using the following format:
```
[gwrite.my_own_plotter]
unit = "mm"
invert_y = true
header = "M3 G21\n"
prelayer = "(Start Layer)\n"
preblock = "(Start Block)\n"
move = """G00 Z5
G00 X%.4f Y%.4f
M3 S1000
G4 P0.3
G01 Z1 F3500
"""
line = """G01 X%.4f Y%.4f Z1\n"""
postblock = """G00 Z 5.0000
M5 S0
G4 P0.5\n"""
footer = """M5
G00 X0.0000 Y0.0000
M2"""
```

You can use the following options inside a profile. You only need to provide the options where you need to change the default. If you want a newline character in an option, you can either use escape sequences (`\n`) or you use TOML multi line strings wrapped in `""""`.

### Output Control
- `unit`:  Defines the [vpype unit](https://vpype.readthedocs.io/en/stable/fundamentals.html#units) which should be used in the output format. Defaults to `mm`.
- `invert_x`: Inverts/Mirrors the output relative to the middle point of the x axis when set to `true`. Defaults to `false`.
- `invert_y`: Inverts/Mirrors the output relative to the middle point of the y axis when set to `true`. Defaults to `false`. This option can be helpful if your output does not have the x=0, y=0 coordinates at the top left (the default) but instead at the bottom left.
- `flip_x`: Flips the X axis by multiplying all values with -1 and therefore turning them negative when set to `true`. Defaults to `false`.
- `flip_y`: Flips the Y axis by multiplying all values with -1 and therefore turning them negative when set to `true`. Defaults to `false`.
- `relative`: Use relative coordinates (so the difference to the previous point) instead of absolute coordinates when set to `true`. Defaults to `false`

### Output Format
All of the options below default to an empty text which means no output is generated.
-  `header`: Output to be generated at the start of the file as a header
- `footer`: Output to be generated at the end of the file as a footer
- `preblock`: Output to be generated before a line is started
- `postblock`: Output to be generated after a line is finished.
- `move`: Output to be generated at the start of a line for its first coordinate pair.
- `line`: Output to be generated to all subsequent coordinate pairs of a line.

## Output structure
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
header = "#Operation, X-value, Y-value\n"
move = "Move, %f, %f\n"
line = "Line-to, %f, %f\n"
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
```
[gwrite.json]
header = "{\n"
footer = "}\n"
prelayer = "\t\"Layer\": {\n"
preblock = "\t\t\"Block\": [\n"
move = "\t\t{\n\t\t\t\"X\": %d,\n\t\t\t\"Y\": %d\n\t\t}"
line = ",\n\t\t{\n\t\t\t\"X\": %d,\n\t\t\t\"Y\": %d\n\t\t}"
postblock = "\n\t\t],\n"
postlayer = "\t},\n"
```
Using this profile, you can generate JSON for the rectangle:
`vpype rect 0 0 100 100 gwrite -p json test.json`

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


