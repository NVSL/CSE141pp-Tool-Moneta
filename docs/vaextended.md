# Developer Guide: Vaextended

Adapted version of Vaex to allow local control over the backend (Default Path: `moneta/moneta/vaextended`);

**IMPORTANT:** Moneta currently uses the following versions of Vaex, as `plot_widget()` is depricated in newer versions. These should be already specified in `setup/requirements.txt`:
```
vaex-arrow: 0.4.2
vaex-astro 0.6.1
vaex-core: 1.5.0
vaex-hdf5: 0.5.6
vaex-jupyter: 0.4.1
vaex-server: 0.2.1
vaex-ui:  0.3.0
vaex-viz: 0.3.8
```

## <a name="modify"></a> Modifying Vaex's Existing Backend

Vaex's original files are located in the `/opt/conda/lib/python3.7/site-packages/vaex` directory. We will refer to this directory as `VAEX_ROOT` for brevity.

### bqplot.py

Add or modify backends in the following way (the code below is from `moneta/moneta/view.py`):

```python
import vaex
import vaex.jupyter.plot
vaex.jupyter.plot.backends['moneta_backend'] = ("vaextended.bqplot", "BqplotBackend")
```

This will create a new backend called `moneta_backend` based off the `BqplotBackend` class in `moneta/moneta/vaextended/bqplot.py` instead of the original `BqplotBackend` in  `VAEX_ROOT/jupyter/bqplot.py`. To use the modified `BqplotBackend`, pass `backend='moneta_backend'` into `plot_widget()`.

### plot.py

In order to expand on aspects the plot itself, such as saving metadata (i.e. x/y labels, cache size) and increasing plot point size, we need to change the `PlotBase` class in `plot.py`. To use our modified `PlotBase` instead of Vaex's original `PlotBase` in `VAEX_ROOT/jupyter/plot.py`, we need to include the following code in `moneta/moneta/vaextended/__init__.py` .

```python
import vaex.jupyter.plot
from vaextended.plot import PlotBase
vaex.jupyter.plot.type_map['vaextended'] = PlotBase
```
To use the modified `PlotBase`, pass `type='vaextended'` into `plot_widget()`. 

**Note:** The `PlotBase` object is what `plot_widget()` returns.


### widgets.py

The `PlotTemplate` class in `widgets.py` contains a base widget for the plot. This includes the top nav bar (title, pan/zoom, etc.), legend, and the plot itself. To use this modified `PlotTemplate`, we need to add the following import to `plot.py` to override the original `PlotTemplate` class.

```python
from vaextended.widgets import PlotTemplate
```

### Vaextended Directory Location

If `Moneta.ipynb` is not in the directory that contains `vaextended`, the path may need to be extended using the following function:

```python
sys.path.append('PATH_TO_VAEXTENDED')
```

**Note:** `PATH_TO_VAEXTENDED` does **NOT** include the `vaextended` directory itself. For the most part, this should not be an issue since the GitHub repository tree places `vaextended` in the same directory as `Moneta.ipynb`.


## Using Vaextended

Using `plot_widget()` with the Vaextended backend requires the following keyword arguments:
 - **backend:** Name referencing the backend to use
 - **type:** Name referencing the `PlotBase` class to use
 - **legend:** A Legend object from `moneta/moneta/legend.py`
 - **x_col:** The x-column name of the dataframe
 - **y_col:** The y-column name of the dataframe
 - **cache_size:** The cache size in bytes
 - **update_stats:** A callback function that updates "Current View Stats" in the Legend object
 - **limit:** The x and y limits in 2D array format (e.g. `[[x_min, x_max], [y_min, y_max]]`) 
    - Required because Vaex incorrectly calculates the y-limits, likely due to the memory addresses being so large in value. This causes the plot to crash from divide-by-zero, so we have to manually pass in the correct limits.


 The following keyword arguments are not required, but should be included as they improve navigation and visuals:
 - **colormap:** Colormap to use. The primary colormap Vaextended uses can be found in `moneta/moneta/settings.py` as `CUSTOM_CMAP`
 - **selection:** Passing in `[True]` allows turning on/off access types or tags via the Legend checkboxes
 - **what:** Determines how Vaex's binned data points should be mapped to the colormap and displayed. Vaextended uses `max(Access)`
 - **default_title:** Title of the plot, typically set to be the trace name (Default: "Moneta")
 - **x_label:** The plot's x-axis label (Default: "Access Number")
 - **y_label:** The plot's y-axis label (Default: "Address")

An example of using `plot_widget()` with Vaextended can be found below. For backend and type, we will use the names set in [**Modifying Vaex's Existing Backend**](#modify):

```python
# Assume this file has three columns: "index", "Address", and "Access"
df = vaex.open('some_trace.hdf5') 
x_min = df.index.min()
x_max = df.index.max()
y_min = df.Address.min()
y_max = df.Address.max()

plot = df.plot_widget(
            df['index'],
            df['Address'],
            what='max(Access)',
            colormap=CUSTOM_CMAP, 
            selection=[True], 
            limits=[[x_min, x_max], [y_min, y_max]],
            backend='moneta_backend', 
            type='vaextended', 
            legend=Legend(),
            default_title='Some Trace', 
            x_col='index', 
            y_col='Address', 
            x_label='Access Number', 
            y_label='Memory Address', 
            cache_size=16384,
            update_stats=function_that_updates_legend_current_view_stats
            )
```



## Other Notes

### Vaex Inverted Navigation

The default installation of Vaex has a bug where `plot_widget()` has it's vertical navigation inverted. We have fixed this bug in Vaextended's `plot.py` in by rotating the plot on line 304:
```diff
+ I = np.rot90(color_grid).copy()
```


### `@extend_class` Decorator

**Note:** This is a legacy feature not being used in the current iteration of Vaextended. To add or modify additional functions, simply make those changes in the corresponding file in the `vaextended` directory.

The decorator is located in `vaextended/utils.py`. To add, override, and/or modify features in the `BqplotBackend` class, use the following format:

```python
@extend_class(BqplotBackend)
def method_name(method_args):
    # body of method
```
