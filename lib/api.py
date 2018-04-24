from . import core
import numpy
import cdp
import cdms2
import MV2

def generateNEXGrid(lats, lons, elements_corners):
    ncols = len(lats)
    mesh = numpy.zeros((ncols,2,4))
    params = []
    for index in range(ncols):
        params.append(core.Input(index, elements_corners, lats, lons))
    meshes = cdp.cdp_run.multiprocess(core.corners, params)
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

def rads2degrees(data, force=False):
    """ converting to degrees from radians if necessary"""
    if data.max()<7. or force:  # likely radians
        data = data / numpy.pi * 180.
    return data

def generateMPASGrid(lats, lons, lats_corners, lons_corners, delta=180.):

    lats = rads2degrees(lats)
    lons = rads2degrees(lons)
    lats_corners = rads2degrees(lats_corners)
    lons_corners = rads2degrees(lons_corners)

    # First clean up wrap effect for longitudes
    cont = True  # work not finished?
    iterations = 0
    while iterations<5 and cont:
        mx = lons_corners.max(axis=1)
        mn = lons_corners.min(axis=1)
        diff = mx - mn
        indices = numpy.argwhere(numpy.greater(diff,delta))
        mns = mn[indices]
        lons_bad = lons_corners[indices]
        mns = numpy.resize(mns,(lons_bad.shape))
        lons_corners[indices] = numpy.where(lons_corners[indices]>mns+delta,360.-lons_corners[indices],lons_corners[indices])
        if len(indices) == 0:
            cont = False
        iterations+=1

    # Now gen grid
    # Grid axes
    lat_axis = cdms2.auxcoord.TransientAuxAxis1D(lats)
    lat_axis.setBounds(lats_corners)

    lon_axis = cdms2.auxcoord.TransientAuxAxis1D(lons)
    lon_axis.setBounds(lons_corners)

    # Actual Grid
    grid = cdms2.gengrid.TransientGenericGrid(lat_axis,lon_axis)
    return grid


def applyGrid(data,grid):
    if not isinstance(data,numpy.ndarray):
        raise RuntimeError("input data to e3smnex's applyGrid function must be numpy array")

    if not isinstance(data,cdms2.avariable.AbstractVariable):
        data = MV2.array(data)

    axes = data.getAxisList()
    gridAxis = grid.getAxis(0)
    for i, ax in enumerate(axes):
        if len(ax) == len(gridAxis):
            axes[i] = gridAxis
    data.setAxisList(axes)
    data.setGrid(grid)
    return data
