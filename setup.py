from distutils.core import setup
import os, requests
if not os.path.exists("share"):
    os.makedirs("share")
for filename in ["e3sm_mesh_ne120.nc","e3sm_mesh_ne30.nc"]:
    filepth = os.path.join("share",filename)
    if not os.path.exists(filepth):
        r = requests.get("https://cdat.llnl.gov/cdat/sample_data/{}".format(filename),stream=True)
        with open(filepth,"wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter local_filename keep-alive new chunks
                    f.write(chunk)


Version="0.0.1"

setup (name = "e3smnex",
       author="AIMS Team",
       version=Version,
       description = "Utilities for E3SM NEx grids",
       url = "http://github.com/cdat/e3sm_nex",
       packages = ['e3smnex'],
       package_dir = {'e3smnex': 'lib'},
       data_files = [ ("share/e3smnex",("share/e3sm_mesh_ne30.nc","share/e3sm_mesh_ne120.nc"))],
       scripts= ["scripts/e3sm_view"],
      )
    
