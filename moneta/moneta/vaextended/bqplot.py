# # alternate wrapper version in case the function should be left alone
# def fix_image_flipping(func):
#     from functools import wraps
#     @wraps(func)
#     def wrapper(self,rgb_image):
#         return func(self, np.flipud(rgb_image))
#     return wrapper
# BqplotBackend.update_image = fix_image_flipping(BqplotBackend.update_image)


from vaex.jupyter.plot import BackendBase
from vaex.jupyter.utils import debounced
import vaex
import numpy as np
import bqplot
import bqplot.pyplot as plt
import ipywidgets as widgets
import ipyvuetify as v
import copy

blackish = '#666'


accessRanges = {}
ZOOM_SELECT = 'Zoom to Selection'
PAN_ZOOM = 'Pan Zoom'
RESET_ZOOM = 'Reset Zoom'

UNDO = 'Undo'
REDO = 'Redo'

from enum import Enum
class Action(Enum):
    other = 0
    undo = 1
    redo = 2

PANZOOM_HISTORY_LIMIT = 50


class BqplotBackend(BackendBase):
    def __init__(self, figure=None, figure_key=None):
        self._dirty = False
        self.figure_key = figure_key
        self.figure = figure
        self.signal_limits = vaex.events.Signal()

        self._cleanups = []

    def update_image(self, rgb_image):
        
        with self.output:
            rgb_image = (rgb_image * 255.).astype(np.uint8)
            pil_image = vaex.image.rgba_2_pil(rgb_image)
            data = vaex.image.pil_2_data(pil_image)
            self.core_image.value = data
            # force update
            self.image.image = self.core_image_fix
            self.image.image = self.core_image
            self.image.x = (self.scale_x.min, self.scale_x.max)
            #self.image.y = (self.scale_y.min, self.scale_y.max)
            self.image.y = (self.limits[1][0], self.limits[1][1])
            self.plot.update_stats()

    def create_widget(self, output, plot, dataset, limits):
        self.plot = plot
        self.output = output
        self.dataset = dataset
        self.limits = np.array(limits).tolist()
        def fix(v):
            # bqplot is picky about float and numpy scalars
            if hasattr(v, 'item'):
                return v.item()
            else:
                return v
        self.scale_x = bqplot.LinearScale(min=fix(limits[0][0]), max=fix(limits[0][1]), allow_padding=False)
        self.scale_y = bqplot.LinearScale(min=fix(limits[1][0]), max=fix(limits[1][1]), allow_padding=False)
        self.scales = {'x': self.scale_x, 'y': self.scale_y}

        self.figure = plt.figure(self.figure_key, fig=self.figure, scales=self.scales)
        self.figure.layout.width = 'calc(100% - 300px)'
        self.figure.layout.min_height = '800px'
        plt.figure(fig=self.figure)
        #self.figure.padding_y = 0
        x = np.arange(0, 10)
        y = x ** 2
        self.core_image = widgets.Image(format='png')
        self.core_image_fix = widgets.Image(format='png')

        self.image = bqplot.Image(scales=self.scales, image=self.core_image)
        self.figure.marks = self.figure.marks + [self.image]
        self.scatter = s = plt.scatter(x, y, visible=False, rotation=x, scales=self.scales, size=x, marker="arrow")
        self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})
        self.figure.interaction = self.panzoom
        for axes in self.figure.axes:
            axes.grid_lines = 'none'
            axes.color = axes.grid_color = axes.label_color = blackish
        self.figure.axes[0].label = str(plot.x)
        self.figure.axes[1].label = str(plot.y)
        self.figure.axes[1].scale = bqplot.LinearScale(min = 0, max=self.scale_y.max-self.scale_y.min, allow_padding=False)

        self.curr_action = Action.other
        self.undo_actions = list()
        self.redo_actions = list()
        self.counter = 2
        self.scale_x.observe(self._update_limits)
        self.scale_y.observe(self._update_limits)
        self.widget = widgets.VBox([self.figure])
        self.create_tools()

    @debounced(0.2, method=True)
    def _update_limits(self, *args):
        with self.output:
            limits = copy.deepcopy(self.limits)
            limits[0:2] = [[scale.min, scale.max] for scale in [self.scale_x, self.scale_y]]
            self.figure.axes[1].scale=bqplot.LinearScale(min=0, max=self.scale_y.max-self.scale_y.min, allow_padding=False)
            if self.counter == 2:
                if self.curr_action in [Action.redo, Action.other]:
                    self.undo_btn.disabled = False
                    self.undo_actions.append(self.limits)
                    if len(self.undo_actions) > PANZOOM_HISTORY_LIMIT:
                        self.undo_actions.pop(0)
                    if self.curr_action == Action.redo:
                        self.redo_actions.pop()
                        if len(self.redo_actions) == 0:
                            self.redo_btn.disabled = True
                    else:
                        self.redo_btn.disabled = True
                        self.redo_actions.clear()
                elif self.curr_action == Action.undo:
                    self.redo_btn.disabled = False
                    self.redo_actions.append(self.limits)
                    if len(self.redo_actions) > PANZOOM_HISTORY_LIMIT:
                        self.redo_actions.pop(0)
                    self.undo_actions.pop()
                    if len(self.undo_actions) == 0:
                        self.undo_btn.disabled = True
                self.curr_action = Action.other
                self.counter = 1
                self._update_limits(self, *args)
            else:
                self.counter = 2

            self.limits = limits

    def create_tools(self):
        self.tools = []
        tool_actions = []
        tool_actions_map = dict()

        if 1:  # tool_select:
            self.zoom_brush = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="blue")
            self.zoom_brush.observe(self.update_zoom_brush, ["brushing"])
            tool_actions_map[ZOOM_SELECT] = self.zoom_brush
            tool_actions_map[PAN_ZOOM] = self.panzoom
            tool_actions = [PAN_ZOOM, ZOOM_SELECT]

            self.start_limits = copy.deepcopy(self.limits)

            def change_interact(*args):
                with self.output:
                    name = tool_actions[self.interaction_tooltips.v_model]
                    self.figure.interaction = tool_actions_map[name]

            self.interaction_tooltips = \
                v.BtnToggle(v_model=0, mandatory=True, multiple=False, children=[
                                v.Tooltip(bottom=True, v_slots=[{
                                    'name': 'activator',
                                    'variable': 'tooltip',
                                    'children': v.Btn(v_on='tooltip.on', children=[
                                        v.Icon(children=['pan_tool'])
                                    ])
                                }], children=[PAN_ZOOM]),
                                v.Tooltip(bottom=True, v_slots=[{
                                    'name': 'activator',
                                    'variable': 'tooltip',
                                    'children': v.Btn(v_on='tooltip.on', children=[
                                        v.Icon(children=['crop'])
                                    ])
                                }], children=[ZOOM_SELECT]),
                            ])
            self.interaction_tooltips.observe(change_interact, "v_model")

            def reset(*args):
                (x1, x2), (y1, y2) = self.start_limits
                with self.scale_x.hold_trait_notifications():
                    with self.scale_y.hold_trait_notifications():
                        self.scale_x.min, self.scale_x.max = x1, x2
                        self.scale_y.min, self.scale_y.max = y1, y2
                with self.zoom_brush.hold_trait_notifications():
                    self.zoom_brush.selected_x = None
                    self.zoom_brush.selected_y = None
            self.reset_btn = v.Btn(v_on='tooltip.on', icon=True, children=[
                                    v.Icon(children=['refresh'])
                                ])
            self.reset_btn.on_event('click', lambda *ignore: reset())
            self.reset_tooltip = v.Tooltip(bottom=True, v_slots=[{
                                    'name': 'activator',
                                    'variable': 'tooltip',
                                    'children': self.reset_btn
                                }], children=[RESET_ZOOM])

            self.undo_btn = v.Btn(v_on='tooltip.on', icon=True, disabled=True, children=[
                                    v.Icon(children=['undo'])
                                ])
            self.undo_tooltip = v.Tooltip(bottom=True, v_slots=[{
                                    'name': 'activator',
                                    'variable': 'tooltip',
                                    'children': self.undo_btn
                                }], children=[UNDO])
            self.redo_btn = v.Btn(v_on='tooltip.on', icon=True, disabled=True, children=[
                                    v.Icon(children=['redo'])
                                ])
            self.redo_tooltip = v.Tooltip(bottom=True, v_slots=[{
                                    'name': 'activator',
                                    'variable': 'tooltip',
                                    'children': self.redo_btn
                                }], children=[REDO])
            @debounced(0.5)
            def undo_redo(*args):
                print(self.undo_actions)
                self.curr_action = args[0]
                (x1, x2), (y1, y2) = args[1][-1]
                with self.scale_x.hold_trait_notifications():
                    with self.scale_y.hold_trait_notifications():
                        self.scale_x.min, self.scale_x.max = x1, x2
                        self.scale_y.min, self.scale_y.max = y1, y2
            self.undo_btn.on_event('click', lambda *ignore: undo_redo(Action.undo, self.undo_actions))
            self.redo_btn.on_event('click', lambda *ignore: undo_redo(Action.redo, self.redo_actions))

            control_lyt = widgets.Layout(width='40px')
            self.panzoom_x = control_x = widgets.Checkbox(value=True,description='X',indent=False, layout=control_lyt)
            self.panzoom_y = control_y = widgets.Checkbox(value=True,description='Y',indent=False, layout=control_lyt)
            def update_panzoom(checkbox):
                if control_x.value:
                    if control_y.value:
                        self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})
                    else:
                        self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x]})
                else:
                    if control_y.value:
                        self.panzoom = bqplot.PanZoom(scales={'y': [self.scale_y]})
                    else:
                        self.panzoom = bqplot.PanZoom()
                tool_actions_map[PAN_ZOOM] = self.panzoom
                # Update immediately if in PAN_ZOOM mode
                name = tool_actions[self.interaction_tooltips.v_model]
                if name == PAN_ZOOM:
                  self.figure.interaction = self.panzoom

            self.panzoom_x.observe(update_panzoom)
            self.panzoom_y.observe(update_panzoom)
            self.panzoom_controls = widgets.VBox([self.panzoom_x,self.panzoom_y])

            self.tooltips = v.Row(children=[
                    self.panzoom_controls, 
                    self.interaction_tooltips, 
                    self.reset_tooltip,
                    self.undo_tooltip,
                    self.redo_tooltip
                ], align='center', justify='center')
            self.plot.add_to_toolbar(self.tooltips)


    def update_zoom_brush(self, *args):
        with self.output:
            if not self.zoom_brush.brushing: # Update on mouse up
                self.figure.interaction = None
            if self.zoom_brush.selected is not None:
                (x1, y1), (x2, y2) = self.zoom_brush.selected
                df = self.dataset
                ind = self.plot.x_label
                addr = self.plot.y_label
                res = df[(df[ind] >= x1) & (df[ind] <= x2) & (df[addr] >= y1) & (df[addr] <= y2)]
                if res.count() != 0:
                    x1 = res[ind].values[0]
                    x2 = res[ind].values[-1]
                    y1 = res[addr].min()[()]
                    y2 = res[addr].max()[()]

                # Fix for plot getting stuck at one value axis
                if (x2 - x1 < 128):
                    x1 -= (128 + x1 - x2) / 2
                    x2 = x1 + 128

                if (y2 - y1 < 128):
                    y1 -= (128 + y1 - y2) / 2
                    y2 = y1 + 128
                
                # Add a 5% padding so points are directly on edge
                padding_x = (x2 - x1) * 0.05
                padding_y = (y2 - y1) * 0.05

                x1 = x1 - padding_x
                x2 = x2 + padding_x
                y1 = y1 - padding_y
                y2 = y2 + padding_y

                with self.scale_y.hold_trait_notifications():
                    self.scale_y.min, self.scale_y.max = y1, y2
                with self.scale_x.hold_trait_notifications():
                    self.scale_x.min, self.scale_x.max = x1, x2
                self.plot.update_grid()
            if not self.zoom_brush.brushing: # Update on mouse up
                self.figure.interaction = self.zoom_brush
            with self.zoom_brush.hold_trait_notifications(): # Delete selection
                self.zoom_brush.selected_x = None
                self.zoom_brush.selected_y = None

    def zoom_sel(self, x1, x2, y1, y2):
        with self.scale_x.hold_trait_notifications():
            self.scale_x.min = x1
            self.scale_x.max = x2
        with self.scale_y.hold_trait_notifications():
            self.scale_y.min = y1
            self.scale_y.max = y2
