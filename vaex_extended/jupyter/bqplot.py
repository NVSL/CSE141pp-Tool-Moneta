from vaex.jupyter.bqplot import *
from vaex_extended.utils.decorator import *
from vaex.jupyter.plot import PlotBase as PlotBase
import vaex_extended
import copy

# # alternate wrapper version in case the function should be left alone
# def fix_image_flipping(func):
#     from functools import wraps
#     @wraps(func)
#     def wrapper(self,rgb_image):
#         return func(self, np.flipud(rgb_image))
#     return wrapper
# BqplotBackend.update_image = fix_image_flipping(BqplotBackend.update_image)

accessRanges = {}

PAN_ZOOM = "pan/zoom"
ZOOM_SELECT = 'zoom select'
SELECT = "select"

@extend_class(BqplotBackend)
def __init__(self, figure=None, figure_key=None):
    self._dirty = False
    self.figure_key = figure_key
    self.figure = figure
    self.signal_limits = vaex.events.Signal()

    self._cleanups = []
    
    self.dataset_original = None
    #self.limit_callback = None
@extend_class(PlotBase)
def _update_image(self):
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


@extend_class(BqplotBackend)
@debounced(0.5, method=True)
def _update_limits(self, *args):
    with self.output:
        limits = copy.deepcopy(self.limits)
        limits[0:2] = [[scale.min, scale.max] for scale in [self.scale_x, self.scale_y]]
        self.limits = limits
        left = max(0, int(limits[0][0]))
        right = max(0, int(limits[0][1]))
        # print(left, right)
        #sliced = self.dataset[left:right]
        #print(len(sliced))
        

@extend_class(BqplotBackend)
def update_image(self, rgb_image):
    # corrects error where the image is flipped vertically
    rgb_image = np.flipud(rgb_image) 
    with self.output:
        rgb_image = (rgb_image * 255.).astype(np.uint8)
        pil_image = vaex.image.rgba_2_pil(rgb_image)
        data = vaex.image.pil_2_data(pil_image)
        self.core_image.value = data
        # force update
        self.image.image = self.core_image_fix
        self.image.image = self.core_image
        self.image.x = (self.scale_x.min, self.scale_x.max)
        self.image.y = (self.scale_y.min, self.scale_y.max)

@extend_class(BqplotBackend)
def create_tools(self):
    self.tools = []
    tool_actions = []
    self.tool_actions_map = tool_actions_map = dict()

    # self.control_widget.set_title(0, "Main")
    self._main_widget = widgets.VBox()
    self._main_widget_1 = widgets.HBox()
    self._main_widget_2 = widgets.HBox()
    if 1:  # tool_select:
        tool_actions_map[PAN_ZOOM] = self.panzoom
        tool_actions.append(PAN_ZOOM)
    
        self.zoom_brush = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="blue")
        tool_actions_map[ZOOM_SELECT] = self.zoom_brush
        tool_actions.append(ZOOM_SELECT)

        self.zoom_brush.observe(self.update_zoom_brush, ["brushing"])
        
        self.brush = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="green")
        tool_actions_map[SELECT] = self.brush
        tool_actions.append(SELECT)

        self.brush.observe(self.update_brush, ["selected", "selected_x"])
        # fig.interaction = brush
        # callback = self.dataset.signal_selection_changed.connect(lambda dataset: update_image())
        # callback = self.dataset.signal_selection_changed.connect(lambda *x: self.update_grid())

        # def cleanup(callback=callback):
        #    self.dataset.signal_selection_changed.disconnect(callback=callback)
        # self._cleanups.append(cleanup)

        self.button_select_nothing = v.Btn(icon=True, v_on='tooltip.on', children=[
                                    v.Icon(children=['delete'])
                                ])
        self.widget_select_nothing = v.Tooltip(bottom=True, v_slots=[{
            'name': 'activator',
            'variable': 'tooltip',
            'children': self.button_select_nothing
        }], children=[
            "Delete selection"
        ])
        self.button_reset = v.Btn(icon=True, v_on='tooltip.on', children=[
                                    v.Icon(children=['refresh'])
                                ])
        self.widget_reset = v.Tooltip(bottom=True, v_slots=[{
            'name': 'activator',
            'variable': 'tooltip',
            'children': self.button_reset
        }], children=[
            "Reset Zoom"
        ])
        
        self.start_limits = copy.deepcopy(self.limits)

        def reset(*args):
            (x1, x2), (y1, y2) = self.start_limits
            with self.scale_x.hold_trait_notifications():
                with self.scale_y.hold_trait_notifications():
                    self.scale_x.min, self.scale_x.max = x1, x2
                    self.scale_y.min, self.scale_y.max = y1, y2
            with self.zoom_brush.hold_trait_notifications():
                self.zoom_brush.selected_x = None
                self.zoom_brush.selected_y = None
            self._update_limits()

        self.button_select_nothing.on_event('click', lambda *ignore: self.plot.select_nothing())
        self.tools.append(self.button_select_nothing)
        
        self.button_reset.on_event('click', lambda *ignore: reset())
        self.tools.append(self.button_reset)
        
        self.modes_names = "replace and or xor subtract".split()
        self.modes_labels = "replace and or xor subtract".split()
        self.button_selection_mode = widgets.Dropdown(description='select', options=self.modes_labels)
        self.tools.append(self.button_selection_mode)

        def change_interact(*args):
            with self.output:
                # print "change", args
                name = tool_actions[self.button_action.v_model]
                self.figure.interaction = tool_actions_map[name]

        tool_actions = [PAN_ZOOM, ZOOM_SELECT, SELECT]
        # tool_actions = [("m", "m"), ("b", "b")]
        self.button_action = \
            v.BtnToggle(v_model=0, mandatory=True, multiple=False, children=[
                            v.Tooltip(bottom=True, v_slots=[{
                                'name': 'activator',
                                'variable': 'tooltip',
                                'children': v.Btn(v_on='tooltip.on', children=[
                                    v.Icon(children=['pan_tool'])
                                ])
                            }], children=[
                                "Pan & zoom"
                            ]),
                            v.Tooltip(bottom=True, v_slots=[{
                                'name': 'activator',
                                'variable': 'tooltip',
                                'children': v.Btn(v_on='tooltip.on', children=[
                                    v.Icon(children=['crop'])
                                ])
                            }], children=[
                                "Zoom to selection"
                            ]),
                           v.Tooltip(bottom=True, v_slots=[{
                                'name': 'activator',
                                'variable': 'tooltip',
                                'children': v.Btn(v_on='tooltip.on', children=[
                                    v.Icon(children=['crop_free'])
                                ])
                            }], children=[
                                "Square selection"
                            ])
                    ])
        self.widget_tool_basic = v.Layout(children=[
            v.Layout(pa_1=True, column=False, align_center=True, children=[
                self.button_action,
                self.widget_select_nothing,
                self.widget_reset
            ])
        ])
        self.plot.add_control_widget(self.widget_tool_basic)

        control_lyt = widgets.Layout(width='40px')
        self.panzoom_x = control_x = widgets.Checkbox(value=True,description='X',indent=False, layout=control_lyt)
        self.panzoom_y = control_y = widgets.Checkbox(value=True,description='Y',indent=False, layout=control_lyt)
        def update_panzoom(checkbox):
            if control_x.value == True:
                if control_y.value == True:
                    self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})
                else:
                    self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x]})
            else:
                if control_y.value:
                    self.panzoom = bqplot.PanZoom(scales={'y': [self.scale_y]})
                else:
                    self.panzoom = bqplot.PanZoom(scales={})
            # Update with new panzoom
            tool_actions_map[PAN_ZOOM] = self.panzoom
            # Update immediately if in PAN_ZOOM mode
            name = tool_actions[self.button_action.v_model]
            if name == PAN_ZOOM:
              self.figure.interaction = self.panzoom
            

        self.panzoom_x.observe(update_panzoom)
        self.panzoom_y.observe(update_panzoom)
        #self.plot.add_control_widget(self.panzoom_x)
        #self.plot.add_control_widget(self.panzoom_y)
        self.panzoom_controls_label = widgets.Label(value="Pan & zoom",layout=widgets.Layout(margin='0 10px 0 0'))
        self.panzoom_controls = widgets.VBox([self.panzoom_x,self.panzoom_y])
        pz_lyt = widgets.Layout(display='flex',flex_flow='row',width='70%')
        self.panzoom_controls_menu = widgets.HBox([self.panzoom_controls_label, self.panzoom_controls])
        self.plot.add_control_widget(self.panzoom_controls_menu)
       
        # Controls to be added to menubar instead of sidebar 
        self.widget_menubar = v.Layout(children=[
            v.Layout(pa_1=True, column=False, align_center=True, children=[
                widgets.VBox([self.panzoom_x, self.panzoom_y]),
                self.button_action,
                self.widget_select_nothing,
                self.widget_reset
            ])
        ])

        # Create list of buttons for tag zooming
        self.buttons = [widgets.Button(
                        description=name,
                        tooltip=name, 
                        icon='search-plus',
                        layout=widgets.Layout(margin='10px 0px 0px 0px', 
                                              height='40px', 
                                              width='90%', 
                                              border='1px solid black'))
                   for name in accessRanges.keys()]
        
        self.zoomButtonList = widgets.VBox(self.buttons, layout = widgets.Layout(align_items="center"))
    
        for button in self.buttons:
            button.on_click(self.zoomSection)        

        self.plot.add_control_widget(self.zoomButtonList)




        self.button_action.observe(change_interact, "v_model")
        self.tools.insert(0, self.button_action)
        self.button_action.value = "pan/zoom"  # tool_actions[-1]
        if len(self.tools) == 1:
            tools = []
        # self._main_widget_1.children += (self.button_reset,)
        self._main_widget_1.children += (self.button_action,)
        self._main_widget_1.children += (self.button_select_nothing,)
        self._main_widget_1.children += (self.button_reset,)
        # self._main_widget_2.children += (self.button_selection_mode,)
    self._main_widget.children = [self._main_widget_1, self._main_widget_2]
    self.control_widget.children += (self._main_widget,)
    self._update_grid_counter = 0  # keep track of t
    self._update_grid_counter_scheduled = 0  # keep track of t
    
@extend_class(BqplotBackend)
def update_zoom_brush(self, *args):
    # Only update on mouse-up
    if not self.zoom_brush.brushing:
        with self.output:
            self.figure.interaction = None
            if self.zoom_brush.selected is not None:
                (x1, y1), (x2, y2) = self.zoom_brush.selected
                mode = self.modes_names[self.modes_labels.index(self.button_selection_mode.value)]
                # Update limits
                with self.scale_x.hold_trait_notifications():
                    with self.scale_y.hold_trait_notifications():
                        self.scale_x.min, self.scale_x.max = x1, x2
                        self.scale_y.min, self.scale_y.max = y1, y2
                self._update_limits()      
            self.figure.interaction = self.zoom_brush
            # Delete selection
            with self.zoom_brush.hold_trait_notifications():
                self.zoom_brush.selected_x = None
                self.zoom_brush.selected_y = None


# From the addressRange dictionary, get the metadata corresponding to the button/tag name
# and modify the scale_x and scale_y of the graph based on the min and max of the axes ranges
@extend_class(BqplotBackend)
@debounced(0.5, method=True)
def zoomSection(self, change):

    rangeData = accessRanges[change.tooltip]    

    xmin = rangeData['startIndex']
    xmax = rangeData['endIndex']
    ymin = rangeData['startAddr']
    ymax = rangeData['endAddr']

    with self.scale_x.hold_trait_notifications():
        self.scale_x.min = xmin
        self.scale_x.max = xmax
    with self.scale_y.hold_trait_notifications():
        self.scale_y.min = ymin
        self.scale_y.max = ymax

