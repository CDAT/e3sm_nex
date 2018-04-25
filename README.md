# A set of tools to view E3SM data on native grids

Currently supports neX and MPAS native grids.

NE120 and NE30 are automatically detected, MPAS need to pass grid file as well.

Other NEX need to associate the grid file (or a previously generated mesh file). Mesh generation for NEX is quite time consuming, but only needs to be done once.

## Installing

Support for both OSX and Linux and both Python 2.7 or Python 3.6


to add to an existing environment

```
conda install -c conda-forge -c cdat e3sm_nex
```

To create a self-contained env:

```
conda create -n e3sm_view -c conda-forge -c cdat
```

## e3sm_view tool

### Quick example

#### NE30

`e3sm_view -i ne30_TS.nc -v TS`

#### NEx (or to force grid generation)

`e3sm_view -i ne120_TS.nc --grid=ne30np4_latlon.091226.nc`

#### MPAS
 
`e3sm_view -i ocean.oEC60to30v3.scrip.161222.nc --grid=ocean.oEC60to30v3.scrip.161222.nc -v grid_area`

### Usage

As of `0.0.2` the following options are available:

```
e3sm_view --help
```

```
usage: e3sm_view [-h] [-p PARAMETERS]
                 [-d OTHER_PARAMETERS [OTHER_PARAMETERS ...]] [-n NUM_WORKERS]
                 [--scheduler_addr SCHEDULER_ADDR]
                 [--granulate GRANULATE [GRANULATE ...]] [-M MESH]
                 [-m MESH_VARIABLE] [-v VARIABLE] [-i INPUT_FILE] [-g GRID]
                 [--grid_type {nex,mpas}] [-e ELEMENT_CORNERS]
                 [--longitude_corners LONGITUDE_CORNERS]
                 [--latitude_corners LATITUDE_CORNERS] [-l LATS_VARIABLE]
                 [-L LONS_VARIABLE] [--lon1 LON1] [--lon2 LON2] [--lat1 LAT1]
                 [--lat2 LAT2] [--time_index TIME_INDEX]
                 [--level_index LEVEL_INDEX] [--show_mesh] [--missing_color]
                 [--levels LEVELS] [--colors COLORS]
                 [--output_type {screen,s,png,pdf,postscript,nc}]
                 [--output OUTPUT] [--geometry GEOMETRY] [-c COLORMAP] [-C]
                 [-P {default,lambert,robinson,mollweide,polar,orthographic}]

optional arguments:
  -h, --help            show this help message and exit
  -p PARAMETERS, --parameters PARAMETERS
                        Path to the user-defined parameter file. (default:
                        None)
  -d OTHER_PARAMETERS [OTHER_PARAMETERS ...], --diags OTHER_PARAMETERS [OTHER_PARAMETERS ...]
                        Path to the other user-defined parameter file.
                        (default: [])
  -n NUM_WORKERS, --num_workers NUM_WORKERS
                        Number of workers, used when running with
                        multiprocessing or in distributed mode. (default:
                        None)
  --scheduler_addr SCHEDULER_ADDR
                        Address of the scheduler in the form of
                        IP_ADDRESS:PORT. Used when running in distributed
                        mode. (default: None)
  --granulate GRANULATE [GRANULATE ...]
                        A list of variables to granulate. (default: None)
  -M MESH, --mesh MESH  mesh file either for input or for file where mesh info
                        will be stored once generated. We try to detect ne120
                        and ne30, for which mesh files are provided (default:
                        None)
  -m MESH_VARIABLE, --mesh_variable MESH_VARIABLE
                        variable containing mesh (in mesh file) (default:
                        mesh)
  -v VARIABLE, --variable VARIABLE
                        variable to view (default: None)
  -i INPUT_FILE, --input_file INPUT_FILE
                        file containing variable to view (default: None)
  -g GRID, --grid GRID  e3sm grid file (default: None)
  --grid_type {nex,mpas}
                        Grid file type nex (nex-like i.e element_corners) or
                        mpas (mpas like grid_corners) (default: None)
  -e ELEMENT_CORNERS, --element_corners ELEMENT_CORNERS
                        variable containing element_corners in grid file
                        (default: None)
  --longitude_corners LONGITUDE_CORNERS
                        variable containing longitude corners in grid file
                        (default: None)
  --latitude_corners LATITUDE_CORNERS
                        variable containing latitude corners in grid file
                        (default: None)
  -l LATS_VARIABLE, --lats_variable LATS_VARIABLE
                        variable containing latitudes in grid file (default:
                        None)
  -L LONS_VARIABLE, --lons_variable LONS_VARIABLE
                        variable containing longitudes in grid file (default:
                        None)
  --lon1 LON1           first longitude (default: 0.0)
  --lon2 LON2           last longitude (default: 360.0)
  --lat1 LAT1           first latitude (default: -90.0)
  --lat2 LAT2           last latitude (default: 90.0)
  --time_index TIME_INDEX
                        time index to plot (default: 0)
  --level_index LEVEL_INDEX
                        leve index to plot (default: 0)
  --show_mesh           draw the mesh on plot (default: False)
  --missing_color       color of missing values on plot (default: lightgrey)
  --levels LEVELS       levels to use (default: None)
  --colors COLORS       color indices to use (default: None)
  --output_type {screen,s,png,pdf,postscript,nc}
                        output type (default: screen)
  --output OUTPUT       output file name (default: None)
  --geometry GEOMETRY   geometry for output (default: 800x600)
  -c COLORMAP, --colormap COLORMAP
                        colormap to use (default: viridis)
  -C, --cleanup_data    apply quick cleanup on data where abs value is > 1.e20
                        (default: False)
  -P {default,lambert,robinson,mollweide,polar,orthographic}, --projection {default,lambert,robinson,mollweide,polar,orthographic}
                        projection type (default: default)
```
