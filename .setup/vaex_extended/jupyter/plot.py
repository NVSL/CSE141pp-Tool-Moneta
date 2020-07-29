import vaex.jupyter.plot
from vaex.jupyter.plot import *
from vaex.jupyter.plot import _ensure_list, _expand, _parse_f, _parse_n, _parse_reduction, _expand_shape
from traitlets import *

from vaex_extended.jupyter.widgets import PlotTemplate as PlotTemplate_v2
import vaex_extended
import copy

class Plot2dDefault(Plot2dDefault):
    
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
        if 'default_title' in kwargs:
            self.default_title = kwargs.get('default_title')
        else:
            self.default_title = 'Moneta'
        self.widget = PlotTemplate_v2(components={
                        #'main-widget': widgets.VBox([self.backend.widget, self.progress, self.output]),
                        'main-widget': widgets.VBox([widgets.HBox([self.backend.widget,self.legend]), self.progress, self.output]),
                        'control-widget': self.control_widget,
                        'output-widget': self.output,
                        'toolbox': self.backend.widget_menubar,
                        'default_title': self.default_title
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
            cache_size = vaex_extended.vaex_cache_size
            diff = y_hi - y_lo
            cache_fraction = min(1, cache_size/diff)
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
    
