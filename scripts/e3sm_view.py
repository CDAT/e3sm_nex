#!/usr/bin/env python

from __future__ import print_function
import vcs
import cdp
import sys
import os
import e3smnex
import cdms2

# Read in data

# In[20]:


# datacurve = cdms2.open(os.path.join(vcs.sample_data,"sampleCurveGrid4.nc"))("sample")
# dataGen = cdms2.open(os.path.join(vcs.sample_data,"sampleGenGrid3.nc"))("sample")
#data = cdms2.open(os.path.expanduser("ne30_TS.nc"))("TS")
#data = cdms2.open(os.path.expanduser("ne120_TS.nc"))("TS")
data = cdms2.open(os.path.expanduser("case_scripts.cam.h1.0001-01-01-00000.nc"))("PS")[0]

#gridFile = cdms2.open(os.path.expanduser("ne11np4_latlon.nc"))
gridFile = cdms2.open(os.path.expanduser("ne30np4_latlon.091226.nc"))
#gridFile = cdms2.open(os.path.expanduser("ne120np4_latlon.100310.nc"))

# Get lat/lon

lats = gridFile("lat").filled()
lons = gridFile("lon").filled()
ncols = len(lats)
ec = gridFile("element_corners").filled()
#data = gridFile("lat")

# Generate Mesh

# In[21]:


generateMesh = True

if not os.path.exists(os.path.expanduser("mesh_vcs.nc")) or generateMesh is True: # Mesh file not present
    grid = e3smnex.generateGrid(ec, lats, lons)
    axes = data.getAxisList()
    print("AXES:",axes)
    print("grid axes:",grid.getAxisList())
    e3smnex.applyGrid(data,grid)

    f = cdms2.open("mesh_vcs.nc","w")
    f.write(data, id = "TS")
    f.close()

f = cdms2.open(os.path.expanduser("mesh_vcs.nc"))
mesh = f("TS")
#data = gridFile("lat")
axes = data.getAxisList()
axes[-1] = mesh.getAxisList()[-1]
data.setAxisList(axes)
data.setGrid(mesh.getGrid())


# Plot

# In[22]:


M = mesh.getGrid().getMesh()
print(M.shape)
print(clockWise(M[0]),True)
nClockwise = 0
for i in range(M.shape[0]):
    nClockwise += clockWise(M[i])
print("CLockwise: {} out of {}".format(nClockwise,M.shape[0]))
x = vcs.init(geometry=(2400,1600))
gm = vcs.createmeshfill()
print(data.getGrid().getMesh()[:,0].max())
print(data.getGrid().getMesh()[:,0].min())
print(data.getGrid().getMesh()[:,1].max())
print(data.getGrid().getMesh()[:,1].min())
gm.mesh = True
gm.wrap=[0.,0.]
gm.datawc_x1 =0.
gm.datawc_x2 = 360.
gm.datawc_y1=-90
gm.datawc_y2 = 90.
gm.wrap=[0., 360.]
#gm.fillareaopacity = [50,50,50,50,50,50,50,50,50,50]
gm.fillareaopacity = None
#gm.list()
x.clear()
x.plot(data,gm)


# In[7]:


x.png("crp")

