# DxfTabbedBoxMaker

[![PyPI - Version](https://img.shields.io/pypi/v/dxftabbedboxmaker.svg)](https://pypi.org/project/dxftabbedboxmaker)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dxftabbedboxmaker.svg)](https://pypi.org/project/dxftabbedboxmaker)

Generate DXF outlines for finger-jointed boxes, to be cut by a laser cutter or
CNC mill.

I started using Paul Hutchison's [TabbedBoxMaker](https://github.com/paulh-rnd/TabbedBoxMaker)
Inkscape plugin, exporting the generated SVG output to DXF before
generating G-code using [dxf2gcode](https://sourceforge.net/projects/dxf2gcode/).
However, I was frustrated by the difficulty in generating a DXF file
whose bounding box was just the cutout shapes (or even that contained the
shapes at the bottom left of the model space).

This package leverages a refactoring of Paul's inkscape plugin into a
[Python package](https://github.com/manuelmcd/TabbedBoxMaker)
which will get merged back into Paul's repository if he's willing:
https://github.com/paulh-rnd/TabbedBoxMaker/pull/56

Schroff box support is not carried through to this package.

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [Usage](#usage)

## Installation

```console
pip install dxftabbedboxmaker
```

## Usage

This package uses the inkscape plugin parameters largely unmodified,
just changing the box dimension paramters into positional (required)
parameters, as opposed to optional parameters.

The parameter values are mostly numeric and you should refer to the
[Inkscape plugin definition file](https://github.com/manuelmcd/TabbedBoxMaker/blob/master/boxmaker.inx)
for a description (e.g. to discover that `--boxtype 2` will generate
an open-top box).

The intent is that defaults should give reasonable results in most
cases.

### Examples

#### Open-top box 100x200x20 for 3mm board

```
dxftabbedboxmaker --boxtype 2 100 200 20 3 > sample1.dxf
```

## License

`dxftabbedboxmaker` is distributed under the terms of the [GPL-2.0-or-later](https://spdx.org/licenses/GPL-2.0-or-later.html) license.
