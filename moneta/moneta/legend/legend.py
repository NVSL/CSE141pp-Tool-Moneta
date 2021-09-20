from ipywidgets import Button, Checkbox, ColorPicker, HBox, Label, Layout, VBox, Accordion
import ipyvuetify as v
from vaex.jupyter.utils import debounced
from tqdm.notebook import tqdm
from matplotlib.colors import to_hex, to_rgba, ListedColormap
from moneta.settings import newc, COMP_W_MISS, COMP_R_MISS, WRITE_MISS, READ_MISS, WRITE_HIT, READ_HIT, LEGEND_MEM_ACCESS_TITLE, LEGEND_TAGS_TITLE,  LEGEND_STATS_TITLE, LEGEND_MEASUREMENT_TITLE, INDEX, ADDRESS, THREAD_ID, LEGEND_THREADS_TITLE
from moneta.legend.accesses import Accesses
from moneta.legend.tags import Tags
from moneta.trace import TAG_TYPE_SPACETIME, TAG_TYPE_THREAD
from moneta.legend.stats import PlotStats
from moneta.legend.measurement import PlotMeasure

from enum import Enum
import numpy as np
from vaex.jupyter.bqplot import *
import logging
log = logging.getLogger(__name__)

class Legend():
    def __init__(self, model):
        self.model = model

        self.panels = v.ExpansionPanels(accordion=True, multiple=True, v_model=[])
        up = 'keyboard_arrow_up'
        down = 'keyboard_arrow_down'
        legend_icon = v.Icon(children=[down])
        self.legend_button = v.Btn(icon=True, children=[legend_icon])
        # Style to remove gray background in panels, and remove padding in panel contents
        panel_style = v.Html(tag='style', children=[(
            ".v-application--wrap{background-color: white!important}"
            ".v-expansion-panel-content__wrap{padding:0!important}"
            ".v-input__slot .v-label{color: black!important}"
        )])

        def a(): self.widgets = VBox([self.panels, panel_style], layout=Layout(padding='0px', border='1px solid black', width='400px'))
        def b(): self.accesses = Accesses(model, self.update_selection)
        def c(): self.stats = PlotStats(model)
        def d(): self.tags = Tags(model, self.update_selection, tag_type=TAG_TYPE_SPACETIME)
        def e(): self.threads = Tags(model, self.update_selection, tag_type=TAG_TYPE_THREAD)
        def m(): self.mearsurement = PlotMeasure(model)
        def f(): self.add_panel(LEGEND_MEM_ACCESS_TITLE, self.accesses.widgets)
        def g(): self.add_panel(LEGEND_TAGS_TITLE, self.tags.widgets)
        def h(): self.add_panel(LEGEND_THREADS_TITLE, self.threads.widgets)
        #def i(): self.add_panel(LEGEND_STATS_TITLE, self.stats.widgets)
        def n(): self.add_panel(LEGEND_MEASUREMENT_TITLE, self.mearsurement.widgets)

        self.progress_bar([
            a,
            b,
            c,
            d,
            e,
            m,
            f,
            g,
            h,
            #i,
            n
            ])

        # give accesses nformation about tags and threads for layers



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

    def progress_bar(self, fns):
        for fn in tqdm(fns, leave=False):
            fn()

    def get_select_string(self): # TODO - move constants out
        selections = set()
        # for checkbox in self.accesses.childcheckboxes:
        #     if checkbox.widget.v_model == False:
        #         selections.add(f'(Access != {checkbox.acc_type})')

        for checkbox in self.tags.checkboxes + self.threads.checkboxes:
            if checkbox.widget.v_model == False:
                selections.add(f"(~({checkbox.tag.query_string()}))")
        q = '&'.join(selections)
        return q

    @debounced(0.5)
    def update_selection(self):
        self.model.curr_trace.df.select(self.get_select_string())

    def add_panel(self, name, contents):
        acc = v.ExpansionPanel(children=[
            v.ExpansionPanelHeader(children=[name]),
            v.ExpansionPanelContent(children=[contents], class_='ma-0 pa-0')
            ])
        self.panels.children = self.panels.children + [acc]

    def openMeasurementPanel(self):
        index = [panel.children[0].children[0] for panel in self.panels.children].index(LEGEND_MEASUREMENT_TITLE)
        if index not in self.panels.v_model:
            self.panels.v_model = self.panels.v_model + [index]
