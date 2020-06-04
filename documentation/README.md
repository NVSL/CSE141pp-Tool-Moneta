# FAQs

### Why are there two setup directories and 3 vaex_extended directories?

There are 2 setup directories that are of importance: the root directory `/setup/` and the relative directory `../Setup/`. Likewise, there are
3 vaex\_extended directories of importance: `/setup/vaex-extended`, `../Setup/vaex_extended_setup`, and `../vaex_extended`. Note that the default current directory will be the `~/work/memorytrace` directory.  
  
**FUTURE TODO:** Pick a better naming scheme for these directories so we don't need this part of the README anymore.

#### ../Setup vs  /setup/

The `../Setup` directory will contain all the files necessary when building the Docker image. Most of these files will be copied over to the `/setup/` direc
tory when building the image.

#### /setup/vaex\_extended vs ../vaex\_extended vs ../Setup/vaex\_extended
These directories contain all the files to create our modified bqplot backend. We will do our backend development in the  `../vaex_extended` directory. Whenever features are finalized and/or fully developed, we will add these changes to `../Setup/vaex_extended_setup`. Once the files are in the `../Setup` directory, the Dockerfile will now copy `../Setup/vaex_extended_setup` to `/setup/vaex_extended`, and the Notebook refer to `/setup/vaex_extended` when it plots using bqplot.  
  
**Note:**  You will see a line at the top of `main.py` that looks like one of the following:

```
sys.path.append('../')
sys.path.append('/setup/')
```

These two lines tell the Notebook where to look to find the files for BqplotBackend. For development (i.e. when working in the dev branch), since the changes are made in the `../vaex_extended` directory, we will need to direct the Notebook's path to `../` so it can find the current changes in the `vaex_extended` folder. However, for student use (i.e. when pushing to the master branch), we will need to change the path to `/setup/`, since the `vaex_extended` directory with the most recent finalized changes will be found there.

### Where is PIN?

##### /setup/pintool

This directory contains all the Pin source files and the main executable to run the Pin program itself.

# TODO
* Fix refresh stats to respond quickly on pan and zoom or with a button
* Custom plot widget name
* Fix legend to include checkboxes and all the data structures with their zoom to selection buttons
* Disable sidebar in plot
* Adjust y-scale to display all the digits of y addresses instead of 1.4e13
* Zoom on click using maximum and minimum y address at that x index
