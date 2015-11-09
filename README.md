ughub - package managment for the UG4 simulation environment
Copyright 2015 G-CSC, Goethe University Frankfurt

'ughub' allows to easily install all the different plugins and applications that
are built on top of 'UG4'. It automatically handles inter-package dependencies
and helps in managing the different involved git repositories.

'ughub' requires Python 2.x (2.7 is recommended). If Python is not available on
your system, please install it through your package manager or download the
setup program, e.g., from https://www.python.org/downloads/release/python-2710/

Once Python is installed, please clone this repository, e.g. to $HOME/bin/ughub
and either add this path to your PATH environment variable or create a link/shortcut
to the bash-script $HOME/bin/ughub/ughub ($HOME/bin/ughub/ughub.bat on windows).

To validate your ughub installation please call 'ughub --version' from your home
directory.

In order to install 'UG4', create a directory (e.g. $HOME/projects/UG4) and change
directory to this path ('cd $HOME/projects/UG4').
Call 'ughub init' to initialize this directory for use with ughub.
'ughub listpackages' will now provide a list of all available packages,
'ughub install ugcore' will install the core components of UG4.
