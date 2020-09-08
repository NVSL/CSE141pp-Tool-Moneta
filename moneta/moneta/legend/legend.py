from ipywidgets import Button, Checkbox, ColorPicker, HBox, Label, Layout, VBox, Accordion
import ipyvuetify as v
from matplotlib.colors import to_hex, to_rgba, ListedColormap
from moneta.settings import newc, COMP_W_MISS, COMP_R_MISS, WRITE_MISS, READ_MISS, WRITE_HIT, READ_HIT, LEGEND_MEM_ACCESS_TITLE, LEGEND_TAGS_TITLE
from moneta.legend.accesses import Accesses
from moneta.legend.tags import Tags
from enum import Enum
import numpy as np

class Legend():
    def __init__(self, model):
        self.model = model

        self.panels = v.ExpansionPanels(accordion=True, multiple=True, v_model=[])
        up = 'keyboard_arrow_up'
        down = 'keyboard_arrow_down'
        legend_icon = v.Icon(children=[down])
        self.legend_button = v.Btn(icon=True, children=[legend_icon])
        # Style to remove gray background in panels, and remove padding in panel contents
        panel_style = v.Html(tag='style', children=[".v-application--wrap{background-color: white!important} .v-expansion-panel-content__wrap{padding:0!important}"])
        self.widgets = VBox([self.panels, panel_style], layout=Layout(padding='0px', border='1px solid black', width='300px'))
        self.accesses = Accesses(model, self.update_selection)
        self.tags = Tags(model, self.update_selection)
        self.add_panel(LEGEND_MEM_ACCESS_TITLE, self.accesses.widgets)
        self.add_panel(LEGEND_TAGS_TITLE, self.tags.widgets)

        def update_legend_icon(_panels, _, selected):
            if len(selected) == len(self.panels.children):
                legend_icon.children = [up]
            elif selected == []:
                legend_icon.children = [down]
        self.panels.on_event('change', update_legend_icon)

        def update_panels(*args):
            if legend_icon.children[0] == up:
                legend_icon.children = [down]
                self.panels.v_model = []
            else:
                legend_icon.children = [up]
                self.panels.v_model = list(range(len(self.panels.children)))
        self.legend_button.on_event('click', update_panels)

    def get_select_string(self): # TODO - move constants out
        selections = set()
        for checkbox in self.accesses.checkboxes:
            if checkbox.widget.v_model == False:
                selections.add('(Access != %d)' % (checkbox.acc_type))
        for checkbox in self.tags.checkboxes:
            if checkbox.widget.v_model == False:
                selections.add('(Tag != %s)' % (checkbox.tag_id))
        return '&'.join(selections)

    def update_selection(self):
        self.model.curr_trace.df.select(self.get_select_string(), mode='replace') # replace not necessary for correctness, but maybe perf?

    def add_panel(self, name, contents):
        acc = v.ExpansionPanel(children=[
            v.ExpansionPanelHeader(children=[name]),
            v.ExpansionPanelContent(children=[contents], class_='ma-0 pa-0')
            ])
        self.panels.children = self.panels.children + [acc]

    def set_zoom_sel_handler(self, f):
        self.tags.set_zoom_sel_handler(f)

    def set_plot(self, plot):
        self.accesses.set_plot(plot)

