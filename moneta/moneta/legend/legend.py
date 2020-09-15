from ipywidgets import Button, Checkbox, ColorPicker, HBox, Label, Layout, VBox, Accordion
import ipyvuetify as v
from vaex.jupyter.utils import debounced
from matplotlib.colors import to_hex, to_rgba, ListedColormap
from moneta.settings import newc, COMP_W_MISS, COMP_R_MISS, WRITE_MISS, READ_MISS, WRITE_HIT, READ_HIT, LEGEND_MEM_ACCESS_TITLE, LEGEND_TAGS_TITLE, LEGEND_CLICK_ZOOM
from moneta.legend.accesses import Accesses
from moneta.legend.tags import Tags
from moneta.legend.click_zoom import Click_Zoom
from enum import Enum
import numpy as np
from vaex.jupyter.bqplot import *

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
        self.widgets = VBox([self.panels, panel_style], layout=Layout(padding='0px', border='1px solid black', width='400px'))
        self.accesses = Accesses(model, self.update_selection)
        self.tags = Tags(model, self.update_selection)
        self.click_zoom = Click_Zoom(model)
        self.add_panel(LEGEND_MEM_ACCESS_TITLE, self.accesses.widgets)
        self.add_panel(LEGEND_TAGS_TITLE, self.tags.widgets)
        self.add_panel(LEGEND_CLICK_ZOOM, self.click_zoom.widgets)

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

    def get_select_array(self):
        self.df = self.model.curr_trace.df
        selected_bytes = self.df.evaluate(self.df.Bytes, selection=True)
        selected_access_number = self.df.evaluate(self.df.Access_Number, selection=True)
        selected_access = self.df.evaluate(self.df.Access, selection=True)
        selected_array = vaex.from_arrays(Bytes=selected_bytes, Access_Number=selected_access_number, Access=selected_access)
        #self.df.select('&'.join(selections), mode='replace') # replace not necessary for correctness, but maybe perf?
        return selected_array

    @debounced(0.5)
    def update_selection(self): 
        self.model.curr_trace.df.select(self.get_select_string(), mode='replace') # replace not necessary for correctness, but maybe perf?
        #selection = self.df[self.model.curr_trace.df[self.get_select_string()]]
        #self.click_zoom.click_zoom_obj.update_df_selections(self.get_select_array())
        #print(self.model.curr_trace.df['Access', 'Tag', 'Bytes', 'Access_Number'])
        self.df = self.model.curr_trace.df
        selected_bytes = self.df.evaluate(self.df.Bytes, selection=True)
        #tmp_df = self.df[['Access', 'Tag', 'Bytes', 'Access_Number'], selection=True]
        #self.df = self.df.extract()
        #print(tmp_df)

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
        self.click_zoom.set_plot(plot)

