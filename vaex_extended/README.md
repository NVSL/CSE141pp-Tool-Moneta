# Extended Vaex

Adapted version of vaex to allow local control over the backend

## Layout
```
vaex_extended/
    __init__.py
    jupyter/
        __init__.py
        bqplot.py
    utils/
        __init__.py
        decorator.py
```
Additional backends to Vaex are to be placed in `vaex_extended/jupyter`
and should follow the format of bqplot.py.  Additionally, they should be
added to `vaex_extended/__init__.py` to be added to the database of backends.

## Usage in Jupyter Notebook

### Modifying Vaex Yourself
Add or modify backends in the following way:
```
import vaex
import vaex.jupyter.plot
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot', 'BqplotBackend')
```
Then use the backend in `plot_widget`.  Name the backend `bqplot` instead of `bqplot_v2`
to replace the existing default bqplot backend rather than create a new one.
```
df = vaex.example()
df.plot_widget(df.x,df.y,backend='bqplot_v2')
```
### Using the Built-In Modified Version of Vaex
Import `vaex_extended` and use exactly like `vaex`.
Specify the backend you want to use.
In `vaex_extended/__init__.py`, name the backend `bqplot` instead of `bqplot_v2`
to replace the existing default bqplot backend rather than create a new one.
```
import vaex_extended
df = vaex_extended.example()
df.plot_widget(df.x,df.y,backend='bqplot_v2')
```
## Use in Other Directories
If the Jupyter notebook is not in the directory that contains `vaex_extended`, the path may
need to be extended.  Eventually, `vaex_extended` should be moved to the correct direcory
so that this is not a issue.

```
import sys, os
sys.path.append('../') # here vaex_extended is in the parent directory
import vaex
import vaex.jupyter.plot
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot', 'BqplotBackend')
```
Alternatively, the package can be installed so that it is available anywhere.
In the directory outside `vaex_extended`, which should contain `setup.py`, run:
```
pip install -e .
```
The flag `-e` will allow edits to the source files to appear without needing a reinstall.
## How to Modify bqplot.py

decorator.py has a decorator to make it easy to modify or add functions to existing
classes in Vaex.

bqplot.py already modifies some methods from `vaex/jupyter/bqplot.py`.  If additional
methods need to be modified or added to the BqplotBackend class, use the format:
```python
@extend_class(BqplotBackend)
def method_name(method_args):
    # body of method
```
## Example
For bqplot backends, Vaex currently flips the image.  The code below fixes the issue.
The decorator `@extend_class` redefines `BqplotBackend.update_image` to `update_image`.

```python
@extend_class(BqplotBackend)
def update_image(self, rgb_image):
    # corrects error where the image is flipped vertically
    rgb_image = np.flipud(rgb_image) 
    with self.output:
        rgb_image = (rgb_image * 255.).astype(np.uint8)
        pil_image = vaex.image.rgba_2_pil(rgb_image)
        data = vaex.image.pil_2_data(pil_image)
        self.core_image.value = data
        # force update
        self.image.image = self.core_image_fix
        self.image.image = self.core_image
        self.image.x = (self.scale_x.min, self.scale_x.max)
        self.image.y = (self.scale_y.min, self.scale_y.max)
```

## How to Make Additional Backends

Import the included decorator as well as the backend to be used as a template.

```python
from vaex.jupyter.bqplot import *
from vaex_extended.utils.decorator import *

```
Additionally, for bqplot backends, Vaex currently flips the image.  Fix this by added `np.flipud` to
`BqplotBackend.update_image` as detailed in the example above.
