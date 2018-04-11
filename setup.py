from distutils.core import setup
Version="0.0.1"

setup (name = "e3smnex",
       author="AIMS Team",
       version=Version,
       description = "Utilities for E3SM NEx grids",
       url = "http://github.com/cdat/e3sm_nex",
       packages = ['e3smnex'],
       package_dir = {'e3smnex': 'lib'},
       #data_files = [ ("share/e3smnex",())],
       scripts= ["scripts/e3sm_view"],
      )
    
