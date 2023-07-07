from typing import List

import argparse
import math
import tabbedboxmaker
import ezdxf.addons.r12writer
import rpack
import sys

class DxfExporter(object):
    """Export AbstractShape objects as DXF"""

    def export(self, shape, dxfwriter) -> None:
        """Write the shape into the given dxfwriter"""
        try:
            export_method = 'export_' + shape.__class__.__name__
            exporter = getattr(self, export_method)
            exporter(shape, dxfwriter)
        except AttributeError:
            print(f'No exporter for shape type "{type(shape)}" (looking for "{export_method}")')
            raise

    def export_Circle(self, circle, dxfwriter) -> None:
        dxfwriter.add_circle(circle.centre, radius=circle.radius)

    def export_Path(self, path, dxfwriter) -> None:
        points = (
            [[path.initial_x, path.initial_y]] +
            [[s.args[0], s.args[1]] for s in path.segments]
        )

        dxfwriter.add_polyline_2d(points)



def effect(length: float, width: float, height: float, thickness: float, config: argparse.Namespace) -> None:
    box = tabbedboxmaker.TabbedBox(config)

    X = length + config.kerf
    Y = width + config.kerf
    Z = height + config.kerf

    # check input values mainly to avoid python errors
    # TODO restrict values to *correct* solutions
    # TODO restrict divisions to logical values
    error=0

    if min(X,Y,Z)==0:
      print('Error: Dimensions must be non zero')
      error=1
    if box.cfg.tab is not None:
        if min(X,Y,Z)<3*box.cfg.tab:
            print('Error: Tab size too large')
            error=1
        if box.cfg.tab<thickness:
            print('Error: Tab size too small')
            error=1
    if thickness==0:
      print('Error: Thickness is zero')
      error=1
    if thickness>min(X,Y,Z)/3: # crude test
      print('Error: Material too thick')
      error=1
    if box.cfg.kerf>min(X,Y,Z)/3: # crude test
      print('Error: Kerf too large')
      error=1
    if box.cfg.spacing>max(X,Y,Z)*10: # crude test
      print('Error: Spacing too large')
      error=1
    if box.cfg.spacing<box.cfg.kerf:
      print('Error: Spacing too small')
      error=1

    if error: exit()

    groups = box.make(X, Y, Z, thickness)

    if config.pack:
        pack(groups)

    output_file = box.cfg.output
    if output_file == '-':
        output_file = sys.stdout

    dxf_exporter = DxfExporter()

    with ezdxf.addons.r12writer(output_file) as dxf_file:
        for group in groups:
            for path in group:
                dxf_exporter.export(path, dxf_file)

def pack(lpl: List[List[tabbedboxmaker.Path]]):
    boundingboxes = []
    sizes = []
    bbpaths = []
    for pathlist in lpl:
        bb = pathlist[0].boundingbox()
        for path in pathlist:
            sbb = path.boundingbox()
            bb = (
                (min(sbb[0][0], bb[0][0]), min(sbb[0][1], bb[0][1])),
                (max(sbb[1][0], bb[1][0]), max(sbb[1][1], bb[1][1])),
            )

        width = int(math.ceil(bb[1][0] - bb[0][0]))
        height = int(math.ceil(bb[1][1] - bb[0][1]))
        boundingboxes.append(bb)
        sizes.append((width, height))
        bbp = tabbedboxmaker.Path(bb[0][0], bb[0][1]) # minx, miny
        bbp.add(tabbedboxmaker.LineSegment(bb[0][0], bb[1][1])) # minx, maxy
        bbp.add(tabbedboxmaker.LineSegment(bb[1][0], bb[1][1])) # maxx, maxy
        bbp.add(tabbedboxmaker.LineSegment(bb[1][0], bb[0][1])) # maxx, miny
        bbp.add(tabbedboxmaker.LineSegment(bb[0][0], bb[0][1])) # minx, miny
        bbpaths.append(bbp)
    #print(f"Adding boundingbox paths: {bbpaths}")
    #lpl.append(bbpaths)
    positions = rpack.pack(sizes)
    if len(positions) != len(boundingboxes) or len(positions) != len(lpl):
        raise Exception(f"Length mismatch {len(positions)}, {len(boundingboxes)}, {len(lpl)}")

    for i, pathlist in enumerate(lpl):
        dx = positions[i][0]-boundingboxes[i][0][0]
        dy = positions[i][1]-boundingboxes[i][0][1]
        for path in pathlist:
            path.translate(dx, dy)

def main():
    ap = argparse.ArgumentParser()
    tabbedboxmaker.TabbedBox.add_args(ap)

    ap.add_argument(
        '--output', type=str, default='-',
        help="Output DXF filename (default '-' for STDOUT)"
    )
    ap.add_argument(
        '--pack', action='store_true', help='Pack shapes'
    )
    ap.add_argument('length',type=float, help='Length of Box')
    ap.add_argument('width', type=float, help='Width of Box')
    ap.add_argument('height', type=float, help='Height of Box')
    ap.add_argument('thickness', type=float, help='Thickness of Material')

    args = ap.parse_args()

    effect(args.length, args.width, args.height, args.thickness, args)
