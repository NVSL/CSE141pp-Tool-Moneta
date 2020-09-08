from ipywidgets import VBox, HBox, Layout, Label, ColorPicker, GridBox
import ipyvuetify as v
from moneta.settings import (
        vdiv, lvdiv, hdiv, lhdiv,
        READ_HIT, WRITE_HIT, READ_MISS,
        WRITE_MISS, COMP_R_MISS, COMP_W_MISS
)
class Accesses():
    def __init__(self, model, update_selection):
        self.model = model
        self.update_selection = update_selection
        self.widgets = self.init_widgets()

    def init_widgets(self):
        read_hit = ChildCheckbox(self.compute_all, READ_HIT)
        write_hit = ChildCheckbox(self.compute_all, WRITE_HIT)
        read_capmiss = ChildCheckbox(self.compute_all, READ_MISS)
        write_capmiss = ChildCheckbox(self.compute_all, WRITE_MISS)
        read_compmiss = ChildCheckbox(self.compute_all, COMP_R_MISS)
        write_compmiss = ChildCheckbox(self.compute_all, COMP_W_MISS)
        chks = [read_hit, write_hit, read_capmiss,
                write_capmiss, read_compmiss, write_compmiss]
        self.checkboxes = chks


        self.all_check = ParentCheckbox(chks, self.compute_all, prepend_icon='fa-globe', tooltip="All")
        self.read_check = ParentCheckbox([read_hit, read_capmiss, read_compmiss], self.compute_all, label="R")
        self.write_check = ParentCheckbox([write_hit, write_capmiss, write_compmiss], self.compute_all, label="W")

        self.hit_check = ParentCheckbox([read_hit, write_hit], self.compute_all, prepend_icon="fa-dot-circle-o", tooltip="Hits")
        self.capmiss_check = ParentCheckbox([read_capmiss, write_capmiss], self.compute_all, prepend_icon="fa-battery", tooltip="Capacity Misses")
        self.compmiss_check = ParentCheckbox([read_compmiss, write_compmiss], self.compute_all, prepend_icon="fa-legal", tooltip="Compulsory Misses")
        self.parentcheckboxes = [self.all_check, self.read_check, self.write_check, 
                self.hit_check, self.capmiss_check, self.compmiss_check]

        def colbox(check):
            return HBox([check.widget], layout=Layout(align_items="center", overflow="hidden"))

        def primbox(check):
            return HBox([check.widget, ColorPicker(concise=True,disabled=False,
                            value="red",layout=Layout(width="30px",margin="0 0 0 -3px", padding="-5"))],
                layout=Layout(justify_content="center",align_items="center",overflow="hidden"))

        alls = colbox(self.all_check)

        read = HBox([self.read_check.widget], layout=Layout(margin="0 0 0 6px", align_items="center", overflow="hidden"))
        write = HBox([self.write_check.widget], layout=Layout(margin="0 0 0 6px", align_items="center", overflow="hidden"))

        hits = colbox(self.hit_check)
        capmisses = colbox(self.capmiss_check)
        compmisses = colbox(self.compmiss_check)

        gridbox = HBox([GridBox([alls, vdiv, read, vdiv, write,
            hdiv, hdiv, hdiv, hdiv, hdiv,
            hits, vdiv, primbox(read_hit), lvdiv, primbox(write_hit),
            hdiv, hdiv, lhdiv, lhdiv, lhdiv,
            capmisses, vdiv, primbox(read_capmiss), lvdiv, primbox(write_capmiss),
            hdiv, hdiv, lhdiv, lhdiv, lhdiv,
            compmisses, vdiv, primbox(read_compmiss), lvdiv, primbox(write_compmiss)],
            layout=Layout(grid_template_rows="50px 2px 50px 2px 50px 2px 50px", grid_template_columns="70px 5px 70px 5px 70px"))], layout=Layout(padding="0 0 0 14px"))

        cache_icon = v.Icon(children=['fa-database'], v_on='tooltip.on')
        cache_icon_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': cache_icon}], children=["Cache"])

        cache_clrpkr = ColorPicker(concise=True, disabled=False, value="red", layout=Layout(width="30px"))

        reset_clrs = v.Btn(v_on='tooltip.on', icon=True, children=[v.Icon(children=['refresh'])])
        reset_clrs_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': reset_clrs}], children=["Reset all colors"])
        cache_row = HBox([cache_icon_tp, cache_clrpkr, reset_clrs_tp],
                        layout=Layout(padding="0 20px 20px 20px", align_items="center", justify_content="space-between"))
        cache_row
        return VBox([gridbox, cache_row])

    def compute_all(self, *_):
        for parent in self.parentcheckboxes:
            parent.update()
        self.update_selection()
        #self.handle_checkbox_change() # TODO

    def handle_checkbox_change(self): # TODO - move constants out
        selections = set()
        for checkbox in self.checkboxes:
            if checkbox.group == SelectionGroup.data_structures:
                if checkbox.widget.value == False:
                    selections.add('(Tag != %s)' % (checkbox.selections))
            else:
                for selection in checkbox.selections:
                    if checkbox.widget.value == False:
                        selections.add('(Access != %d)' % (selection))
        self.model.curr_trace.df.select('&'.join(selections), mode='replace') # replace not necessary for correctness, but maybe perf?


class ParentCheckbox:
    def __init__(self, children, compute_all, label=None, prepend_icon=None, tooltip=""):
        if label is None and prepend_icon is None:
            raise SystemError
        if label is None: # _widget for v_model, widget for display
            self._widget = v.Checkbox(v_on='tooltip.on', prepend_icon=prepend_icon, v_model=True)
            self.widget = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': self._widget}],
                children=[tooltip])
        else:
            self._widget = v.Checkbox(label=label, v_model=True)
            self.widget = self._widget
        self._widget.on_event('change', self.handler)
        self.children = children
        self.compute_all = compute_all

    def handler(self, checkbox, _, new):
        self.widget.indeterminate = False
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
    def __init__(self, handler, acc_type):
        self.widget = v.Checkbox(ripple=False, v_model=True, color='primary')
        self.widget.on_event('change', handler)
        self.acc_type=acc_type
