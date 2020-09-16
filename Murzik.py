import pylab
import matplotlib.patches
import matplotlib.lines
import matplotlib.path

def drawLine (axes):
    x0 = 0
    y0 = 0

    x1 = 1
    y1 = 0.5

    x2 = 0.5
    y2 = 1.0

    line = matplotlib.lines.Line2D ([x0, x1, x2], [y0, y1, y2], color="k")
    axes.add_line (line)

    pylab.text (0.5, 1.1, "Line2D", horizontalalignment="center")

def drawPolygons (axes):
    polygon_1 = matplotlib.patches.Polygon ([(0, -0.75),
                                             (0, -1.25),
                                             (0.5, -1.25),
                                             (1, -0.75)])
    axes.add_patch (polygon_1)
    pylab.text (0.6, -0.7, "Polygon", horizontalalignment="center")


    polygon_2 = matplotlib.patches.Polygon ([(-0.5, 0),
                                             (-1, -0.5),
                                             (-1, -1),
                                             (-0.5, -1)],
                                            fill = False,
                                            closed = False)
    axes.add_patch (polygon_2)
    pylab.text (-1.0, -0.1, "Polygon", horizontalalignment="center")

def drawPath (axes):
    vertices = [(1.0, -1.75), (1.5, -1.5), (1.5, -1.0), (1.75, -0.75)]
    codes = [matplotlib.path.Path.MOVETO,
             matplotlib.path.Path.LINETO,
             matplotlib.path.Path.LINETO,
             matplotlib.path.Path.LINETO,
             ]

    path = matplotlib.patches.Path (vertices, codes)
    path_patch = matplotlib.patches.PathPatch (path, fill=False)
    axes.add_patch (path_patch)

    pylab.text (1.5, -1.75, "Path", horizontalalignment="center")

if __name__ == "__main__":
    pylab.xlim (-2, 2)
    pylab.ylim (-2, 2)
    pylab.grid()

    # Get the current axes
    axes = pylab.gca()
    axes.set_aspect("equal")

    drawLine (axes)
    drawPolygons (axes)
    drawPath (axes)

    pylab.show()