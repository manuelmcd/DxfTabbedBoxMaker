import argparse
import tabbedboxmaker
import ezdxf.addons.r12writer
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
    
    output_file = box.cfg.output
    if output_file == '-':
        output_file = sys.stdout

    dxf_exporter = DxfExporter()

    with ezdxf.addons.r12writer(output_file) as dxf_file:
        for group in groups:
            for path in group:
                dxf_exporter.export(path, dxf_file)

def main():
    ap = argparse.ArgumentParser()
    tabbedboxmaker.add_args(ap)

    ap.add_argument(
        '--output', type=str, default='-',
        help="Output DXF filename (default '-' for STDOUT)"
    )
    ap.add_argument('length',type=float, help='Length of Box')
    ap.add_argument('width', type=float, help='Width of Box')
    ap.add_argument('height', type=float, help='Height of Box')
    ap.add_argument('thickness', type=float, help='Thickness of Material')

    args = ap.parse_args()
    
    effect(args.length, args.width, args.height, args.thickness, args)
