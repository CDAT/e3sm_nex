import core
import numpy
import cdp
import cdms2
import MV2

def generateGrid(elements_corners, lats, lons):
    ncols = len(lats)
    mesh = numpy.zeros((ncols,2,4))
    params = []
    for index in xrange(ncols):
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

def applyGrid(data,grid):
    if not isinstance(data,numpy.ndarray):
        raise RuntimeError("input data to e3smnex's applyGrid function must be numpy array")

    if not isinstance(data,cdms2.avariable.AbstractVariable):
        data = MV2.array(data)
    axes = data.getAxisList()
    axes[-1] = grid.getAxisList()[0]
    data.setAxisList(axes)
    data.setGrid(grid)
    return data
