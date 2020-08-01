from __future__ import absolute_import
import traitlets
import ipywidgets as widgets
import ipyvuetify as v
import six
import vaex.utils
from vaex.delayed import delayed, delayed_list
import numpy as np
import importlib
from IPython.display import display
import copy
from .utils import debounced
from vaex.utils import _ensure_list, _expand, _parse_f, _parse_n, _parse_reduction, _expand_shape
from .widgets import PlotTemplate

type_map = {}


def register_type(name):
    def reg(cls):
        assert cls not in type_map
        type_map[name] = cls
        return cls
    return reg


def get_type(name):
    if name not in type_map:
        raise ValueError("% not found, options are %r" % (name, type_map.keys()))
    return type_map[name]


backends = {}
backends['ipyleaflet'] = ('vaex.jupyter.ipyleaflet', 'IpyleafletBackend')
backends['bqplot'] = ('vaex.jupyter.bqplot', 'BqplotBackend')
backends['ipyvolume'] = ('vaex.jupyter.ipyvolume', 'IpyvolumeBackend')
backends['matplotlib'] = ('vaex.jupyter.ipympl', 'MatplotlibBackend')
backends['ipympl'] = backends['mpl'] = backends['matplotlib']


def create_backend(name):
    if callable(name):
        return name()
    if name not in backends:
        raise NameError("Unknown backend: %s, known ones are: %r" % (name, backends.keys()))
    module_name, class_name = backends[name]
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name, None)
    if cls is None:
        raise NameError("Could not find classname %s in module %s for backend %s" % (class_name, module_name, name))
    return cls()


class BackendBase(widgets.Widget):
    dim = 2
    limits = traitlets.List(traitlets.Tuple(traitlets.CFloat(), traitlets.CFloat()))

    @staticmethod
    def wants_colors():
        return True

    def update_vectors(self, vcount, vgrids, vcount_limits):
        pass

def _translate_selection(selection):
    if selection in [None, False]:
        return None
    if selection == True:
        return 'default'
    else:
        return selection



class PlotBase(widgets.Widget):

    x = traitlets.Unicode(allow_none=False).tag(sync=True)
    y = traitlets.Unicode(allow_none=True).tag(sync=True)
    z = traitlets.Unicode(allow_none=True).tag(sync=True)
    w = traitlets.Unicode(allow_none=True).tag(sync=True)
    vx = traitlets.Unicode(allow_none=True).tag(sync=True)
    vy = traitlets.Unicode(allow_none=True).tag(sync=True)
    vz = traitlets.Unicode(allow_none=True).tag(sync=True)
    smooth_pre = traitlets.CFloat(None, allow_none=True).tag(sync=True)
    smooth_post = traitlets.CFloat(None, allow_none=True).tag(sync=True)
    what = traitlets.Unicode(allow_none=False).tag(sync=True)
    vcount_limits = traitlets.List([None, None], allow_none=True).tag(sync=True)
    f = traitlets.Unicode(allow_none=True)
    grid_limits = traitlets.List(allow_none=True)
    grid_limits_min = traitlets.CFloat(None, allow_none=True)
    grid_limits_max = traitlets.CFloat(None, allow_none=True)

    def __init__(self, backend, dataset, x, y=None, z=None, w=None, grid=None, limits=None, shape=128, what="count(*)", f=None,
                 vshape=16,
                 selection=None, grid_limits=None, normalize=None, colormap="afmhot",
                 figure_key=None, fig=None, what_kwargs={}, grid_before=None, vcount_limits=None, 
                 show_drawer=False,
                 controls_selection=True, **kwargs):
        super(PlotBase, self).__init__(x=x, y=y, z=z, w=w, what=what, vcount_limits=vcount_limits, grid_limits=grid_limits, f=f, **kwargs)
        self.backend = backend
        self.vgrids = [None, None, None]
        self.vcount = None
        self.dataset = dataset
        self.limits = self.get_limits(limits)
        self.shape = shape
        self.shape = 512
        self.selection = selection
        self.grid_limits_visible = None
        self.normalize = normalize
        self.colormap = colormap
        self.what_kwargs = what_kwargs
        self.grid_before = grid_before
        self.figure_key = figure_key
        self.fig = fig
        self.vshape = vshape
        self.scales = [[self.limits[0][0],self.limits[0][1]],[self.limits[1][0],self.limits[1][1]]]

        self._new_progressbar()

        self.output = widgets.Output()
        def output_changed(*ignore):
            self.widget.new_output = True
        self.output.observe(output_changed, 'outputs')
        # with self.output:
        if 1:
            self._cleanups = []

            self.progress = widgets.FloatProgress(value=0.0, min=0.0, max=1.0, step=0.01)
            self.progress.layout.width = "95%"
            self.progress.layout.max_width = '500px'
            self.progress.description = "progress"

            self.extra_widget = v.Row(pa_1=True, children=[])
            self.backend.create_widget(self.output, self, self.dataset, self.limits)

            self.widget = PlotTemplate(components={
                        'main-widget': widgets.VBox([self.backend.widget, self.progress, self.output]),
                        'output-widget': self.output,
                        'extra-widget': self.extra_widget
                    },
                    model=show_drawer
            )
            if grid is None:
                self.update_grid()
            else:
                self.grid = grid

        def _on_limits_change(*args):
            self._progressbar.cancel()
            self.update_grid()
        self.backend.observe(_on_limits_change, "limits")
        for attrname in "x y z vx vy vz".split():
            def _on_change(change, attrname=attrname):
                limits_index = {'x': 0, 'y': 1, 'z': 2}.get(attrname)
                if limits_index is not None:
                    self.backend.limits[limits_index] = None
                self.update_grid()
            self.observe(_on_change, attrname)
        # self.update_image() # sometimes bqplot doesn't update the image correcly

    @debounced(0.3, method=True)
    def hide_progress(self):
        self.progress.layout.visibility = 'hidden'

    def get_limits(self, limits):
        return self.dataset.limits(self.get_binby(), limits)

    def active_selections(self):
        selections = _ensure_list(self.selection)

        def translate(selection):
            if selection is False:
                selection = None
            if selection is True:
                selection = "default"
            return selection
        selections = map(translate, selections)
        selections = list([s for s in selections if self.dataset.has_selection(s) or s in [False, None]])
        if not selections:
            selections = [False]
        return selections

    def show(self):
        display(self.widget)

    def add_extra_widget(self, widget):
        self.extra_widget.children += [widget]
        # TODO: find out why we need to do this, is this a bug?
        self.extra_widget.send_state('children')

    def _progress(self, v):
        self.progress.value = v

    def _new_progressbar(self):
        def update(v):
            with self.output:
                self.progress.layout.visibility = 'visible'
                import IPython
                ipython = IPython.get_ipython()
                if ipython is not None:  # for testing
                    ipython.kernel.do_one_iteration()
                self.progress.value = v
                if v == 1:
                    self.hide_progress()
                return not self._progressbar.cancelled
        self._progressbar = vaex.utils.progressbars(False, next=update, name="bqplot")

    def get_shape(self):
        return _expand_shape(self.shape, len(self.get_binby()))

    def get_vshape(self):
        return _expand_shape(self.vshape, len(self.get_binby()))

    @debounced(.5, method=True)
    def update_grid(self):
        with self.output:
            limits = self.backend.limits[:self.backend.dim]
            xyz = [self.x, self.y, self.z]
            for i, limit in enumerate(limits):
                if limits[i] is None:
                    limits[i] = self.dataset.limits(xyz[i], delay=True)

            @delayed
            def limits_done(limits):
                with self.output:
                    self.limits[:self.backend.dim] = np.array(limits).tolist()
                    limits_backend = copy.deepcopy(self.backend.limits)
                    limits_backend[:self.backend.dim] = self.limits[:self.backend.dim]
                    self.backend.limits = limits_backend
                    self._update_grid()
            limits_done(delayed_list(limits))
            self._execute()

    def _update_grid(self):
        with self.output:
            self._progressbar.cancel()
            self._new_progressbar()
            current_pb = self._progressbar
            delay = True
            promises = []
            pb = self._progressbar.add("grid")
            result = self.dataset._stat(binby=self.get_binby(), what=self.what, limits=self.limits,
                                        shape=self.get_shape(), progress=pb,
                                        selection=self.active_selections(), delay=True)
            if delay:
                promises.append(result)
            else:
                self.grid = result

            vs = [self.vx, self.vy, self.vz]
            for i, v in enumerate(vs):
                result = None
                if v:
                    result = self.dataset.mean(v, binby=self.get_binby(), limits=self.limits,
                                               shape=self.get_vshape(), progress=self._progressbar.add("v" + str(i)),
                                               selection=self.active_selections(), delay=delay)
                if delay:
                    promises.append(result)
                else:
                    self.vgrids[i] = result
            result = None
            if any(vs):
                expr = "*".join([v for v in vs if v])
                result = self.dataset.count(expr, binby=self.get_binby(), limits=self.limits,
                                            shape=self.get_vshape(), progress=self._progressbar.add("vcount"),
                                             selection=self.active_selections(), delay=delay)
            if delay:
                promises.append(result)
            else:
                self.vgrids[i] = result
            @delayed
            def assign(grid, vx, vy, vz, vcount):
                with self.output:
                    if not current_pb.cancelled:  # TODO: remote dataset jobs cannot be cancelled
                        self.progress.value = 0
                        self.grid = grid
                        self.vgrids = [vx, vy, vz]
                        self.vcount = vcount
                        self._update_image()
            if delay:
                for promise in promises:
                    if promise:
                        promise.end()
                assign(*promises).end()
                self._execute()
            else:
                self._update_image()

    @debounced(0.05, method=True)
    def _execute(self):
        with self.output:
            self.dataset.execute()

    @debounced(0.5, method=True)
    def update_image(self):
        self._update_image()

    def _update_image(self):
        with self.output:
            grid = self.get_grid().copy()  # we may modify inplace
            f = _parse_f(self.f)
            with np.errstate(divide='ignore', invalid='ignore'):
                fgrid = f(grid)
            self.grid_limits = [0, 8]

            y_lo, y_hi = self.backend.limits[1]
            x_lo, x_hi = self.backend.limits[0]
            cache_size = 1000 # Fix this default
            diffy = y_hi - y_lo
            diffx = x_hi - x_lo
            new_size = 0
            curr_scale = max(diffx, diffy)
            new_size = int(min(32, self.shape//curr_scale))
            if new_size > 1:
                row = col = 0
                rows = len(fgrid[0])
                cols = len(fgrid[0][0])
                n_fgrid = copy.deepcopy(fgrid)
                for row in range(rows-1, -1, -1):
                    for col in range(cols):
                        val = fgrid[0][row][col]
                        if val != 0:
                            for i in range(row, max(-1, row-new_size), -1):
                                for j in range(col, min(cols,col+new_size)):
                                    if fgrid[0][i][j] == 0:
                                        n_fgrid[0][i][j] = val
                fgrid = n_fgrid

            cache_fraction = min(1, cache_size/diffy)
            lim = cache_fraction*fgrid.shape[1]
            for i in range(int(lim)):
                fgrid[0][0][i] = 2.4

            ngrid, fmin, fmax = self.normalise(fgrid)
            if self.backend.wants_colors():
                color_grid = self.colorize(ngrid)
                if len(color_grid.shape) > 3:
                    if len(color_grid.shape) == 4:
                        if color_grid.shape[0] > 1:
                            color_grid = vaex.image.fade(color_grid[::-1])
                        else:
                            color_grid = color_grid[0]
                    else:
                        raise ValueError("image shape is %r, don't know what to do with that, expected (L, M, N, 3)" % (color_grid.shape,))
                I = np.rot90(color_grid).copy()
                self.backend.update_image(I)
            else:
                self.backend.update_image(ngrid[-1])
    def get_grid(self):
        return self.grid

    def get_vgrids(self):
        return self.vgrids[0], self.vgrids[1], self.vgrids[2], self.vcount

    def colorize(self, grid):
        return _parse_reduction("colormap", self.colormap, [])(grid)

    def normalise(self, grid):
        if self.grid_limits is not None:
            vmin, vmax = self.grid_limits
            grid = grid.copy()
            grid -= vmin
            if vmin == vmax:
                grid = grid * 0
            else:
                grid /= (vmax - vmin)
        else:
            n = _parse_n(self.normalize)
            grid, vmin, vmax = n(grid)
        return grid, vmin, vmax


@register_type("default")
class Plot2dDefault(PlotBase):
    y = traitlets.Unicode(allow_none=False).tag(sync=True)

    def __init__(self, **kwargs):
        super(Plot2dDefault, self).__init__(**kwargs)

    def colorize(self, grid):
        if self.z:
            grid = grid.copy()
            grid[~np.isfinite(grid)] = 0
            total = np.sum(grid, axis=-1)
            mask = total == 0
            import matplotlib.cm
            colormap = matplotlib.cm.get_cmap(self.colormap)
            N = grid.shape[-1]
            z = np.linspace(0, 1, N, endpoint=True)
            colors = colormap(z)
            cgrid = np.dot(grid, colors)
            cgrid = (cgrid.T / total.T).T
            n = _parse_n(self.normalize)
            ntotal, __, __ = n(total)
            cgrid[mask, 3] = 0
            return cgrid
        else:
            return _parse_reduction("colormap", self.colormap, [])(grid)

    def get_shape(self):
        if self.z:
            if ":" in self.z:
                shapez = int(self.z.split(":")[1])
                shape = _expand_shape(self.shape, 2) + (shapez,)
            else:
                shape = _expand_shape(self.shape, 3)
            return shape
        else:
            return super(Plot2dDefault, self).get_shape()

    def get_binby(self):
        if self.z:
            z = self.z
            if ":" in z:
                z = z.split(":")[0]
            return [self.x, self.y, z]
        else:
            return [self.x, self.y]


@register_type("slice")
class Plot2dSliced(PlotBase):
    z = traitlets.Unicode(allow_none=False).tag(sync=True)
    z_slice = traitlets.CInt(default_value=0).tag(sync=True)  # .tag(sync=True) # TODO: do linking at python side
    z_shape = traitlets.CInt(default_value=10).tag(sync=True)
    z_relative = traitlets.CBool(False).tag(sync=True)
    z_min = traitlets.CFloat(default_value=None, allow_none=True).tag(sync=True)  # .tag(sync=True)
    z_max = traitlets.CFloat(default_value=None, allow_none=True).tag(sync=True)  # .tag(sync=True)
    z_select = traitlets.CBool(default_value=True)

    def __init__(self, **kwargs):
        self.z_min_extreme, self.z_max_extreme = kwargs["dataset"].minmax(kwargs["z"])
        super(Plot2dSliced, self).__init__(**kwargs)
        self.create_tools()

    def get_limits(self, limits):
        limits = self.dataset.limits(self.get_binby(), limits)
        limits = list([list(k) for k in limits])
        if self.z_min is None:
            self.z_min = limits[2][0]
        if self.z_max is None:
            self.z_max = limits[2][1]
        limits[2][0] = self.z_min
        limits[2][1] = self.z_max
        return limits

    def select_rectangle(self, x1, y1, x2, y2, mode="replace"):
        name = _translate_selection(self.widget_selection_active.value)
        dz = self.z_max - self.z_min
        z1 = self.z_min + dz * self.z_slice / self.z_shape
        z2 = self.z_min + dz * (self.z_slice + 1) / self.z_shape
        spaces = [self.x, self.y]
        limits = [[x1, x2], [y1, y2]]
        if self.z_select:
            spaces += [self.z]
            limits += [[z1, z2]]
        self.dataset.select_box(spaces, limits=limits, mode=self.widget_selection_mode.value, name=name)

    def select_lasso(self, x, y, mode="replace"):
        raise NotImplementedError("todo")

    def get_grid(self):
        zslice = self.grid[..., self.z_slice]
        if self.z_relative:
            with np.errstate(divide='ignore', invalid='ignore'):
                zslice = zslice / self.grid.sum(axis=-1)
        return zslice
        # return self.grid[...,self.z_slice]

    def get_vgrids(self):
        def zsliced(grid):
            return grid[..., self.z_slice] if grid is not None else None
        return [zsliced(grid) for grid in super(Plot2dSliced, self).get_vgrids()]

    def create_tools(self):
        # super(Plot2dSliced, self).create_tools()
        self.z_slice_slider = widgets.IntSlider(value=self.z_slice, min=0, max=self.z_shape - 1)
        # self.add_control_widget(self.z_slice_slider)
        self.z_slice_slider.observe(self._z_slice_changed, "value")
        self.observe(self._z_slice_changed, "z_slice")

        dz = self.z_max_extreme - self.z_min_extreme

        self.z_range_slider = widgets.FloatRangeSlider(min=min(self.z_min, self.z_min_extreme), value=[self.z_min, self.z_max],
                                                       max=max(self.z_max, self.z_max_extreme), step=dz / 1000)
        self.z_range_slider.observe(self._z_range_changed_, names=["value"])
        # self.observe(self.z_range_slider, "z_min")

        self.z_control = widgets.VBox([self.z_slice_slider, self.z_range_slider])
        self.add_control_widget(self.z_control)

        if self.controls_selection:
            self.widget_z_select = widgets.Checkbox(description='select z range', value=self.z_select)
            widgets.link((self, 'z_select'), (self.widget_z_select, 'value'))
            self.add_control_widget(self.widget_z_select)


    def _z_range_changed_(self, changes, **kwargs):
        # print("changes1", changes, repr(changes), kwargs)
        self.limits[2][0], self.limits[2][1] =\
            self.z_min, self.z_max = self.z_range_slider.value = changes["new"]
        self.update_grid()

    def _z_slice_changed(self, changes):
        self.z_slice = self.z_slice_slider.value = changes["new"]
        self._update_image()

    def get_shape(self):
        return _expand_shape(self.shape, 2) + (self.z_shape, )

    def get_vshape(self):
        return _expand_shape(self.vshape, 2) + (self.z_shape, )

    def get_binby(self):
        return [self.x, self.y, self.z]
