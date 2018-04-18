#!/usr/bin/env python

from __future__ import print_function
import vcs
import cdp
import sys
import os
import e3sm_nex
import cdms2
import warnings
import numpy
import curses
import ast


def input_char(message):
    try:
        win = curses.initscr()
        win.clear()
        win.addstr(0, 0, message)
        while True: 
            ch = win.getch()
            if ch in range(32, 127): break
            time.sleep(0.05)
    except:
        raise
    finally:
        curses.endwin()
    return chr(ch)

parser = cdp.cdp_parser.CDPParser()

parser.add_argument("-M", "--mesh",help="mesh file either for input or for file where mesh info will be stored once generated. We try to detect ne120 and ne30, for which mesh files are provided", default=None)
parser.add_argument("-m", "--mesh_variable", default="mesh", help="variable containing mesh (in mesh file)")
parser.add_argument("-v","--variable",help="variable to view")
parser.add_argument("-i","--input_file",help="file containing variable to view")
parser.add_argument("-g", "--grid",help="e3sm grid file", default=None)
parser.add_argument("--grid_type", choices=("nex","mpas"), help="Grid file type nex (nex-like i.e element_corners) or mpas (mpas like grid_corners)", default=None)
parser.add_argument("-e", "--element_corners",default=None, help="variable containing element_corners in grid file")
parser.add_argument("--longitude_corners",default=None, help="variable containing longitude corners in grid file")
parser.add_argument("--latitude_corners",default=None, help="variable containing latitude corners in grid file")
parser.add_argument("-l", "--lats_variable",default=None, help="variable containing latitudes in grid file")
parser.add_argument("-L", "--lons_variable",default=None, help="variable containing longitudes in grid file")
parser.add_argument("--lon1",help="first longitude",default=0.)
parser.add_argument("--lon2",help="last longitude",default=360.)
parser.add_argument("--lat1",help="first latitude",default=-90.)
parser.add_argument("--lat2",help="last latitude",default=90.)
parser.add_argument("--time_index", help="time index to plot",default=0)
parser.add_argument("--level_index", help="leve index to plot",default=0)
parser.add_argument("--show_mesh", help="draw the mesh on plot", action="store_true", default=False)
parser.add_argument("--missing_color", help="color of missing values on plot", action="store_true", default="lightgrey")
parser.add_argument("--levels",default=None,help="levels to use",type=ast.literal_eval)
parser.add_argument("--colors",default=None,help="color indices to use",type=ast.literal_eval)
parser.add_argument("--output_type",help="output type",choices=("screen","s","png","pdf","postscript","nc"), default="screen")
parser.add_argument("--output",help="output file name")
parser.add_argument("--geometry",help="geometry for output",default="800x600")
parser.add_argument("-c","--colormap",default="viridis",help="colormap to use")
parser.add_argument("-C","--cleanup_data",default=False, action="store_true", help="apply quick cleanup on data where abs value is > 1.e20")
parser.add_argument("-P","--projection",default="default",help="projection type",choices=("default", "lambert", "robinson", "mollweide", "polar", "orthographic"))
P = parser.get_parameters()[0]

if not os.path.exists(P.input_file):
    raise RuntimeError("Could not find input file {}".format(P.input_file))
infile = cdms2.open(P.input_file)
if not P.variable in infile.variables:
    raise RuntimeError("Could not find variable {} in file {}".format(P.variable,P.input_file))
data = infile[P.variable]

# Test for mesh on data
genGrid = False
try:
    grid = data.getGrid()
    M = grid.getMesh()
except Exception as err:
    # No mesh, trying to open the mesh file
    if P.mesh is None:
        if data.shape[-1] == 777602 and P.grid is None:
            P.mesh = os.path.join(sys.prefix,"share","e3smnex","e3sm_mesh_ne120.nc")
            warnings.warn("You did not provide a mesh file, but it appear you are trying to view an ne120, we are using the provided ne120 mesh file at {}".format(P.mesh))
        elif data.shape[-1] == 48602 and P.grid is None:
            P.mesh = os.path.join(sys.prefix,"share","e3smnex","e3sm_mesh_ne30.nc")
            warnings.warn("You did not provide a mesh file, but it appear you are trying to view an ne30, we are using the provided ne30 mesh file at {}".format(P.mesh))
        else:
            P.mesh = "e3sm_mesh.nc"
    if not os.path.exists(P.mesh):
        if P.grid is None:
            warnings.warn("could not get mesh from data and mesh file {} cannot be located we will try to generate the grid".format(P.mesh))
        genGrid = True
    else:
        with cdms2.open(P.mesh) as f:
            if not P.mesh_variable in f.variables:
                warnings.warn("could not find mesh variable {} in mesh file {}. We will try to generate the grid".format(P.mesh_variable, P.mesh))
                genGrid = True
            else:
                print("Reading mesh from variable '{}' in {}".format(P.mesh_variable, P.mesh))
                grid = f(P.mesh_variable).getGrid()
                try:
                    grid.getMesh()
                except:
                    warnings.warn("Could not get mesh information out of grid read, will regenerate the mesh info")
                    genGrid = True

if genGrid: # We need to generate the grid
    if P.grid is None or not os.path.exists(P.grid):
        raise RuntimeError("We need to generate the mesh, but could not open grid file {}".format(P.grid))

    # Load data from grid file
    with cdms2.open(P.grid) as f:
        if P.grid_type is None:
            # Not passed by user we need to figure it
            if P.element_corners is not None:
                P.grid_type = "nex"
            elif P.longitude_corners is not None:
                P.grid_type = "mpas"
            else: # Ok user gave us no hint via grid_type or corner variables...
                if "element_corners" in f.variables:
                    P.grid_type = "nex"
                elif "grid_corner_lat" in f.variables and "grid_corner_lon" in f.variables:
                    P.grid_type = "mpas"
                else:
                    raise RuntimeError("Could not determine automagically grid_file type for grid file {}".format(P.grid))

        if P.grid_type == "nex":
            if P.element_corners is None:
                if "element_corners" in f.variables:
                    P.element_corners = "element_corners"
                else:
                    RuntimeError("could not figure out name of element_corners variable in grid file {}".format(P.grid))

            if P.element_corners not in f.variables:
                raise RuntimeError("Could not get elements corner variable ({}) from grid file {}".format(P.element_corners, P.grid))
            ec = f(P.element_corners).filled()

            if P.lats_variable is None:
                if "lat" in f.variables:
                    P.lats_variable = "lat"
                else:
                    RuntimeError("could not figure out name of latitudes variable in grid file {}".format(P.grid))
            if P.lats_variable not in f.variables:
                raise RuntimeError("Could not get latitudes variable ({}) from grid file {}".format(P.lats_variable, P.grid))
            lats = f(P.lats_variable).filled()
            if P.lons_variable is None:
                if "lon" in f.variables:
                    P.lons_variable = "lon"
                else:
                    RuntimeError("could not figure out name of longitudes variable in grid file {}".format(P.grid))
            if P.lons_variable not in f.variables:
                raise RuntimeError("Could not get longitudes variable ({}) from grid file {}".format(P.lons_variable, P.grid))
            lons = f(P.lons_variable).filled()
            print("Generating NEX Mesh please be patient")
            grid = e3sm_nex.generateNEXGrid(lats, lons, ec)
        else:  # MPAS grid type
            if P.lats_variable is None:
                if "grid_center_lat" in f.variables:
                    P.lats_variable = "grid_center_lat"
                else:
                    RuntimeError("could not figure out name of latitudes variable in grid file {}".format(P.grid))
            if P.lats_variable not in f.variables:
                raise RuntimeError("Could not get latitudes variable ({}) from grid file {}".format(P.lats_variable, P.grid))
            lats = f(P.lats_variable).filled()
            if P.lons_variable is None:
                if "grid_center_lon" in f.variables:
                    P.lons_variable = "grid_center_lon"
                else:
                    RuntimeError("could not figure out name of longtudes variable in grid file {}".format(P.grid))
            if P.lons_variable not in f.variables:
                raise RuntimeError("Could not get longitudes variable ({}) from grid file {}".format(P.lons_variable, P.grid))
            lons = f(P.lons_variable).filled()

            if P.latitude_corners is None:
                if "grid_corner_lat" in f.variables:
                    P.latitude_corners = "grid_corner_lat"
                else:
                    RuntimeError("could not figure out name of latitudes corners variable in grid file {}".format(P.grid))
            if P.latitude_corners not in f.variables:
                raise RuntimeError("Could not get latitudes corners variable ({}) from grid file {}".format(P.latitude_corners, P.grid))
            lats_corners = f(P.latitude_corners).filled()
            if P.longitude_corners is None:
                if "grid_corner_lon" in f.variables:
                    P.longitude_corners = "grid_corner_lon"
                else:
                    RuntimeError("could not figure out name of latitudes corners variable in grid file {}".format(P.grid))
            if P.longitude_corners not in f.variables:
                raise RuntimeError("Could not get longitudes corners variable ({}) from grid file {}".format(P.longitude_corners, P.grid))
            lons_corners = f(P.longitude_corners).filled()
            print("Generating MPAS Mesh please be patient")
            grid = e3sm_nex.generateMPASGrid(lats, lons, lats_corners, lons_corners)



    print("Mesh generated storing as {} in {}".format(P.mesh_variable, P.mesh))
    axes = data.getAxisList()
    with cdms2.open(P.mesh,"w") as f:
        mesh = numpy.zeros(grid.shape)
        mesh = e3sm_nex.applyGrid(mesh,grid)
        f.write(mesh,id=P.mesh_variable)

if P.output is None:  # We need to make up a name
    output_name = "{}_{}".format(data.id,grid.shape[0])
else:
    output_name = P.output
if P.output_type == "nc":
    data = e3sm_nex.applyGrid(data(),grid)
    with cdms2.open(output_name,"w"):
        cdms2.write(data)

width, height = P.geometry.split("x")
width = int(width)
height = int(height)
if P.output_type in ["png","postscript","pdf"]:
    bg = True
else:
    bg = False
if sys.platform == "darwin":
    W = width*2
    H = height *2
else:
    W = width
    H = height
x = vcs.init(geometry=(W,H), bg=bg)

projections  = {"default":vcs.createprojection()}
for typ in ["lambert","mollweide","robinson","polar","orthographic"]:
    p = vcs.createprojection()
    p.type = typ
    projections[typ] = p

gm = vcs.createmeshfill()
gm.datawc_x1 = float(P.lon1)
gm.datawc_x2 = float(P.lon2)
gm.datawc_y1 = float(P.lat1)
gm.datawc_y2 = float(P.lat2)
gm.mesh = P.show_mesh
gm.missing = P.missing_color
gm.projection = projections[P.projection]
gm.colormap = P.colormap
if P.levels is not None:
    gm.levels = P.levels
if P.colors is not None:
    gm.fillareacolors = P.colors
user_key =""
time_index = P.time_index
level_index = P.level_index
time = data.getTime()
level = data.getLevel()
typ = "p"  # default dump type is png
while user_key is not "q":
    kw = {}#"squeeze":1}
    if data.getTime() is not None:
        kw["time"]=slice(time_index,time_index+1)
    if data.getLevel() is not None:
        kw["level"] = slice(level_index,level_index+1)
    plot_data = data(**kw)
    if P.cleanup_data:
        plot_data = cdms2.MV2.masked_greater(numpy.abs(plot_data),1.e20)
    #while len(plot_data.shape)>1:
    #    plot_data = plot_data[0]
    e3sm_nex.applyGrid(plot_data,grid)
    x.clear()
    x.plot(plot_data,gm)
    if P.output_type in ["png","postscript","pdf"]:
        x.png(output_name)#,width=width,height=height,units="pixel")
        user_key = "q"
    else:
        user_key = input_char("Next instruction? (n)ext, (p)rev, (d)ump, next (t)ime, prev (T)ime, next (l)evel, prev (L)evel, (i)nteract, q(uit)")
        if user_key == "t" and time is not None:
            time_index +=1
            if time_index == len(time):
                time_index = 0
        elif user_key == "T" and time is not None:
            time_index -=1
            if time_index == 0:
                time_index = len(time)-1
        elif user_key == "l" and level is not None:
            level_index +=1
            if level_index == len(level):
                level_index = 0
        elif user_key == "L" and level is not None:
            level_index -=1
            if level_index == 0:
                level_index = len(level)-1
        elif user_key == "n":
            do_level = True
            if time is not None:
                time_index +=1
                if time_index == len(time):
                    time_index=0
                else:
                    do_level = False
            if do_level and level is not None:
                level_index +=1
                if level_index == len(level):
                    level_index = 0
        elif user_key == "p":
            do_level = True
            if time is not None:
                time_index -=1
                if time_index == -1:
                    time_index=len(time)-1
                else:
                    do_level = False
            if do_level and level is not None:
                level_index -=1
                if level_index == 0:
                    level_index = len(level)-1
        elif user_key == "d":
            utyp = input_char("Which format? (p)ng, (P)df, po(s)tscript, (n)etCDF")
            if utyp in ["p","P","s","n"]:
                typ = utyp
            dump_name = output_name
            if dump_name[-4:].lower() in [".png", ".pdf"]:
                dump_name = dump_name[:-4]
            if dump_name[-3:].lower() in [".ps", ".nc"]:
                dump_name = dump_name[:-3]
            if typ in ["p","P","s"]:
                if time is not None:
                    dump_name+="_{:0>3}".format(time_index)
                if level is not None:
                    dump_name+="_{:0>3}".format(level_index)
            else:
                dump_name+=".nc"
            if typ == "p":
                x.png(dump_name,width=width,height=height,units="pixel")
            elif typ == "P":
                x.pdf(dump_name,width=width,height=height,units="pixel")
            elif typ == "s":
                x.postscript(dump_name,width=width,height=height,units="pixel")
            elif typ == "n":
                data2 = e3sm_nex.applyGrid(data(),grid)
                with cdms2.open(dump_name,"w") as f:
                    f.write(data2,id=data.id)
        elif user_key == "i":
            print("Press Q to return to this prompt")
            x.interact()
            

