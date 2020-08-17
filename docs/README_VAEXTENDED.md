# Developer Guide: Vaextended

Adapted version of Vaex to allow local control over the backend (Default Path: `~/work/moneta/moneta/vaextended`);

## <a name="modify"></a> Modifying Vaex's Existing Backend

### bqplot.py

Add or modify backends in the following way (the code below is from `view.py`):

```
import vaex
import vaex.jupyter.plot
vaex.jupyter.plot.backends['bqplot_v2'] = ("vaextended.bqplot", "BqplotBackend")
```

This will create a new Vaex backend called `bqplot_v2` that uses the the `bqplot.py` file in the `vaextended` directory, as referenced by `vaextended.bqplot`, instead of the original `bqplot.py` from Vaex in the `/opt/conda/lib/python3.7/site-packages/vaex/jupyter` directory.

### plot.py

In order to expand on various aspects the plot itself, such as saving metadata (i.e. x/y labels, cache size) and increasing plot point size, we need to change the `PlotBase` class in `plot.py`. In order to use this modified `PlotBase` instead of Vaex's original `PlotBase`, we need to include the following code in `vaextended/__init__.py` .

```
import vaex.jupyter.plot
from vaextended.plot import PlotBase
vaex.jupyter.plot.type_map['custom_plot1'] = PlotBase
```

This allows us to save our custom `PlotBase` from our `plot.py`, as referenced by `vextended.plot` as a key-value pair into the Vaex plot's `type_map` upon initialization. If we pass in the `type=TYPE` argument into `plot_widget()`, Vaex will search in `type_maps` for the `TYPE` key and use the corresponding value as it's `PlotBase`. So, if we were to pass in `type='custom_plot1'`, Vaex would use our custom `PlotBase` instead of the original instance.


### widgets.py

The main feature of interest in the `PlotTemplate` class in `widgets.py` is the plot title. For Vaextended's `PlotTemplate`, we replaced the plot title with `Moneta` instead of `Vaex` to better reflect the tool. To use this modified `PlotTemplate`, we need to add the following import to `plot.py` to override the original.

```
from vaextended.widgets import PlotTemplate
```

### Vaextended Directory Location

If the Moneta Jupyter Notebook is not in the directory that contains `vaextended`, the path may need to be extended using the following function:

```
sys.path.append('PATH_TO_VAEXTENDED')
```

Note that `PATH_TO_VAEXTENDED` does **NOT** include the `vaextended` directory itself. For the most part, this should not be an issue since the GitHub repository  tree places `vaextended` in the same directory as `Moneta.ipynb`.

## Using Vaextended

To use the modified backends and plots of Vaextended, simply specify the backend and plot type you want to use with the `backend=BACKEND` and `type=PLOT_TYPE` keyword arguments in `plot_widget`. An example using the names set in [**Modifying Vaex's Existing Backend**](#modify) can be found below:

```
import vaex
df = vaex.example()
df.plot_widget(df.x, df.y, backend='bqplot_v2', type='custom_plot1')
```

### Accessing the Backend

`plot_widget()` will return a plot object, which has a `backend` element of type `BqplotBackend`. To access all the functions and variables of the `BqplotBackend`, all you need to do is save the result of `plot_widget` to a variable and access the `backend` property.
```
plot = df.plot_widget(...)
backend = plot.backend
```

## Other Notes

### Vaex Inverted Navigation

The default installation of Vaex has a bug where the plot created by `plot_widget()` has it's vertical navigation inverted, such that moving the plot upwards will cause the plot points to reload as if you moved the plot downward.

# TODO: Locate line that fixes this error

### `@extend_class` Decorator

**Note:** This is a legacy feature is not being used in the current iteration of Vaextended. To add or modify additional functions, simply make those changes in the corresponding file in the `vaextended` directory.

`vaextended/utils.py` has a decorator to make it easy to modify or add functions to existing classes in Vaex. If additional methods need to be modified or added to the `BqplotBackend` class, use the following format:

```python
@extend_class(BqplotBackend)
def method_name(method_args):
    # body of method
```