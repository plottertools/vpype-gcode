# vpype-embroidery
Vpype plugin for embroidery
See: https://github.com/abey79/vpype


Embroidery vpype plugin. Reads and Writes embroidery files for the vpype pipeline.

* `eread` load an embroidery into the pipeline
* `ewrite` write embroidery geometries to disk
* `efill` fill closed shapes in the document with a Eulerian fill.


# Installing
`$ pip install vpype-embroidery`

# Examples

## Complex fills

`vpype begin grid -o 25 25 10 10 circle 0 0 100 end efill show`

![epype](https://user-images.githubusercontent.com/3302478/101284648-fe3d0a00-3795-11eb-8a3b-5f340624195d.png)

## Convert SVG -> DST

`vpype read butterfly.svg ewrite butterfly.dst`

## Convert PES -> SVG

`vpype eread duck.pes write duck.svg`


# Supported Formats.

This uses `pyembroidery` for the backend so the formats supported are as follows:
https://github.com/EmbroidePy/pyembroidery

## Embroidery Formats
### Write

* .pes
* .dst
* .exp
* .jef
* .vp3
* .u01
* .pec
* .xxx
* .gcode

### Read
* .pes
* .dst
* .exp
* .jef
* .vp3
* .10o
* .100
* .bro
* .dat (barudan & sunstar)
* .dsb
* .dsz
* .emd
* .exy
* .fxy
* .gt
* .hus
* .inb
* .jpx
* .ksm
* .max
* .mit
* .new
* .pcd
* .pcm
* .pcq
* .pcs
* .pec
* .phb
* .phc
* .sew
* .shv
* .stc
* .stx
* .tap
* .tbf
* .u01
* .xxx
* .zxy
* .gcode

## Related Formats

We also write some miscellaneous formats

### Write
* .col : Color format.
* .edr : Color format.
* .inf : Color format.
* .pmv : Brother Stitch Format.

### Read
* .col : Color format.
* .edr : Color format.
* .inf : Color format.
* .pmv : Brother Stitch Format.

## Utility Formats:

### Write
* .csv : comma-separated values
* .json : JavaScript Object Notation
* .png : Portable Network Graphic
* .txt : text file.
* .svg : Scalable Vector Graphics

### Read
* .csv : comma-separated values
* .json : JavaScript Object Notation
