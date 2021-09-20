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
from IPython.display import Image as IPyImage
from IPython.display import clear_output

from moneta.settings import TextStyle, WARNING_LABEL
from PIL import Image

blackish = '#666'


accessRanges = {}
ZOOM_SELECT = 'Zoom to Selection'
PAN_ZOOM = 'Pan Zoom test1'
RESET_ZOOM = 'Reset Zoom'
CLICK_ZOOM_IN = 'Click Zoom IN'
CLICK_ZOOM_OUT = 'Click Zoom OUT'
CLICK_ZOOM_SCALE = 0.1 # 10x zoom
SCREENSHOT = 'Screenshot Test'
RULER = "Measurement"

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
        # self.coor_x = 0
        # self.coor_y = 0
        self.czoom_xmin = 0
        self.czoom_xmax = 0
        self.czoom_ymin = 0
        self.czoom_ymax = 0
        self.res = 0
        self._observers = []


    def update_image(self, rgb_image):
        with self.output:
            rgb_image = (rgb_image * 255.).astype(np.uint8)
            pil_image = vaex.image.rgba_2_pil(rgb_image)
            self.pil_image_test = pil_image
            
            data = vaex.image.pil_2_data(pil_image)
            self.core_image.value = data
            # force update
            self.image.image = self.core_image_fix
            self.image.image = self.core_image
            self.image.x = (self.scale_x.min, self.scale_x.max)
            #self.image.y = (self.scale_y.min, self.scale_y.max)
            self.image.y = (self.limits[1][0], self.limits[1][1])
            self.base_address.value = f"Base address: 0x{int(self.limits[1][0]):X}"
            self.zoom_args.value = self.zoom_args_string()
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
        self.figure.layout.width = 'calc(100% - 400px)'
        self.figure.layout.min_height = '800px'
        plt.figure(fig=self.figure)
        #self.figure.padding_y = 0
        x = np.arange(0, 10)
        y = x ** 2
        self.core_image = widgets.Image(format='png')
        self.core_image_fix = widgets.Image(format='png')

        self.image = bqplot.Image(scales=self.scales, image=self.core_image)
        # triggered by regular mouse click not a brush selector
        self.image.on_element_click(self.click_to_zoom)
        
        self.figure.marks = self.figure.marks + [self.image]
        self.scatter = s = plt.scatter(x, y, visible=False, rotation=x, scales=self.scales, size=x, marker="arrow")
        self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})
        self.figure.interaction = self.panzoom
        for axes in self.figure.axes:
            axes.grid_lines = 'none'
            axes.color = axes.grid_color = axes.label_color = blackish
        self.figure.axes[0].label = plot.x_label
        self.figure.axes[1].label = plot.y_label
        self.figure.axes[1].scale = bqplot.LinearScale(min = 0, max=self.scale_y.max-self.scale_y.min, allow_padding=False)
        self.stuck_ctr = 0

        self.base_address = widgets.Label(value=f"Base address: 0x{int(self.limits[1][0]):X}")
        self.zoom_args = widgets.Text(
            description="Zoom Args", 
            value=self.zoom_args_string(), 
            disabled=True, 
            style={'description_width':'initial'},
            layout=widgets.Layout(width='50%')
        )

        self.curr_action = Action.other
        self.undo_actions = list()
        self.redo_actions = list()
        self.counter = 2
        self.scale_x.observe(self._update_limits)
        self.scale_y.observe(self._update_limits)
        self.widget = widgets.VBox([self.figure, self.base_address, self.zoom_args])
        self.create_tools()

    @debounced(0.2, method=True)
    def _update_limits(self, *args):
        with self.output:
            limits = copy.deepcopy(self.limits)
            limits[0:2] = [[scale.min, scale.max] for scale in [self.scale_x, self.scale_y]]
            self.figure.axes[1].scale=bqplot.LinearScale(min=0, max=self.scale_y.max-self.scale_y.min, allow_padding=False)
            self.figure.axes[0].scale=bqplot.LinearScale(min=self.scale_x.min, max=self.scale_x.max, allow_padding=False)
            if self.counter == 2:
                self.output.clear_output() # Disable when debugging
                self.stuck_ctr = 0
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
        self.tool_actions = []
        tool_actions_map = dict()

        if 1:  # tool_select:
            #### initiaite the 4 types of zoom brushes, which should only highlight axis that are not locked ###
            self.zoom_brush_full = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="blue")
            self.zoom_brush_full.observe(self.update_zoom_brush_full, ["brushing"])
            
            self.zoom_brush_vertical =  bqplot.interacts.BrushIntervalSelector(scale=self.scale_y, orientation='vertical', color="blue")
            self.zoom_brush_vertical.observe(self.update_zoom_brush_vertical, ["brushing"])

            self.zoom_brush_horizontal =  bqplot.interacts.BrushIntervalSelector(scale=self.scale_x, orientation='horizontal', color="blue")
            self.zoom_brush_horizontal.observe(self.update_zoom_brush_horizontal, ["brushing"])

            self.zoom_brush_none = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="gray")
            self.zoom_brush_none.observe(self.update_zoom_brush_none, ["brushing"])

            # initiaite measurement tool
            self.ruler = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="blue")
            self.ruler.observe(self.measure_selected_area, ["brushing"])
            #### Set the default initial tools ####
            self.zoom_brush = self.zoom_brush_full  
            self.click_brush = None # use regular mouse
            self.click_brush_in = None 
            self.click_brush_out = None

            tool_actions_map[ZOOM_SELECT] = self.zoom_brush
            tool_actions_map[PAN_ZOOM] = self.panzoom
            tool_actions_map[CLICK_ZOOM_IN] = self.click_brush_in
            tool_actions_map[CLICK_ZOOM_OUT] = self.click_brush_out
            tool_actions_map[RULER] = self.ruler
            self.tool_actions = [PAN_ZOOM, ZOOM_SELECT,
                                 CLICK_ZOOM_IN, CLICK_ZOOM_OUT, RULER]

            self.start_limits = copy.deepcopy(self.limits)

            def change_interact(*args):
                with self.output:
                    name = self.tool_actions[self.interaction_tooltips.v_model]
                    self.figure.interaction = tool_actions_map[name]
                    if name == RULER:
                        self.plot.model.legend.openMeasurementPanel()

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
                                v.Tooltip(bottom=True, v_slots=[{
                                    'name': 'activator',
                                    'variable': 'tooltip',
                                    'children': v.Btn(v_on='tooltip.on', children=[
                                        v.Icon(
                                            children=['mdi-magnify-plus-cursor'])
                                    ])
                                }], children=[CLICK_ZOOM_IN]),
                                v.Tooltip(bottom=True, v_slots=[{
                                    'name': 'activator',
                                    'variable': 'tooltip',
                                                'children': v.Btn(v_on='tooltip.on', children=[
                                                    v.Icon(
                                                        children=['mdi-magnify-minus-cursor'])
                                                ])
                                }], children=[CLICK_ZOOM_OUT]),
                                v.Tooltip(bottom=True, v_slots=[{
                                    'name': 'activator',
                                    'variable': 'tooltip',
                                    'children': v.Btn(v_on='tooltip.on', children=[
                                        v.Icon(children=['mdi-ruler'])
                                    ])
                                }], children=[RULER])      # ruler
                            ])
            self.interaction_tooltips.observe(change_interact, "v_model")

            def reset(*args):
                (x1, x2), (y1, y2) = self.start_limits
                self.zoom_sel(x1, x2, y1, y2, smart_zoom=True)
                with self.zoom_brush.hold_trait_notifications():
                    self.zoom_brush.selected_x = None
                    self.zoom_brush.selected_y = None
                    self.zoom_brush.selected = None
                
            self.screenshot_btn = v.Btn(v_on='tooltip.on', icon=True, children=[
                                    v.Icon(children=['mdi-camera'])
                                ])
            self.screenshot_tooltip = v.Tooltip(bottom=True, v_slots=[{
                                    'name': 'activator',
                                    'variable': 'tooltip',
                                    'children': self.screenshot_btn
                                }], children=[SCREENSHOT])
            @debounced(0.5)
            def screenshot():
                def peer(a):
                    print(type(a).__name__)
                    print(type(a).__module__)
                    print(dir(a))
                    
                #display(self.pil_image_test)
                # print(self.core_image.value)
                #peer(self.figure)
                #self.figure.save_png("test.png")
                #display(IPyImage("test.png"))
                #display(self.core.image)
                clear_output(wait=True)
                self.plot.model.plot.show()
                display(IPyImage(self.core_image.value))
                
            self.screenshot_btn.on_event('click', lambda *ignore: screenshot())
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
                self.curr_action = args[0]
                (x1, x2), (y1, y2) = args[1][-1]
                with self.scale_x.hold_trait_notifications():
                    with self.scale_y.hold_trait_notifications():
                        self.scale_x.min, self.scale_x.max = x1, x2
                        self.scale_y.min, self.scale_y.max = y1, y2
            self.undo_btn.on_event('click', lambda *ignore: undo_redo(Action.undo, self.undo_actions))
            self.redo_btn.on_event('click', lambda *ignore: undo_redo(Action.redo, self.redo_actions))



            control_lyt = widgets.Layout(width='100px')
            self.control_x = widgets.Checkbox(value=False,description='Lock X Axis',indent=False, layout=control_lyt)
            self.control_y = widgets.Checkbox(value=False,description='Lock Y Axis',indent=False, layout=control_lyt)
            def axis_lock_update(checkbox):
                ####### Only allows one checkbox to be locked at a time ######
                if checkbox['owner'].description == self.control_x.description:
                    if self.control_y.value:
                        self.control_y.value = False

                if checkbox['owner'].description == self.control_y.description:
                    if self.control_x.value:
                        self.control_x.value = False
                ##############################################################
                # When a axis checkbox is locked.
                # Updates the panzoom tool to lock eithier the x or y axis.
                # Also updates the zoombrush tool to use relevant zoom brush
                if self.control_x.value:
                    if self.control_y.value:
                        self.panzoom = bqplot.PanZoom()
                        self.zoom_brush = self.zoom_brush_none
                    else:
                        self.panzoom = bqplot.PanZoom(scales={'y': [self.scale_y]})
                        self.zoom_brush = self.zoom_brush_vertical
                else:
                    if self.control_y.value:
                        self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x]})
                        self.zoom_brush = self.zoom_brush_horizontal
                    else:
                        self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})
                        self.zoom_brush = self.zoom_brush_full

                tool_actions_map[PAN_ZOOM] = self.panzoom
                tool_actions_map[ZOOM_SELECT] = self.zoom_brush

                # Update immediately if in PAN_ZOOM mode
                name = self.tool_actions[self.interaction_tooltips.v_model]
                if name == PAN_ZOOM:
                    self.figure.interaction = self.panzoom
                elif name == ZOOM_SELECT:
                    self.figure.interaction = self.zoom_brush
                

            self.control_x.observe(axis_lock_update)
            self.control_y.observe(axis_lock_update)
            self.axis_controls = widgets.VBox([self.control_x,self.control_y])

            self.tooltips = v.Row(children=[
                    self.axis_controls, 
                    self.interaction_tooltips, 
                    self.reset_tooltip,
                    self.undo_tooltip,
                    self.redo_tooltip,
                    self.screenshot_tooltip
                ], align='center', justify='center')
            self.plot.add_to_toolbar(self.tooltips)

    def get_df_selection(self, x1, x2, y1, y2):
        ind = self.plot.x_col
        addr = self.plot.y_col
        df = self.dataset
        return df[(df[ind] >= x1) & (df[ind] <= x2) & (df[addr] >= y1) & (df[addr] <= y2)]

    def update_zoom_brush_full(self, *args):
        with self.output:
            if not self.zoom_brush.brushing: # Update on mouse up
                self.figure.interaction = None
            if self.zoom_brush.selected is not None:
                (x1, y1), (x2, y2) = self.zoom_brush.selected
                if not self.zoom_brush.brushing: # Update on mouse up
                    self.figure.interaction = self.zoom_brush
                with self.zoom_brush.hold_trait_notifications(): # Delete selection
                    self.zoom_brush.selected_x = None
                    self.zoom_brush.selected_y = None

                self.zoom_sel(x1, x2, y1, y2, smart_zoom=True, padding=True)

    def update_zoom_brush_horizontal(self, *args):
        with self.output:
            if not self.zoom_brush.brushing: # Update on mouse up
                self.figure.interaction = None
            if self.zoom_brush.selected is not None:
                (x1, x2) = self.zoom_brush.selected
                if not self.zoom_brush.brushing: # Update on mouse up
                    self.figure.interaction = self.zoom_brush
                with self.zoom_brush.hold_trait_notifications(): # Delete selection
                    self.zoom_brush.selected = None

                self.zoom_sel(x1, x2, None, None, smart_zoom=False, padding=False)

    def update_zoom_brush_vertical(self, *args):
        with self.output:
            if not self.zoom_brush.brushing: # Update on mouse up
                self.figure.interaction = None
            if self.zoom_brush.selected is not None:
                (y1, y2) = self.zoom_brush.selected
                if not self.zoom_brush.brushing: # Update on mouse up
                    self.figure.interaction = self.zoom_brush
                with self.zoom_brush.hold_trait_notifications(): # Delete selection
                    self.zoom_brush.selected = None
                self.zoom_sel(None, None, y1, y2, smart_zoom=False, padding=False)

    def measure_selected_area(self, *args):
        with self.output:
            if not self.ruler.brushing: # Update on mouse up
                pass
            if self.ruler.selected is not None:
                (x1, y1), (x2, y2) = self.ruler.selected
                if not self.ruler.brushing: # Update on mouse up
                    self.figure.interaction = self.ruler
                with self.ruler.hold_trait_notifications(): # Delete selection
                    self.ruler.selected_x = None
                    self.ruler.selected_y = None
                df = self.get_df_selection(x1, x2, y1, y2)

                uniqueCacheLines = {l >> int(np.log2(self.plot.model.curr_trace.cache_block)) for l in df.unique('Address')}
                self.plot.model.legend.mearsurement.update(y2-y1, len(uniqueCacheLines), df.count(), df)
                

    def update_zoom_brush_none(self, *args):
        with self.zoom_brush.hold_trait_notifications(): # Delete selection
            self.zoom_brush.selected = None

    def zoom_sel(self, x1, x2, y1, y2, smart_zoom=False, padding=False):
        #################### handle locked x or y axis ########################
        # dont zoom if both axes are locked
        if self.control_x.value == True and self.control_y.value == True:
            return
        # if either x axis or y axis is locked, set the coresponding x12 or y12 coords to
        # the current axis size so it doesn't zoom 
        if self.control_x.value == True:
            smart_zoom = False
            padding = False
            x1 = self.scale_x.min
            x2 = self.scale_x.max
        if self.control_y.value == True:
            smart_zoom = False
            padding = False
            y1 = self.scale_y.min
            y2 = self.scale_y.max
        #######################################################################    

        df = self.get_df_selection(x1, x2, y1, y2)

        if df.count() != 0:
            selection = self.plot.model.legend.get_select_string()
            if selection != "":
                df = df[df[selection]]

        if df.count() == 0:
            self.stuck_ctr+=1
            with self.output:
                self.output.clear_output()
                print(f"{WARNING_LABEL} {TextStyle.YELLOW}No accesses in selection{'!'*self.stuck_ctr}{TextStyle.END}")
            return

        if smart_zoom: # For reset and zoom to selection
            ind = self.plot.x_col
            addr = self.plot.y_col
            x1 = df[ind].values[0]
            x2 = df[ind].values[-1]+1 # To fix resets on single values + to match original limits
            y1 = df[addr].min()[()]
            y2 = df[addr].max()[()]+1


        if padding: # Fix for plot getting stuck at one value axis
            if (x2 - x1 < 128):
                x1 -= (128 + x1 - x2) / 2
                x2 = x1 + 128

            if (y2 - y1 < 128):
                y1 -= (128 + y1 - y2) / 2
                y2 = y1 + 128
            
            # Add a 5% padding so points are not directly on edge
            padding_x = (x2 - x1) * 0.05
            padding_y = (y2 - y1) * 0.05

            x1 = x1 - padding_x
            x2 = x2 + padding_x
            y1 = y1 - padding_y
            y2 = y2 + padding_y

        with self.scale_x.hold_trait_notifications():
            self.scale_x.min, self.scale_x.max = float(x1), float(x2)
        with self.scale_y.hold_trait_notifications():
            self.scale_y.min, self.scale_y.max = float(y1), float(y2)

    def click_to_zoom(self, _, target):
        '''
            click to zoom call back 
            target contains mouse coordinates
        '''
        # check whether we want to zoom in or out
        tool_name = self.tool_actions[self.interaction_tooltips.v_model]
        if tool_name == CLICK_ZOOM_IN:
            scale = CLICK_ZOOM_SCALE
            use_smart_zoom = True
            use_padding = True
        elif tool_name == CLICK_ZOOM_OUT:
            scale = CLICK_ZOOM_SCALE * 100
            use_smart_zoom = False
            use_padding = False
        else:
            print('Invalid Tool Selected')
            return


        # get the mouse coordinates
        x = target['data']['click_x']
        y = target['data']['click_y']

        # difference smallest and largest value on each axis
        x_diff = abs(self.scale_x.max - self.scale_x.min)
        y_diff = abs(self.scale_y.max - self.scale_y.min)
        # multiply diff by CLICK_ZOOM_SCALE for 10x zoom, and by 0.5 since we want to
        # create a box around the x y mouse coord.
        x1 = x - (0.5 * scale * x_diff)
        x2 = x + (0.5 * scale * x_diff)
        y1 = y - (0.5 * scale * y_diff)
        y2 = y + (0.5 * scale * y_diff)

        self.zoom_sel(float(x1), float(x2), float(y1), float(y2),
                      smart_zoom=use_smart_zoom, padding=use_padding)            

    def zoom_args_string(self):
        to_int = [tuple( map(int,i) ) for i in self.limits]
        return f'zoom_access={to_int[0]}, zoom_address={to_int[1]}'
