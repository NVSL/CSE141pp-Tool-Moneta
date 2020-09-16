from ipywidgets import Button, Checkbox, ColorPicker, HBox, Label, Layout, VBox, Accordion
import ipyvuetify as v
from matplotlib.colors import to_hex, to_rgba, ListedColormap
from moneta.settings import newc, COMP_W_MISS, COMP_R_MISS, WRITE_MISS, READ_MISS, WRITE_HIT, READ_HIT, LEGEND_MEM_ACCESS_TITLE, LEGEND_TAGS_TITLE, INDEX_LABEL
from moneta.utils import stats_percent
from enum import Enum
import numpy as np

class SelectionGroup(Enum):
    hit_miss = 0
    read_write = 1
    data_structures = 2
    hit_miss_read = 3
    hit_miss_write = 4

class Legend():
    def __init__(self, model):
        self.model = model
        self.wid_150 = Layout(width='110px')
        self.wid_180 = Layout(width='125px')
        self.wid_15 = Layout(width='15px')
        self.wid_30 = Layout(width='30px')
        self.wid_270 = Layout(width='270px')
        self.mar_5 = Layout(width='5px')
        self.checkboxes = []
        self.colorpickers = {}
        self.colormap = np.copy(newc)

        self.widgets = VBox([], layout=Layout(padding='0px', border='1px solid black', width='300px'))
        self.add_accordion(LEGEND_MEM_ACCESS_TITLE, self.get_memoryaccesses())
        self.add_accordion(LEGEND_TAGS_TITLE, self.get_tags())


        self.ignore_changes = False
        def click():
            self.ignore_changes = True
            if self.control.status == True:
                self.collapse_all()
                self.control.children[0].children=['keyboard_arrow_down']
            else:
                self.expand_all()
                self.control.children[0].children=['keyboard_arrow_up']
            self.ignore_changes = False
        
            self.control.status = not self.control.status

        self.control = v.Btn(v_on='tooltip.on', icon=True, children=[
                                    v.Icon(children=['keyboard_arrow_up'])
                                ])
        self.control.status = True
        self.control.on_event('click', lambda *ignore: click())
        self.control_tooltip = v.Tooltip(bottom=True, v_slots=[{
                                'name': 'activator',
                                'variable': 'tooltip',
                                'children': self.control
                            }], children=['Legend'])

    def collapse_all(self):
        for accordion in self.widgets.children:
            accordion.selected_index = None
    def expand_all(self):
        for accordion in self.widgets.children:
            accordion.selected_index = 0


    def add_accordion(self, name, contents):
        accordion = Accordion([contents])
        accordion.set_title(0, name)
        self.widgets.children = tuple(list(self.widgets.children) + [accordion])
        accordion.observe(lambda *ignore: check_accordion_status())

        def check_accordion_status():
            if self.ignore_changes:
                return

            all_open = True
            all_closed = True

            for acc in self.widgets.children:
                if acc.selected_index == None:
                    all_open = False
                else:
                    all_closed = False

            if all_open:
                self.control.status = True
                self.control.children[0].children=['keyboard_arrow_up']
            elif all_closed:
                self.control.status = False
                self.control.children[0].children=['keyboard_arrow_down']


    def hit_miss_row(self, desc, primary_clr, sec_clr, group, read_selection, write_selection):
        read = self.create_checkbox('', self.wid_15, SelectionGroup.hit_miss_read, [read_selection])
        write = self.create_checkbox('', self.wid_15, SelectionGroup.hit_miss_write, [write_selection])
        both = self.create_parent_checkbox(desc, self.wid_150, group, [read_selection, write_selection], [read, write])
        return HBox([
            both,
            read,
            self.create_colorpicker(primary_clr),
            write,
            self.create_colorpicker(sec_clr)
        ], layout=Layout(overflow_x = 'hidden'))

    def cache_row(self, desc, clr):
        return HBox([
            Label(value=desc, layout=self.wid_180),
            self.create_colorpicker(clr)
        ])

    def all_rw_row(self, checkboxes):
        both = self.create_parent_checkbox('All', self.wid_150, SelectionGroup.hit_miss, [COMP_W_MISS, COMP_R_MISS, WRITE_MISS, READ_MISS, WRITE_HIT, READ_HIT],
                [checkbox.widget for checkbox in checkboxes if checkbox.group == SelectionGroup.hit_miss_read or checkbox.group == SelectionGroup.hit_miss_write])
        read =  self.create_parent_checkbox('', self.wid_15, SelectionGroup.read_write, [READ_HIT, READ_MISS, COMP_R_MISS],
                [checkbox.widget for checkbox in checkboxes if checkbox.group == SelectionGroup.hit_miss_read])
        write = self.create_parent_checkbox('', self.wid_15, SelectionGroup.read_write, [WRITE_HIT, WRITE_MISS, COMP_W_MISS],
                [checkbox.widget for checkbox in checkboxes if checkbox.group == SelectionGroup.hit_miss_write])
        return HBox([
            both,
            read,
            Label(value='R', layout=self.wid_30),
            write,
            Label(value='W', layout=self.wid_30)
        ])

    def get_memoryaccesses(self):
        hits_row = self.hit_miss_row("Hits", 1, 2, SelectionGroup.hit_miss, READ_HIT, WRITE_HIT)
        cap_misses_row = self.hit_miss_row("Cap Misses", 4, 5, SelectionGroup.hit_miss, READ_MISS, WRITE_MISS)
        comp_misses_row = self.hit_miss_row("Comp Misses", 6, 8, SelectionGroup.hit_miss, COMP_R_MISS, COMP_W_MISS)
        all_rw_row = self.all_rw_row(self.checkboxes) # All required checkboxes must already be in self.checkboxes
        memoryaccesses = VBox([
            all_rw_row,
            hits_row,
            cap_misses_row,
            comp_misses_row,
            self.cache_row("Cache", 3),
            self.create_reset_btn()],layout=Layout(padding='10px', overflow_x = 'auto'))
        return memoryaccesses

    def get_tags(self):
        tag_rows = [HBox([
            self.create_checkbox(tag.name, self.wid_150, SelectionGroup.data_structures, -1, ext=[tag.access[0], tag.access[1]]),
            self.create_button(tag)],
            layout=Layout(height='28px', overflow_y = 'hidden'))
        for tag in self.model.curr_trace.tags]
        
        all_ds_row = HBox([
            self.create_parent_checkbox('All', self.wid_150, 
                SelectionGroup.data_structures, 7+1,
                [checkbox.widget for checkbox in self.checkboxes if checkbox.group == SelectionGroup.data_structures]),
            ], layout=Layout(height='28px'))

        accordion = VBox(
            [all_ds_row] + tag_rows,
            layout=Layout(max_height='210px', overflow_y='auto', padding='10px'))
        return accordion

    def create_colorpicker(self, clr):
        clr_picker = ColorPicker(concise=True, value=to_hex(self.colormap[clr][0:3]), disabled=False, layout=self.wid_30)
        clr_picker.observing = True
        def handle_color_picker(change):
            if clr_picker.observing:
                self.colormap[clr] = to_rgba(change.new, 1)
                self.plot.colormap = ListedColormap(self.colormap)
                self.plot.backend.plot._update_image()
        clr_picker.observe(handle_color_picker,names='value')
        self.colorpickers[clr] = clr_picker
        return clr_picker

    def create_reset_btn(self):
        btn = Button(
                icon='refresh',
                tooltip="Reset all colors to default",
                tyle={'button_color': 'transparent'},
                layout=Layout(height='35px', width='50px',
                    borders='none', align_items='center'
                    )
                )
        def refresh_colormap(change):
            self.colormap = np.copy(newc)
            for clr, clr_picker in self.colorpickers.items():
                clr_picker.observing = False
                clr_picker.value=to_hex(self.colormap[clr][0:3])
                clr_picker.observing = True
            self.plot.colormap = ListedColormap(self.colormap)
            self.plot.backend.plot._update_image()
        btn.on_click(refresh_colormap)
        return btn

    def create_button(self, tag):
        df = self.model.curr_trace.df
        stats = df[int(tag.access[0]):int(tag.access[1])+1].count(binby=[df.Access], limits=[1,7], shape=[6])
        btn = Button(
                icon='search-plus',
                tooltip=self.tag_tooltip(tag) + '\n' + self.stats_to_str(stats),
                style={'button_color': 'transparent'},
                layout=Layout(height='35px', width='35px',
                                borders='none', align_items='center'
                             )
                )
        def zoom_to_selection(_):
            self.zoom_sel_handler(float(tag.access[0]), float(tag.access[1]),
                                    float(tag.address[0]), float(tag.address[1]))
        btn.on_click(zoom_to_selection)
        return btn

    def set_zoom_sel_handler(self, f):
        self.zoom_sel_handler = f

    def set_plot(self, plot):
        self.plot = plot

    def tag_tooltip(self, tag):
        access_range = f'Access Range: {tag.access[0]}, {tag.access[1]} \n'
        address_range = f'Address Range: {tag.address[0]}, {tag.address[1]} \n'

        return access_range + address_range


    def stats_to_str(self, stats):
        total = sum(stats)
        total_string = f'Total: {total}\n\n'
        read_hits = f'Read Hits: {stats[0]} ({stats_percent(stats[0],total)}) \n'
        write_hits = f'Write Hits: {stats[1]} ({stats_percent(stats[1],total)}) \n'
        cap_read_misses = f'Capacity Read Misses: {stats[2]} ({stats_percent(stats[2],total)}) \n'
        cap_write_misses = f'Capacity Write Misses: {stats[3]} ({stats_percent(stats[3],total)}) \n'
        comp_read_misses = f'Compulsory Read Hits: {stats[4]} ({stats_percent(stats[4],total)}) \n'
        comp_write_misses = f'Compulsort Write Hits: {stats[5]} ({stats_percent(stats[5],total)}) \n'
       


        return total_string + read_hits + write_hits + cap_read_misses + cap_write_misses + comp_read_misses + comp_write_misses

    def create_checkbox(self, desc, layout, group, selections, ext=[]):
        self.checkboxes.append(CheckBox(desc, layout, group, selections, self.handle_checkbox_change, ext=ext))
        return self.checkboxes[-1].widget

    def create_parent_checkbox(self, desc, layout, group, selections, child_checkboxes):
        def handle_parent_checkbox_change(_):
            if _.name == 'value':
                if parent_checkbox.widget.manual_change == False:
                    for checkbox in child_checkboxes:
                        checkbox.value = _.new
                parent_checkbox.widget.manual_change = False
        parent_checkbox = CheckBox(desc, layout, group, selections, handle_parent_checkbox_change)
        def handle_child_checkbox_change(_):
            if parent_checkbox.widget.value == True:
                if _.new == False:
                    parent_checkbox.widget.manual_change = True
                    parent_checkbox.widget.value = False
            if parent_checkbox.widget.value == False:
                if all([checkbox.value for checkbox in child_checkboxes]):
                    parent_checkbox.widget.manual_change = True
                    parent_checkbox.widget.value = True
        for checkbox in child_checkboxes:
            checkbox.observe(handle_child_checkbox_change, names='value')
        return parent_checkbox.widget

    def handle_checkbox_change(self, _): # TODO - move constants out
        selections = set()
        for checkbox in self.checkboxes:
            if checkbox.group == SelectionGroup.data_structures:
                if checkbox.widget.value == False:
                    selections.add('((%s < %s) | (%s > %s))' % ('Access_Number', checkbox.ext[0], 'Access_Number', checkbox.ext[1]))
            else:
                for selection in checkbox.selections:
                    if checkbox.widget.value == False:
                        selections.add('(Access != %d)' % (selection))
        self.model.curr_trace.df.select('&'.join(selections), mode='replace') # replace not necessary for correctness, but maybe perf?

class CheckBox():
    def __init__(self, desc, layout, group, selections, handle_fun, ext=[]):
        self.widget = Checkbox(description=desc, layout=layout,
                                value=True, disabled=False, indent=False)
        self.widget.observe(handle_fun, names='value')
        self.widget.manual_change = False
        self.group = group
        self.selections = selections
        self.ext = ext
