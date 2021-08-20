from ipywidgets import VBox, HBox, Layout, Label, ColorPicker, GridBox, Dropdown
import ipyvuetify as v
from matplotlib.colors import to_hex, to_rgba, ListedColormap
from moneta.settings import (
        vdiv, lvdiv, Whdiv, hdiv, lhdiv,
        READ_HIT, WRITE_HIT, READ_MISS,
        WRITE_MISS, COMP_R_MISS, COMP_W_MISS,
        newc, READS_CLR, WRITES_CLR, HIT_CLR,
        MISS_CAP_CLR, MISS_COM_CLR, TOP_COM_MISS,
        TOP_CAP_MISS, TOP_HIT, TOP_WRITE, TOP_READ,
        COLOR_VIEW, C_VIEW_OPTIONS
)
import numpy as np
import os

class Accesses():
    def __init__(self, model, update_selection):
        self.model = model
        self.update_selection = update_selection
        self.colormap = np.copy(newc)
        self.colorpickers = {}
        self._CURR_C_VIEW = os.environ.get('COLOR_VIEW') # get the color setting from enviroment
        self.widgets = self.init_widgets()

    def init_widgets(self):
        #######################################################################
        '''
            Helper functions to help with wrapping widgets in layouts and initializing UI
            elements
        '''
        def clr_picker(clr, cache=False, top_level_color=False):
            '''

            '''
            def handle_color_picker(change):
                self.colormap[clr] = to_rgba(change.new, 1)
                self.model.plot.colormap = ListedColormap(self.colormap)
                self.model.plot.backend.plot.update_image()
            
            def handle_color_picker_multiple(change):
                for acceses_type in clr[4:]:
                    self.colormap[acceses_type] = to_rgba(change.new, 1)
                self.model.plot.colormap = ListedColormap(self.colormap)
                self.model.plot.backend.plot.update_image()
            
            if top_level_color:
                clr_picker = ColorPicker(concise=True, value=to_hex(clr[0:3]), 
                        disabled=False, layout=Layout(width="25px", margin="0 0 0 4px"))
      
                clr_picker.observe(handle_color_picker_multiple, names='value')
                self.colorpickers[top_level_color] = clr_picker
            else:
                if cache:
                    clr_picker = ColorPicker(concise=True, value=to_hex(self.colormap[clr][0:3]), 
                            disabled=False, layout=Layout(width="30px"))
                else:
                    clr_picker = ColorPicker(concise=True, value=to_hex(self.colormap[clr][0:3]), 
                            disabled=False, layout=Layout(width="25px", margin="0 0 0 4px"))
               
                clr_picker.observe(handle_color_picker, names='value')
                self.colorpickers[clr] = clr_picker

            clr_picker.observing = True
            return clr_picker

        def init_dropdown(clr, cache=False, top_level_color=False):
            dropdown_widget = Dropdown(options=C_VIEW_OPTIONS,
                    value=self._CURR_C_VIEW,
                    disabled=False,
                    layout={'width': 'min-content'}
                    )
            # dropdown_widget.observe(handle_color_picker, names='value')
            # self.colorpickers[clr] = dropdown_widget
            # dropdown_widget.observing = True
            return dropdown_widget

        def parentbox(check, has_clrpicker, clr=None, top_level_color=False):
            if has_clrpicker:
                return HBox([check.widget , init_dropdown(clr, top_level_color=top_level_color)], 
                            layout=Layout(align_items="center", overflow="hidden", justify_content="flex-start"))
            else:
                return HBox([check.widget], 
                            layout=Layout(align_items="center", overflow="hidden", justify_content="center"))

        def childbox(check):
            return HBox([check.widget, init_dropdown(check.clr)],
                        layout=Layout(justify_content="center",align_items="center",overflow="hidden"))
        #######################################################################
        # drop down menue for color view selection
        dropdown = Dropdown(options=C_VIEW_OPTIONS,
                            value=self._CURR_C_VIEW,
                            disabled=False,
                            layout={'width': 'min-content'}
                            )
        dropdown.observe(self.update_colormenue, names='value')
        
        dropdown_row = HBox([GridBox([Label(value='Selected Color View:'), dropdown],
                            layout=Layout(grid_template_rows="30px", grid_template_columns="120px 200px"))], 
                            layout=Layout( padding="0px 0px 14px 100px"))
        
        #######################################################################
        
        # Primary checkboxes
       
        # if CURR_C_VIEW == C_VIEW_OPTIONS[0]: 
        read_hit = ChildCheckbox(self.compute_all, READ_HIT, 1)
        write_hit = ChildCheckbox(self.compute_all, WRITE_HIT, 2)

        read_miss = ChildCheckbox(self.compute_all, READ_MISS, 4)
        write_miss = ChildCheckbox(self.compute_all, WRITE_MISS, 5)
       
        # read_capmiss = ChildCheckbox(self.compute_all, READ_MISS, 4)
        # write_capmiss = ChildCheckbox(self.compute_all, WRITE_MISS, 5)
        # read_compmiss = ChildCheckbox(self.compute_all, COMP_R_MISS, 6)
        # write_compmiss = ChildCheckbox(self.compute_all, COMP_W_MISS, 8)

        self.childcheckboxes = [read_hit, write_hit, read_miss, write_miss]

        # Parent checkbox container which hold child checkboxes
        # Only init neccessary color contol options based on CURR_C_VIEW
        
        self.all_check = ParentCheckbox([read_hit, write_hit, read_miss, write_miss], self.compute_all, 
                                        label = 'All', tooltip="Show All", is_all_chk=True)
        self.read_check = ParentCheckbox([read_hit, read_miss], self.compute_hit_miss_group, 
                                        label='Reads', tooltip="Reads", clr=TOP_READ, clr_val=READS_CLR)
        self.write_check = ParentCheckbox([write_hit, write_miss], self.compute_hit_miss_group, 
                                        label='Writes', tooltip="Writes", clr=TOP_WRITE, clr_val=WRITES_CLR)
        self.hit_check = ParentCheckbox([read_hit, write_hit], self.compute_read_write_group, 
                                        label='Hits', tooltip="Hits", clr=TOP_HIT, clr_val=HIT_CLR)
        self.miss_check = ParentCheckbox([read_miss, write_miss], self.compute_read_write_group, 
                                    label='Miss', tooltip="Misses", clr=TOP_CAP_MISS, clr_val=MISS_CAP_CLR)



        # self.capmiss_check = ParentCheckbox([read_capmiss, write_capmiss], self.compute_read_write_group, 
        #                                     label='Cap Miss', tooltip="Capacity Misses", clr=TOP_CAP_MISS, clr_val=MISS_CAP_CLR)
        # self.compmiss_check = ParentCheckbox([read_compmiss, write_compmiss], self.compute_read_write_group, 
        #                                     label='Com Miss', tooltip="Compulsory Misses", clr=TOP_COM_MISS, clr_val=MISS_COM_CLR)
        # top level checkbox groups
        # self.parentcheckboxes = [self.all_check, self.read_check, self.write_check, 
        #         self.hit_check, self.capmiss_check, self.compmiss_check]
        # self.read_write_group = [self.all_check, self.read_check, self.write_check]
        # self.hit_miss_group = [self.all_check, self.hit_check, self.capmiss_check, self.compmiss_check]


        # Wrap parent boxes in ipywidget
        alls = parentbox(self.all_check, has_clrpicker=False)
        read = parentbox(self.read_check, has_clrpicker=True, clr=READS_CLR, top_level_color=TOP_READ)
        write = parentbox(self.write_check, has_clrpicker=True, clr=WRITES_CLR, top_level_color=TOP_WRITE)
        hits = parentbox(self.hit_check, has_clrpicker=True, clr=HIT_CLR, top_level_color=TOP_HIT)
        # capmisses = parentbox(self.capmiss_check, has_clrpicker=True, clr=MISS_CAP_CLR, top_level_color=TOP_CAP_MISS)
        # compmisses = parentbox(self.compmiss_check,has_clrpicker=True, clr=MISS_COM_CLR, top_level_color=TOP_COM_MISS)
        misses = parentbox(self.miss_check,has_clrpicker=True, clr=MISS_COM_CLR, top_level_color=TOP_COM_MISS)

     
     
        if self._CURR_C_VIEW == C_VIEW_OPTIONS[0]:
            grid_elements = [read, vdiv, write, 
                             Whdiv, hdiv, Whdiv,
                             misses, vdiv, hits
                            ]
            row_template = "50px 2px 50px 2px 50px"
            column_template = "180px 2px 180px"

        elif self._CURR_C_VIEW == C_VIEW_OPTIONS[1]:
            grid_elements = [read, vdiv, write]
            row_template = "70px"
            column_template = "180px 2px 180px"

        elif self._CURR_C_VIEW == C_VIEW_OPTIONS[2]:
            grid_elements = [hits, vdiv, misses]
            row_template = "70px"
            column_template = "180px 2px 180px"

        elif self._CURR_C_VIEW == C_VIEW_OPTIONS[3]:
            grid_elements = [Label(value="Access Colors are by TAGs")]
            row_template = "30px"
            column_template = "300px"
        elif self._CURR_C_VIEW == C_VIEW_OPTIONS[4]:
            grid_elements = [Label(value="Access Colors are by THREADs")]
            row_template = "30px"
            column_template = "300px"




        # Add pseudo grid and wrap primary boxes in ipywidget
        gridbox = HBox([GridBox(grid_elements,
                                layout=Layout(grid_template_rows=row_template, grid_template_columns=column_template))], 
                                layout=Layout( padding="0 0 0 14px"))

        cache_icon = v.Icon(children=['fa-database'], v_on='tooltip.on')
        cache_icon_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': cache_icon}], children=["Cache"])

        cache_clrpkr = clr_picker(3, cache=True)

        reset_clrs = v.Btn(v_on='tooltip.on', icon=True, children=[v.Icon(children=['refresh'])])
        reset_clrs.on_event('click', self.reset_colormap)
        reset_clrs_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': reset_clrs}], children=["Reset all colors"])
        cache_row = HBox([cache_icon_tp, cache_clrpkr, reset_clrs_tp],
                        layout=Layout(padding="0 20px 20px 20px", align_items="center", justify_content="space-between"))
        return VBox([dropdown_row, gridbox, cache_row])


    def update_colormenue(self, new):
        print(new)


    def compute_colors(self, parent):
        '''
            Call this function to force update of colors based of state of checkboxes.

            parent: the top level ParentCheckbox that has recently changed state
        '''
        for acceses_type in parent.clr_val[4:]:
            self.colormap[acceses_type] = to_rgba(self.colorpickers[parent.clr].value, 1)
        
        for child in self.childcheckboxes:
            if child.widget.v_model == True and child.widget.disabled == False:
                self.colormap[child.clr] = to_rgba(self.colorpickers[child.clr].value, 1)
        
        self.model.plot.colormap = ListedColormap(self.colormap)
        self.model.plot.backend.plot._update_image()


    def compute_all(self, *kwargs):
        '''
            Update the graph with new acceses selections, triggered by checkbox event handler. 
            update_selection implemented in Legend.py.
        '''
        self.all_check.update()
        self.update_selection()

    def compute_read_write_group(self, self_parentbox=None):
        state = self.hit_check._widget.v_model or self.capmiss_check._widget.v_model or self.compmiss_check._widget.v_model
        for parent in self.read_write_group:
            parent.update(disabled=state)
            # disable colorpickers of children
            for child in parent.children:
                self.colorpickers[child.clr].disabled = state

            # disable top level group color picker as well
            if not parent.is_all_chk:
                self.colorpickers[parent.clr].disabled = state

        self.update_selection()
        self.compute_colors(self_parentbox)

    def compute_hit_miss_group(self, self_parentbox=None):
        state = self.read_check._widget.v_model or self.write_check._widget.v_model
        for parent in self.hit_miss_group:
            parent.update(disabled=state)
            # disable colorpickers of children
            for child in parent.children:
                self.colorpickers[child.clr].disabled = state

            # disable top level group color picker as well to_hex([29/255, 135/255, 23/255, 1])
            if not parent.is_all_chk:
                self.colorpickers[parent.clr].disabled = state
                
        self.update_selection()
        self.compute_colors(self_parentbox)

    def reset_colormap(self, *_):
        self.colormap = np.copy(newc)
        for clr, clr_picker in self.colorpickers.items():
            if clr < TOP_READ:
                clr_picker.observing = False
                clr_picker.value = to_hex(self.colormap[clr][0:3])
                clr_picker.observing = True
        self.model.plot.colormap = ListedColormap(self.colormap)
        self.model.plot.backend.plot._update_image()

class ParentCheckbox:
    def __init__(self, children, compute_all, label="", append_icon=None, prepend_icon=None, tooltip="", is_all_chk=False, clr=None, clr_val=None):
        # _widget for v_model, widget for display
        if append_icon:  
            self._widget = v.Checkbox(
                v_on='tooltip.on', append_icon=append_icon, v_model=False, color='primary')
        elif prepend_icon:
            self._widget = v.Checkbox(
                v_on='tooltip.on', prepend_icon=prepend_icon, v_model=False, color='primary')
        elif is_all_chk:
            self._widget = v.Checkbox(
                v_on='tooltip.on', label=label, v_model=True , color='primary')
        else:
            self._widget = v.Checkbox(
                v_on='tooltip.on', label=label, v_model=False , color='primary')

        self.widget = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': self._widget}],
                children=[tooltip])
        self._widget.on_event('change', self.handler)
        self.children = children
        self.compute_all = compute_all
        self.is_all_chk = is_all_chk
        self.clr = clr
        self.clr_val = clr_val

    def handler(self, checkbox, _, new):
        ''' 
            Syncs all the children of this parent checkbox to the state of the parent.
            Example: If the parent checkbox is checked all children are also checked.

            checkbox: the parent checkbox
            new [True, False]: the new changed state 
        '''
        
        self._widget.indeterminate = False # disable intermediate icon, since the state has been user updated

        if self.is_all_chk:
            child_val = not new
            child_indt = False
            child_disabled = False
        else:
            child_val = new
            child_indt = new 
            child_disabled = new

        for child in self.children:
            if self.is_all_chk:
                child.widget.v_model = not child_val
            
            child.widget.indeterminate = child_indt
            child.widget.disabled = child_disabled

        self.compute_all(self) # update selection

    def update(self, disabled=None):
        '''


        '''
        if disabled is not None:
            self._widget.disabled = disabled

        if self.is_all_chk:
            on = 0
            off = 0
            for child in self.children:
                if child.widget.v_model:
                    on+=1
                else:
                    off+=1
            self._widget.v_model = on == len(self.children)


class ChildCheckbox:
    def __init__(self, handler, acc_type, clr):
        self.widget = v.Checkbox(ripple=True, v_model=True, color='primary')
        self.widget.on_event('change', handler)
        self.acc_type=acc_type
        self.clr = clr
