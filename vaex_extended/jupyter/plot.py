import vaex.jupyter.plot
from vaex.jupyter.plot import *
from vaex.jupyter.plot import _ensure_list, _expand, _parse_f, _parse_n, _parse_reduction, _expand_shape
from traitlets import *

from vaex_extended.jupyter.widgets import PlotTemplate as PlotTemplate_v2

class Plot2dDefault(Plot2dDefault):
    
    #colormap = traitlets.Any(allow_none=False).tag(sync=True)
    #draw_cache = traitlets.Bool(allow_none=True).tag(sync=True)
    def __init__(self, **kwargs):
        super(Plot2dDefault, self).__init__(**kwargs)
        self.widgetLegend = widgets.Output()
        with self.widgetLegend:
            import matplotlib.pyplot as mplplt
            colors = [[0,0,1,1], [0,1,1,1], [0.047,1,0,1],[1,1,0,1],[1,0,0,1],[0.737,0.745,0.235,1], [0.745,0.309,0.235,1]]
            f = lambda m,c: mplplt.plot([],[],marker=m, color=c, ls="none")[0]
            handles = [f("s", colors[i]) for i in range(7)]
            labels = ["read hits","write hits","read misses","write misses","compulsory read misses","compulsory write misses"]
            legend = mplplt.legend(handles,labels,loc=1,framealpha=1,frameon=True,prop={"size":20})
            #def draw_legend(legend, expand=[-10,-10,10,10]):
            #    fig = legend.figure
            #    fig.canvas.draw()
            #    bbox = legend.get_window_extent()
            #    bbox = bbox.from_extents(*(bbox.extents + np.array(expand)))
            #    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
            #draw_legend(legend)
            mplplt.gca().set_axis_off()      

        self.legend = widgets.VBox([]) 
        if 'legend' in kwargs:
            self.legend = kwargs.get('legend')
        if 'draw_cache' in kwargs:
            self.draw_cache = kwargs.get('draw_cache')
        self.widget = PlotTemplate_v2(components={
                        #'main-widget': widgets.VBox([self.backend.widget, self.progress, self.output]),
                        'main-widget': widgets.VBox([widgets.HBox([self.backend.widget,self.legend]), self.progress, self.output]),
                        'control-widget': self.control_widget,
                        'output-widget': self.output,
                        'toolbox': self.backend.widget_menubar
                    },
                    model=False
            )

