from ipywidgets import VBox, HBox, Layout, Label, ColorPicker, GridBox
import ipyvuetify as v
from matplotlib.colors import to_hex, to_rgba, ListedColormap
from moneta.settings import (
        vdiv, lvdiv, hdiv, lhdiv,
        READ_HIT, WRITE_HIT, READ_MISS,
        WRITE_MISS, COMP_R_MISS, COMP_W_MISS,
        newc
)
import numpy as np

class Accesses():
    def __init__(self, model, update_selection):
        self.model = model
        self.update_selection = update_selection
        self.colormap = np.copy(newc)
        self.colorpickers = {}
        self.widgets = self.init_widgets()

    def init_widgets(self):
        # Primary checkboxes
        read_hit = ChildCheckbox(self.compute_all, READ_HIT, 1)
        write_hit = ChildCheckbox(self.compute_all, WRITE_HIT, 2)
        read_capmiss = ChildCheckbox(self.compute_all, READ_MISS, 4)
        write_capmiss = ChildCheckbox(self.compute_all, WRITE_MISS, 5)
        read_compmiss = ChildCheckbox(self.compute_all, COMP_R_MISS, 6)
        write_compmiss = ChildCheckbox(self.compute_all, COMP_W_MISS, 8)
        chks = [read_hit, write_hit, read_capmiss,
                write_capmiss, read_compmiss, write_compmiss]
        self.checkboxes = chks


        # Parent checkboxes
        self.all_check = ParentCheckbox(chks, self.compute_all, label = 'All', tooltip="Show All")
        self.read_check = ParentCheckbox([read_hit, read_capmiss, read_compmiss], self.compute_all, 
                                         label='Reads', tooltip="Reads")
        self.write_check = ParentCheckbox([write_hit, write_capmiss, write_compmiss], self.compute_all, 
                                          label='Writes', tooltip="Writes")
        self.hit_check = ParentCheckbox([read_hit, write_hit], self.compute_all, 
                                          label='Hits', tooltip="Hits")
        self.capmiss_check = ParentCheckbox([read_capmiss, write_capmiss], self.compute_all, 
                                             label='Capacity Misses', tooltip="Capacity Misses")
        self.compmiss_check = ParentCheckbox([read_compmiss, write_compmiss], self.compute_all, 
                                              label='Compuls Misses', tooltip="Compulsory Misses")
        self.parentcheckboxes = [self.all_check, self.read_check, self.write_check, 
                self.hit_check, self.capmiss_check, self.compmiss_check]

        def parentbox(check):
            return HBox([check.widget], layout=Layout(align_items="center", overflow="hidden", justify_content="center"))

        def clr_picker(clr, cache=False):
            if cache:
                clr_picker = ColorPicker(concise=True, value=to_hex(self.colormap[clr][0:3]), 
                        disabled=False, layout=Layout(width="30px"))
            else:
                clr_picker = ColorPicker(concise=True, value=to_hex(self.colormap[clr][0:3]), 
                        disabled=False, layout=Layout(width="25px", margin="0 0 0 8px"))
            clr_picker.observing = True
            def handle_color_picker(change):
                self.colormap[clr] = to_rgba(change.new, 1)
                self.model.plot.colormap = ListedColormap(self.colormap)
                self.model.plot.backend.plot._update_image()
            clr_picker.observe(handle_color_picker, names='value')
            self.colorpickers[clr] = clr_picker
            return clr_picker

        def primbox(check):
            return HBox([check.widget, clr_picker(check.clr)],
                layout=Layout(justify_content="center",align_items="center",overflow="hidden"))

        # Wrap parent boxes in ipywidget
        alls = parentbox(self.all_check)

        read = parentbox(self.read_check)
        write = parentbox(self.write_check)

        hits = parentbox(self.hit_check)
        capmisses = parentbox(self.capmiss_check)
        compmisses = parentbox(self.compmiss_check)

        # Add pseudo grid and wrap primary boxes in ipywidget
        gridbox = HBox([GridBox([alls, vdiv, read, vdiv, write,
                                 hdiv, hdiv, hdiv, hdiv, hdiv,
                                 hits, vdiv, primbox(read_hit), lvdiv, primbox(write_hit),
                                 hdiv, hdiv, lhdiv, lhdiv, lhdiv,
                                 capmisses, vdiv, primbox(read_capmiss), lvdiv, primbox(write_capmiss),
                                 hdiv, hdiv, lhdiv, lhdiv, lhdiv,
                                 compmisses, vdiv, primbox(read_compmiss), lvdiv, primbox(write_compmiss)],
                                layout=Layout(grid_template_rows="50px 2px 50px 2px 50px 2px 50px", grid_template_columns="100px 5px 100px 5px 100px"))], layout=Layout(padding="0 0 0 14px"))

        cache_icon = v.Icon(children=['fa-database'], v_on='tooltip.on')
        cache_icon_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': cache_icon}], children=["Cache"])

        cache_clrpkr = clr_picker(3, cache=True)

        reset_clrs = v.Btn(v_on='tooltip.on', icon=True, children=[v.Icon(children=['refresh'])])
        reset_clrs.on_event('click', self.reset_colormap)
        reset_clrs_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': reset_clrs}], children=["Reset all colors"])
        cache_row = HBox([cache_icon_tp, cache_clrpkr, reset_clrs_tp],
                        layout=Layout(padding="0 20px 20px 20px", align_items="center", justify_content="space-between"))
        cache_row
        return VBox([gridbox, cache_row])

    def compute_all(self, *_):
        for parent in self.parentcheckboxes:
            parent.update()
        self.update_selection()

    def reset_colormap(self, *_):
        self.colormap = np.copy(newc)
        for clr, clr_picker in self.colorpickers.items():
            clr_picker.observing = False
            clr_picker.value = to_hex(self.colormap[clr][0:3])
            clr_picker.observing = True
        self.model.plot.colormap = ListedColormap(self.colormap)
        self.model.plot.backend.plot._update_image()

class ParentCheckbox:
    def __init__(self, children, compute_all, label="", append_icon=None, prepend_icon=None, tooltip=""):
        # _widget for v_model, widget for display
        if append_icon:  
            self._widget = v.Checkbox(
                v_on='tooltip.on', append_icon=append_icon, v_model=True)
        elif prepend_icon:
            self._widget = v.Checkbox(
                v_on='tooltip.on', prepend_icon=prepend_icon, v_model=True)
        else:
            self._widget = v.Checkbox(
                v_on='tooltip.on', label=label, v_model=True)

        self.widget = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': self._widget}],
                children=[tooltip])
        self._widget.on_event('change', self.handler)
        self.children = children
        self.compute_all = compute_all

    def handler(self, checkbox, _, new):
        self._widget.indeterminate = False
        for child in self.children:
            child.widget.v_model = new
        self.compute_all()

    def update(self):
        on = 0
        off = 0
        for child in self.children:
            if child.widget.v_model:
                on+=1
            else:
                off+=1
        self._widget.v_model = on == len(self.children)
        self._widget.indeterminate = on > 0 and off > 0

class ChildCheckbox:
    def __init__(self, handler, acc_type, clr):
        self.widget = v.Checkbox(ripple=False, v_model=True, color='primary')
        self.widget.on_event('change', handler)
        self.acc_type=acc_type
        self.clr = clr
