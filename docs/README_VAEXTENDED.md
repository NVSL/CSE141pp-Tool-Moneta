# Developer Guide: Vaextended

Adapted version of Vaex to allow local control over the backend (Default Path: `~/work/moneta/moneta/vaextended`);

## <a name="modify"></a> Modifying Vaex's Existing Backend

### bqplot.py

Add or modify backends in the following way (the code below is from `view.py`):

```
import vaex
import vaex.jupyter.plot
vaex.jupyter.plot.backends['moneta_backend'] = ("vaextended.bqplot", "BqplotBackend")
```

This will create a new Vaex backend called `moneta_backend` that uses the the `bqplot.py` file in the `vaextended` directory, as referenced by `vaextended.bqplot`, instead of the original `bqplot.py` from Vaex in the `/opt/conda/lib/python3.7/site-packages/vaex/jupyter` directory.

### plot.py

In order to expand on various aspects the plot itself, such as saving metadata (i.e. x/y labels, cache size) and increasing plot point size, we need to change the `PlotBase` class in `plot.py`. In order to use this modified `PlotBase` instead of Vaex's original `PlotBase`, we need to include the following code in `vaextended/__init__.py` .

```
import vaex.jupyter.plot
from vaextended.plot import PlotBase
vaex.jupyter.plot.type_map['vaextended'] = PlotBase
```

This allows us to save our custom `PlotBase` from our `plot.py`, as referenced by `vextended.plot` as a key-value pair into the Vaex plot's `type_map` upon initialization. If we pass in the `type=TYPE` argument into `plot_widget()`, Vaex will search in `type_maps` for the `TYPE` key and use the corresponding value as it's `PlotBase`. So, if we were to pass in `type='vaextended'`, Vaex would use our custom `PlotBase` instead of the original instance.


### widgets.py

The `PlotTemplate` class in `widgets.py` contains most widget features of the plot, particularly the top nav bar with the title and various zoom widgets, as well as interactive plot itself within the `v-main` area. Note that these widgets mainly use [ipyvuetify](https://ipyvuetify.readthedocs.io/en/latest/). For Vaextended's `PlotTemplate`, we replaced the plot title with the trace name instead of `Vaex` to better reflect the plot and made it editable. We also removed the sidebar and the expandable output section from the original Vaex, as Moneta does not have much use for those two widgets. To use this modified `PlotTemplate`, we need to add the following import to `plot.py` to override the original.

```
from vaextended.widgets import PlotTemplate
```

### Vaextended Directory Location

If the Moneta Jupyter Notebook is not in the directory that contains `vaextended`, the path may need to be extended using the following function:

```
sys.path.append('PATH_TO_VAEXTENDED')
```

Note that `PATH_TO_VAEXTENDED` does **NOT** include the `vaextended` directory itself. For the most part, this should not be an issue since the GitHub repository tree places `vaextended` in the same directory as `Moneta.ipynb`.

## Using Vaextended

To use the modified backends and plots of Vaextended, specify the backend and plot type you want to use with the `backend=BACKEND` and `type=PLOT_TYPE` keyword arguments in `plot_widget()`. If the values set in [**Modifying Vaex's Existing Backend**](#modify) remain unchanged, `backend='moneta_backend'` and `type='vaextended'` should be passed in. Otherwise, these two values should be replaced accordingly.


Using `plot_widget()` with the Vaextended backend also requires the following keyword arguments in addition to `backend` and `type`:
 - **legend:** A Legend object from `moneta/legend.py`
 - **x_col:** The x-column name of the dataframe
 - **y_col:** The y-column name of the dataframe
 - **x_label:** The plot's x-axis label
 - **y_label:** The plot's y-axis label
 - **cache_size:** The cache size in bytes
 - **update_stats:** A callback function that updates "Current View Stats" in the Legend object
  - **limit:** The x and y limits in 2D array format (e.g. `[[x_min, x_max], [y_min, y_max]]`). Required because Vaex incorrectly calculates the y-limits, likely due to the memory addresses being so large in value. This causes the plot to crash from divide-by-zero, so we have to manually pass in the correct limits.


 The following keyword arguments are technically not required, but should be included as they improve navigation and visuals:
  - **colormap:** Colormap to use. The primary colormap Vaextended uses can be found in `moneta/settings.py` as `CUSTOM_CMAP`
  - **selection:** Passing in `[True]` allows turning on/off access types or tags via the Legend checkboxes
  - **what:** Determines which value out of Vaex's binned data points should be mapped to the colormap and displayed. Vaextended uses `max(Access)`
  - **default_title:** Title of the plot, typically set to be the trace name

An example of using `plot_widget()` with Vaextended can be found below:

```
import vaex
from moneta.legend import Legend
from moneta.settings import CUSTOM_CMAP

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
            update_stats=lambda *ignore: update_legend_view_stats(legend.plot_stats, plot, False)
            )
```




### Accessing the Backend

`plot_widget()` will return a plot object, which has a `backend` element of type `BqplotBackend`. To access all the functions and variables of the `BqplotBackend`, all you need to do is save the result of `plot_widget` to a variable and access the `backend` property.
```
plot = df.plot_widget(...)
backend = plot.backend
```

## Other Notes

### Vaex Inverted Navigation

The default installation of Vaex has a bug where the plot created by `plot_widget()` has it's vertical navigation inverted, such that moving the plot upwards will cause the plot points to reload as if you moved the plot downward. We have fixed this bug in Vaextended's `plot.py` in by rotating the plot grid by 90 degrees on line 304:
```diff
+ I = np.rot90(color_grid).copy()
```


### `@extend\_class` Decorator

**Note:** This is a legacy feature not being used in the current iteration of Vaextended. To add or modify additional functions, simply make those changes in the corresponding file in the `vaextended` directory.

`vaextended/utils.py` has a decorator to make it easy to modify or add functions to existing classes in Vaex. If additional methods need to be modified or added to the `BqplotBackend` class, use the following format:

```python
@extend_class(BqplotBackend)
def method_name(method_args):
    # body of method
```
