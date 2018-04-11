from __future__ import print_function
import cdms2
import numpy
import cdp

# Utilities Classes

class Input(object):
    def __init__(self, index, corners, lats, lons):
        self.index = index
        self.corners = corners
        self.lats =lats
        self.lons = lons

# Utilities Functions

def clockWise(pts,showPoints = False):
    n = pts.shape[-1]
    if showPoints: print(pts,pts.shape)
    clockwise = 0 
    for i in range(n):
        if i == n-1:
            j=0
        else:
            j=i+1
        if showPoints: print(i,j,pts[:,i])
        clockwise += (pts[0,j]+pts[0,i])*(pts[1,j]-pts[1,i])
    if showPoints: print("Result:",clockwise)
    if clockwise < 0:
        return False
    else:
        return True

def corners(param):
    index = param.index
    ec = param.corners
    lats = param.lats
    lons =param.lons
    cells_indices = numpy.argwhere(ec==(index+1))[:,1]
    lats_corners = []
    lons_corners = []
    for i in cells_indices:
        select = ec[...,i]-1
        lat = lats[select]
        lon = lons[select].tolist()
        counter = 0
        while(max(lon)-min(lon))>181. and counter<5:
            lon[lon.index(min(lon))]=360.-lon[lon.index(min(lon))]
            counter+=1
        if counter>8:
            lon = lons[select]
        lats_corners.append(numpy.average(lat))
        lons_corners.append(numpy.average(lon))
    if len(lats_corners)==3:  # special cases
        lats_corners.append(lats_corners[-1])
        lons_corners.append(lons_corners[-1])

    # Need to do the 181 magic again here!
    counter = 0
    while(max(lons_corners)-min(lons_corners)>181.) and counter<8:
        counter+=1
        lons_corners[lons_corners.index(min(lons_corners))] += 360.
    pts = numpy.array([lats_corners, lons_corners])
    if not clockWise(pts):
        lats_corners = lats_corners[::-1]
        lons_corners = lons_corners[::-1]
    return index, lats_corners, lons_corners


def generateGrid(elements_corners, lats, lons):
    ncols = len(lats)
    mesh = numpy.zeros((ncols,2,4))
    print("Constructing mesh cdp")
    params = []
    for index in xrange(ncols):
        params.append(Input(index, elements_corners, lats, lons))
    meshes = cdp.cdp_run.multiprocess(corners, params)
    for i in range(ncols):
        corners = meshes[i]
        index,l,L = corners
        mesh[index,0] = numpy.array(l)
        mesh[index,1] = numpy.array(L)
    lat_axis = cdms2.auxcoord.TransientAuxAxis1D(lats)
    lat_axis.id = "lat"
    lat_axis.setBounds(mesh[:,0])
    lon_axis = cdms2.auxcoord.TransientAuxAxis1D(lons)
    lon_axis.id = "lon"
    lon_axis.setBounds(mesh[:,1])
    grid = cdms2.gengrid.TransientGenericGrid(lat_axis,lon_axis)
    return grid

def applyGrid(data,grid):
    axes = data.getAxisList()
    axes[-1] = grid.getAxisList()[0]
    data.setAxisList(axes)
    data.setGrid(grid)
