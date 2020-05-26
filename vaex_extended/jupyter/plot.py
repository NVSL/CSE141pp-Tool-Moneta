import vaex.jupyter.plot
from vaex.jupyter.plot import *
from vaex.jupyter.plot import _ensure_list, _expand, _parse_f, _parse_n, _parse_reduction, _expand_shape
from traitlets import *

from vaex_extended.jupyter.widgets import PlotTemplate as PlotTemplate_v2

class Plot2dDefault(Plot2dDefault):
    def __init__(self, **kwargs):
        super(Plot2dDefault, self).__init__(**kwargs)
        self.widget = PlotTemplate_v2(components={
                        'main-widget': widgets.VBox([self.backend.widget, self.progress, self.output]),
                        'control-widget': self.control_widget,
                        'output-widget': self.output,
                        'toolbox': self.backend.widget_menubar
                    },
                    model=False
            )

