import sys
from setuptools import setup

from ughub import g_ughubVersionString

metadata = dict(name="ughub",
      version=g_ughubVersionString,
      description="package managment for the UG4 simulation environment",
      long_description="ughub' allows to easily install all the different "
                       "plugins and applications that are built on top of UG4."
                       " It automatically handles inter-package dependencies "
                       "and helps in managing the different involved git repositories.",
      package_dir={'ughub': '.'},
      packages=['ughub'],
      entry_points={"console_scripts": ["ughub = ughub.ughub:main"] },
)


sys.exit(setup(**metadata))
