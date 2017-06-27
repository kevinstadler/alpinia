#!/usr/bin/env python

import warnings
warnings.simplefilter("ignore")
from mapnik import Map, Coord, Projection, load_map, render_to_file
warnings.resetwarnings()

from argparse import ArgumentParser
parser = ArgumentParser(description='alpinia! comically exaggerated relief maps made easy')
parser.add_argument('--xml', '-x', default='alpinia.xml', help='mapnik style file (default: %(default)s)')
parser.add_argument('--size', type=int, nargs=2, default=[1920, 1080],
  help='output width and height in pixels. if one of them is 0, the other will be chosen so that the aspect of the map matches that of the input data file (default: %(default)s)')
parser.add_argument('--center', type=float, nargs=2,
  help='desired map center (latitude and longitude in degrees)')
parser.add_argument('--scale', type=float, help='desired map scale')

parser.add_argument('--hillshade', '-z', nargs='?', type=float, const=1.0,
  help="(re-)generate hillshading. input and output filename are extracted from the xml file's 'relief' and 'hillshade' layers respectively. optionally, specify the z exaggeration to use for the hillshading (default: %(const)s)")

parser.add_argument('output', nargs='?', default='alpinia.png', help='output filename (default: %(default)s)')

args = vars(parser.parse_args())

if args['hillshade']:

  # parse dem/hillshade filenames from xml
  from os.path import dirname, join
  import xml.dom.minidom as xml
  x = xml.parse(args['xml'])
  def getfilename(layername):
    dem = next(l for l in x.getElementsByTagName('Layer')
      if l.getAttribute('name') == layername)
    basename = next(p for p in dem.getElementsByTagName('Parameter')
      if p.getAttribute('name') == 'file').firstChild.data
    return join(dirname(args['xml']), basename)

  demfile = getfilename('dem')
  hillshadefile = getfilename('hillshade')

  # create hillshade
  from osgeo.gdal import DEMProcessing, DEMProcessingOptions, Open
#   alg --- 'ZevenbergenThorne' or 'Horn'
  print 'creating hillshading in', hillshadefile, '...'
  DEMProcessing(hillshadefile, demfile, 'hillshade',
    zFactor=args['hillshade'], combined=True)

m = Map(args['size'][0], args['size'][1])

load_map(m, args['xml'])

m.zoom_all()
if args['scale']:
  m.zoom(args['scale'] / m.scale_denominator())

if args['center']:
  mapcoordcenter = Projection(m.srs).forward(Coord(args['center'][1], args['center'][0]))
  center = m.view_transform().forward(mapcoordcenter)
  m.pan(int(center.x), int(center.y))

print 'scale denominator', m.scale_denominator()
print 'writing to', args['output']
render_to_file(m, args['output'])
