#import vaex.jupyter.plot
#from vaex.jupyter.plot import *
#from vaex.jupyter.plot import _ensure_list, _expand, _parse_f, _parse_n, _parse_reduction, _expand_shape
#from traitlets import *

#from vaex_extended.jupyter.widgets import PlotTemplate as PlotTemplate_v2
#import vaex_extended
#import copy

import traitlets
import ipywidgets as widgets
import ipyvuetify as v
from vaex.jupyter.utils import debounced
import vaex
from vaex_extended.jupyter.widgets import PlotTemplate
from vaex.delayed import delayed, delayed_list
from vaex.utils import _ensure_list, _expand, _parse_f, _parse_n, _parse_reduction, _expand_shape
from IPython.display import display
import numpy as np
import copy

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
        print("vaex extended plot base init")
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

            if 'legend' in kwargs:
                self.legend = kwargs.get('legend')
            self.widget = PlotTemplate(components={
                        'main-widget': widgets.VBox([widgets.HBox([self.backend.widget, self.legend], layout=widgets.Layout(margin="50px 10px 10px 10px")), self.progress, self.output]),
                        'output-widget': self.output,
                        'extra-widget': self.extra_widget
                    },
                    model=show_drawer
            )
            if grid is None:
                self.update_grid()
            else:
                self.grid = grid

            # checkboxes work because of this
            callback = self.dataset.signal_selection_changed.connect(lambda *x: self.update_grid())

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
        print("in extra widget adding")
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

    def get_binby(self):
        if self.z:
            z = self.z
            if ":" in z:
                z = z.split(":")[0]
            return [self.x, self.y, z]
        else:
            return [self.x, self.y]




"""
class Plot2dDefault(Plot2dDefault):
"""
"""
    #colormap = traitlets.Any(allow_none=False).tag(sync=True)
    #draw_cache = traitlets.Bool(allow_none=True).tag(sync=True)
    def __init__(self, **kwargs):
        super(Plot2dDefault, self).__init__(**kwargs)
        # self.widgetLegend = widgets.Output()
        # with self.widgetLegend:
        #     import matplotlib.pyplot as mplplt
        #     colors = [[0,0,1,1], [0,1,1,1], [0.047,1,0,1],[1,1,0,1],[1,0,0,1],[0.737,0.745,0.235,1], [0.745,0.309,0.235,1]]
        #     f = lambda m,c: mplplt.plot([],[],marker=m, color=c, ls="none")[0]
        #     handles = [f("s", colors[i]) for i in range(7)]
        #     labels = ["read hits","write hits","read misses","write misses","compulsory read misses","compulsory write misses"]
        #     legend = mplplt.legend(handles,labels,loc=1,framealpha=1,frameon=True,prop={"size":20})
        #     #def draw_legend(legend, expand=[-10,-10,10,10]):
        #     #    fig = legend.figure
        #     #    fig.canvas.draw()
        #     #    bbox = legend.get_window_extent()
        #     #    bbox = bbox.from_extents(*(bbox.extents + np.array(expand)))
        #     #    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
        #     #draw_legend(legend)
        #     mplplt.gca().set_axis_off()      
        
        self.legend = widgets.VBox([]) 
        if 'legend' in kwargs:
            self.legend = kwargs.get('legend')
        if 'update_stats' in kwargs:
            #self.update_stats = kwargs.get('update_stats')
            setattr(self.__class__, '_update_stats', kwargs.get('update_stats'))
        else:
            self.update_stats = lambda *args, **kwargs: None
        self.widget = PlotTemplate_v2(components={
                        #'main-widget': widgets.VBox([self.backend.widget, self.progress, self.output]),
                        'main-widget': widgets.VBox([widgets.HBox([self.backend.widget,self.legend]), self.progress, self.output]),
                        'control-widget': self.control_widget,
                        'output-widget': self.output,
                        'toolbox': self.backend.widget_menubar
                    },
                    model=False
            )
    @debounced(0.3, method=True)
    def update_stats(self):
        self._update_stats()
    def _update_image(self):
        self.update_stats()
        with self.output:
            grid = self.get_grid().copy()  # we may modify inplace
            if self.smooth_pre:
                for i in range(grid.shape[0]):  # seperately for every selection
                    grid[i] = vaex.grids.gf(grid[i], self.smooth_pre)
            #f = _parse_f(self.f)
            #with np.errstate(divide='ignore', invalid='ignore'):
            #    fgrid = f(grid)
            fgrid = grid
            try:
                #mask = np.isfinite(fgrid)
                #vmin, vmax = np.percentile(fgrid[mask], [self.grid_limits_min, self.grid_limits_max])
                #self.grid_limits = [vmin, vmax]
                self.grid_limits = [0, 8] # Make scale invariant
                #print("backend limits ", self.backend.limits)
            except:
                pass
            if self.smooth_post:
                for i in range(grid.shape[0]):
                    fgrid[i] = vaex.grids.gf(fgrid[i], self.smooth_post)
            y_lo, y_hi = self.backend.limits[1]
            x_lo, x_hi = self.backend.limits[0]
            cache_size = vaex_extended.vaex_cache_size
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
                I = np.transpose(color_grid, (1, 0, 2)).copy()
                #I = np.transpose(color_grid, (1, 0, 2)).copy()
                # if self.what == "count(*)":
                #     I[...,3] = self.normalise(np.sqrt(grid))[0]
                self.backend.update_image(I)
            else:
                self.backend.update_image(ngrid[-1])
            self.backend.update_vectors(self.vcount, self.vgrids, self.vcount_limits)
            return
            src = vaex.image.rgba_to_url(I)
            self.image.src = src
            # self.scale_x.min, self.scale_x.max = self.limits[0]
            # self.scale_y.min, self.scale_y.max = self.limits[1]
            self.image.x = self.scale_x.min
            self.image.y = self.scale_y.max
            self.image.width = self.scale_x.max - self.scale_x.min
            self.image.height = -(self.scale_y.max - self.scale_y.min)
    
            vx, vy, vz, vcount = self.get_vgrids()
            if vx is not None and vy is not None and vcount is not None:
                # print(vx.shape)
                vx = vx[-1]
                vy = vy[-1]
                vcount = vcount[-1].flatten()
                vx = vx.flatten()
                vy = vy.flatten()
    
                xmin, xmax = self.limits[0]
                ymin, ymax = self.limits[1]
                centers_x = np.linspace(xmin, xmax, self.vshape, endpoint=False)
                centers_x += (centers_x[1] - centers_x[0]) / 2
                centers_y = np.linspace(ymin, ymax, self.vshape, endpoint=False)
                centers_y += (centers_y[1] - centers_y[0]) / 2
                # y, x = np.meshgrid(centers_y, centers_x)
                x, y = np.meshgrid(centers_x, centers_y)
                x = x.T
                y = y.T
                x = x.flatten()
                y = y.flatten()
                mask = vcount > 5
                # print(xmin, xmax, x)
                self.scatter.x = x * 1.
                self.scatter.y = y * 1.
                angle = -np.arctan2(vy, vx) + np.pi / 2
                self.scale_rotation.min = 0
                self.scale_rotation.max = np.pi
                angle[~mask] = 0
                self.scatter.rotation = angle
                # self.scale.size = mask * 3
                # self.scale.size = mask.asdtype(np.float64) * 3
                self.vmask = mask
                self.scatter.size = self.vmask * 2 - 1
                # .asdtype(np.float64)
    
                self.scatter.visible = True
                self.scatter.visible = len(x[mask]) > 0
                # self.scatter.marker = "arrow"
                # print("UpDated")
"""    
