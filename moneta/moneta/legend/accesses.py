from ipywidgets import VBox, HBox, Layout, Label, ColorPicker, GridBox, Dropdown, Button
import ipyvuetify as v
from matplotlib.colors import to_hex, to_rgba, ListedColormap
# from moneta.settings import (
#         vdiv, lvdiv, Whdiv, hdiv, lhdiv,
#         READ_HIT, WRITE_HIT, READ_MISS,
#         WRITE_MISS, COMP_R_MISS, COMP_W_MISS,
#         newc, THREAD_ID,
#         COLOR_VIEW, C_VIEW_OPTIONS
# )
from moneta.settings import *
import numpy as np
import os
from vaex.jupyter.utils import debounced
from moneta.trace import ThreadTag, SpaceTimeTag


class Accesses():
    def __init__(self, model, update_selection):
        self.model = model
        self.update_selection = update_selection
        self.colormap = np.copy(newc)
        self.colorpickers = {}
        self._CURR_C_VIEW = os.environ.get('COLOR_VIEW') # get the color setting from enviroment
        
        self.all_tags =  self.model.curr_trace.tags # includes spacetime and thread
        self.layer_options = [
            ('None', [0]), ('RHit', [READ_HIT]),  ('WHit', [WRITE_HIT]),  ('RMissCapacity', [READ_MISS]),
            ('RMissCompulsory', [COMP_R_MISS]), ('WMissCapacity', [WRITE_MISS]), ('WMissCompulsory', [COMP_W_MISS])
         ]

        i_val = 9
        for tag in self.all_tags:
           i_layer = (tag.display_name(), tag)
           i_val += 1
           self.layer_options.append(i_layer)

        self.widgets = self.init_widgets()

    def init_widgets(self):
        #######################################################################
        '''
            Helper functions to help with wrapping widgets in layouts and initializing UI
            elements
        '''
        def clr_picker(enum_color, cache=False, miss_acc=False):
            '''

            '''
            def handle_color_picker(change):
                print(enum_color, change)
                self.colormap[enum_color] = to_rgba(change.new, 1)
                self.model.plot.colormap = ListedColormap(self.colormap)
                self.model.plot.backend.plot.update_image()
            
            def handle_color_picker_multiple(change):
                print(enum_color)
                for acceses_type in enum_color:
                    print(acceses_type)
                    self.colormap[acceses_type] = to_rgba(change.new, 1)
                self.model.plot.colormap = ListedColormap(self.colormap)
                self.model.plot.backend.plot.update_image()
            
            if miss_acc:
                clr_picker = ColorPicker(concise=True, value=to_hex(self.colormap[3][0:3]), 
                        disabled=False, layout=Layout(width="25px", margin="0 4px 0 4px"))
      
                clr_picker.observe(handle_color_picker_multiple, names='value')
                
            else:
                if cache:
                    clr_picker = ColorPicker(concise=True, value=to_hex(self.colormap[enum_color][0:3]), 
                            disabled=False, layout=Layout(width="30px"))
                else:
                    clr_picker = ColorPicker(concise=True, value=to_hex(self.colormap[enum_color][0:3]), 
                            disabled=False, layout=Layout(width="25px", margin="0 4px 0 4px"))
               
                clr_picker.observe(handle_color_picker, names='value')
                self.colorpickers[enum_color] = clr_picker

            clr_picker.observing = True
            return clr_picker



        def ParentBox(parent_widgets, miss_acc=False):
            return HBox([clr_picker(enum_color=parent_widgets.enum_color, miss_acc=miss_acc), parent_widgets.check_widget , parent_widgets.dropdown_widget], 
                        layout=Layout(align_items="center", overflow="hidden", justify_content="flex-start"))


        #######################################################################
        # drop down menue for color view selection
        self.dropdown = Dropdown(options=C_VIEW_OPTIONS,
                            value=self._CURR_C_VIEW,
                            disabled=False,
                            layout={'width': 'min-content'}
                            )
        self.dropdown.observe(self.update_presets, names='value')
        self.dropdown.observing = True
        dropdown_row = HBox([GridBox([Label(value='Layer Preset:'), self.dropdown],
                            layout=Layout(grid_template_rows="30px", grid_template_columns="120px 200px"))], 
                            layout=Layout( padding="0px 0px 14px 100px"))
        
        #######################################################################

        # Primary layers
        self.layer1_widgets = ParentWidgets(label='1', tooltip="Layer1", enum_color=9, clr=6.1, 
                                            init_layer_val=[0], layer_options=self.layer_options, compute=self.compute_layers)
        self.layer2_widgets = ParentWidgets(label='2', tooltip="Layer2", enum_color=8, clr=5.5, 
                                            init_layer_val=[0], layer_options=self.layer_options, compute=self.compute_layers)
        self.layer3_widgets = ParentWidgets(label='3', tooltip="Layer3", enum_color=7, clr=5.1,
                                            init_layer_val=[0], layer_options=self.layer_options, compute=self.compute_layers)
        self.layer4_widgets = ParentWidgets(label='4', tooltip="Layer4", enum_color=6, clr=4.4, 
                                            init_layer_val=[0], layer_options=self.layer_options, compute=self.compute_layers)
        self.layer5_widgets = ParentWidgets(label='5', tooltip="Layer5", enum_color=5, clr=3.5, 
                                            init_layer_val=[0], layer_options=self.layer_options, compute=self.compute_layers)
        self.layer6_widgets = ParentWidgets(label='6', tooltip="Layer6", enum_color=4, clr=3.1, 
                                            init_layer_val=[0], layer_options=self.layer_options, compute=self.compute_layers)
        self.layer7_widgets = ParentWidgets(label='7', tooltip="Layer7", enum_color=3, clr=2.4, 
                                            init_layer_val=[0], layer_options=self.layer_options, compute=self.compute_layers)
        self.layer8_widgets = ParentWidgets(label='8', tooltip="Layer8", enum_color=2, clr=1.4, 
                                            init_layer_val=[0], layer_options=self.layer_options, compute=self.compute_layers)
    

        self.layers = [self.layer1_widgets, self.layer2_widgets, self.layer3_widgets, self.layer4_widgets,
                       self.layer5_widgets, self.layer6_widgets, self.layer7_widgets, self.layer8_widgets]

        
        # Wrap parent widgets in a layout with a color picker
        layer1 = ParentBox(self.layer1_widgets)
        layer2 = ParentBox(self.layer2_widgets)
        layer3 = ParentBox(self.layer3_widgets)
        layer4 = ParentBox(self.layer4_widgets)
        layer5 = ParentBox(self.layer5_widgets)
        layer6 = ParentBox(self.layer6_widgets)
        layer7 = ParentBox(self.layer7_widgets)
        layer8 = ParentBox(self.layer8_widgets)



        grid_elements = [layer1, vdiv, layer2, 
                            Whdiv, hdiv, Whdiv,
                            layer3, vdiv, layer4,
                            Whdiv, hdiv, Whdiv,
                            layer5, vdiv, layer6,
                            Whdiv, hdiv, Whdiv,
                            layer7, vdiv, layer8,
                            Whdiv, hdiv, Whdiv,
                        ]
        row_template = "50px 2px 50px 2px 50px 2px 50px 2px 50px 2px"
        column_template = "180px 2px 180px"


        # Add pseudo grid and wrap primary boxes in ipywidget
        gridbox = HBox([GridBox(grid_elements,
                                layout=Layout(grid_template_rows=row_template, grid_template_columns=column_template))], 
                                layout=Layout( padding="0 0 0 14px"))

        # cache_icon = v.Icon(children=['fa-database'], v_on='tooltip.on')
        # cache_icon_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': cache_icon}], children=["Cache"])

        # cache_clrpkr = clr_picker(3, cache=True)

        # reset_clrs = v.Btn(v_on='tooltip.on', icon=True, children=[v.Icon(children=['refresh'])])
        # reset_clrs.on_event('click', self.reset_colormap)
        # reset_clrs_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': reset_clrs}], children=["Reset all colors"])
        # cache_row = HBox([cache_icon_tp, cache_clrpkr, reset_clrs_tp],
        #                 layout=Layout(padding="0 20px 20px 20px", align_items="center", justify_content="space-between"))  ## , cache_row
        return VBox([dropdown_row, gridbox])

    # @debounced(0.2)
    def compute_layers(self, change):
        
        # reset the layer value of old selections
        # tags threads and accesses use seperate queries
        if type(change['old']) is SpaceTimeTag :
            addr_low = float(change['old'].address[0])
            addr_high = float(change['old'].address[1]) + 1
            indx_low = float(change['old'].access[0])
            indx_high = float(change['old'].access[1]) + 1

            # !See Explantion Below
            self.model.curr_trace.df.Temp1 = self.model.curr_trace.df.func.where(
                (addr_low <= self.model.curr_trace.df.Address), 1.0 , 2.0)

            self.model.curr_trace.df.Temp2 = self.model.curr_trace.df.func.where(
                (addr_high >= self.model.curr_trace.df.Address), 1.0 , 3.0)

            self.model.curr_trace.df.TempA = self.model.curr_trace.df.func.where(
                (self.model.curr_trace.df.Temp1 == self.model.curr_trace.df.Temp2), 1.0 , 6.0)

            self.model.curr_trace.df.Temp3 = self.model.curr_trace.df.func.where(
                ( indx_low <= self.model.curr_trace.df.index ), 1.0 , 4.0)
            self.model.curr_trace.df.Temp4 = self.model.curr_trace.df.func.where(
                ( indx_high >= self.model.curr_trace.df.index ), 1.0, 5.0)
            self.model.curr_trace.df.TempB = self.model.curr_trace.df.func.where(
                (self.model.curr_trace.df.Temp3 == self.model.curr_trace.df.Temp4), 1.0 , 7.0)
            
            self.model.curr_trace.df[LAYER] = self.model.curr_trace.df.func.where(
                (self.model.curr_trace.df.TempA == self.model.curr_trace.df.TempB), 
                0.4 , self.model.curr_trace.df.Layer)
           

        elif type(change['old']) is ThreadTag:
            t_id = change['old'].thread_id
            self.model.curr_trace.df[LAYER] = self.model.curr_trace.df.func.where(self.model.curr_trace.df.ThreadID == t_id, 1, self.model.curr_trace.df.Layer)
        else:
            for atype in change['old']:
                self.model.curr_trace.df[LAYER] = self.model.curr_trace.df.func.where(self.model.curr_trace.df.Access == atype, 1 , self.model.curr_trace.df.Layer)
        

        for layer in reversed(self.layers):
            # check if the layer checkbox is enabled first
            if layer.check.v_model == True:
                # do not update none layers and layer.dropdown_widget.value == change['new'] 
                if layer.dropdown_widget.value != [0] :
                    # tags threads and accesses use seperate queries
                    if type(layer.dropdown_widget.value) is SpaceTimeTag :
                        addr_low = float(layer.dropdown_widget.value.address[0])
                        addr_high = float(layer.dropdown_widget.value.address[1]) + 1
                        indx_low = float(layer.dropdown_widget.value.access[0])
                        indx_high = float(layer.dropdown_widget.value.access[1]) + 1

                        # df.func.where has a bug where it can only evaluate single boolean value expressions
                        #   EX. self.model.curr_trace.df.Address >= addr_low and self.model.curr_trace.df.Address <= addr_high
                        #   results in only the first comparison being evaluated.
                        # Thus we must seperate the upper and lower bound calculations, this is not efficient but has minimal
                        # impact on perfomance.
                       
                        # create temp layer to find which accesses belong to tag.
                        self.model.curr_trace.df.Temp1 = self.model.curr_trace.df.func.where(
                            (addr_low <= self.model.curr_trace.df.Address), 1.0 , 2.0)

                        self.model.curr_trace.df.Temp2 = self.model.curr_trace.df.func.where(
                            (addr_high >= self.model.curr_trace.df.Address), 1.0 , 3.0)

                        self.model.curr_trace.df.TempA = self.model.curr_trace.df.func.where(
                            (self.model.curr_trace.df.Temp1 == self.model.curr_trace.df.Temp2), 1.0 , 6.0)

                        self.model.curr_trace.df.Temp3 = self.model.curr_trace.df.func.where(
                            ( indx_low <= self.model.curr_trace.df.index ), 1.0 , 4.0)
                        self.model.curr_trace.df.Temp4 = self.model.curr_trace.df.func.where(
                            ( indx_high >= self.model.curr_trace.df.index ), 1.0, 5.0)
                        self.model.curr_trace.df.TempB = self.model.curr_trace.df.func.where(
                            (self.model.curr_trace.df.Temp3 == self.model.curr_trace.df.Temp4), 1.0 , 7.0)
                        
                        self.model.curr_trace.df[LAYER] = self.model.curr_trace.df.func.where(
                            self.model.curr_trace.df.TempA == self.model.curr_trace.df.TempB, 
                            layer.clr , self.model.curr_trace.df.Layer)

                    elif type(layer.dropdown_widget.value) is ThreadTag:
                        t_id = layer.dropdown_widget.value.thread_id
                        self.model.curr_trace.df[LAYER] = self.model.curr_trace.df.func.where(
                            self.model.curr_trace.df.ThreadID == t_id, layer.clr , self.model.curr_trace.df.Layer)
                    else:
                        for atype in layer.dropdown_widget.value:
                            self.model.curr_trace.df[LAYER] = self.model.curr_trace.df.func.where(
                                self.model.curr_trace.df.Access == atype, layer.clr , self.model.curr_trace.df.Layer)
                    
            else:
                for atype in layer.dropdown_widget.value:
                    self.model.curr_trace.df[LAYER] = self.model.curr_trace.df.func.where(
                        self.model.curr_trace.df.Access == atype, 1, self.model.curr_trace.df.Layer)

        self.model.plot.colormap = ListedColormap(self.colormap)
        self.model.plot.backend.plot.update_grid()

    def update_presets(self, change):
        new_preset = change.new
        if new_preset == 'None':
            for layer in self.layers:
                layer.update_selection([0])
        elif new_preset == 'AccessType':
            self.layers[0].update_selection([COMP_W_MISS])
            self.layers[1].update_selection([WRITE_MISS])
            self.layers[2].update_selection([COMP_R_MISS])
            self.layers[3].update_selection([COMP_R_MISS])
            self.layers[4].update_selection([WRITE_HIT])
            self.layers[5].update_selection([READ_HIT])
     
        elif new_preset == 'TAG':
            layer_index = 0
            for layer_option in reversed(self.layer_options):
                if type(layer_option[1]) is SpaceTimeTag and layer_index < len(self.layers):
                    if layer_option[0] != 'Stack' and layer_option[0] != 'Heap':
                        self.layers[layer_index].update_selection(layer_option[1])
                        layer_index += 1
        elif new_preset == 'THREAD':
            layer_index = 0
            for layer_option in reversed(self.layer_options):
                if type(layer_option[1]) is ThreadTag and layer_index < len(self.layers):
                    self.layers[layer_index].update_selection(layer_option[1])
                    layer_index += 1
        elif new_preset == 'Custom':
            for (index, layer_option) in enumerate(self.custom_layer_preset):
                for option in self.layer_options:
                    if option[0] == layer_option:
                        self.layers[index].update_selection(option[1])

    def set_custom_presets(self, layer_preset):
        self.custom_layer_preset = layer_preset
        self.dropdown.value = 'Custom'


    def reset_colormap(self, *_):
        self.colormap = np.copy(newc)
        for clr, clr_picker in self.colorpickers.items():
            if clr < TOP_READ:
                clr_picker.observing = False
                clr_picker.value = to_hex(self.colormap[enum_color][0:3])
                clr_picker.observing = True
        self.model.plot.colormap = ListedColormap(self.colormap)
        self.model.plot.backend.plot._update_image()

class ParentWidgets:
    def __init__(self, label, tooltip, enum_color, clr, init_layer_val, layer_options, compute):

        self.check = v.Checkbox(v_on='tooltip.on', label=label, v_model=True , color='primary')
        self.check_widget = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': self.check}],
                children=[tooltip])
       
        self.compute = compute
        self.enum_color = enum_color
        self.init_layer_val = init_layer_val
        self.layer_options = layer_options
        self.dropdown_widget = Dropdown(options=self.layer_options ,
                                        value=init_layer_val,
                                        disabled=False,
                                        layout={'width': '90px'}
                                        )
        self.dropdown_widget.observe(self.compute, names='value')
        self.dropdown_widget.observing = True
        self.clr = clr


    def update_selection(self, new_preset):
        self.dropdown_widget.observing = False
        self.dropdown_widget.value = new_preset
        self.dropdown_widget.observing = True