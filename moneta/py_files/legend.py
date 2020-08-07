from ipywidgets import Button, Checkbox, ColorPicker, HBox, Label, Layout, VBox
from matplotlib.colors import to_hex
from settings import newc, COMP_W_MISS, COMP_R_MISS, WRITE_MISS, READ_MISS, WRITE_HIT, READ_HIT
from enum import Enum

class SelectionGroup(Enum):
    hit_miss = 0
    read_write = 1
    data_structures = 2

class Legend():
    def __init__(self, tags, df):
        self.wid_150 = Layout(width='150px')
        self.wid_30 = Layout(width='30px')
        self.wid_270 = Layout(width='270px')
        self.checkboxes = []
        self.df = df
        first_row = HBox([
                Label(value='Legend', layout=self.wid_150), 
                Label(value='R', layout=self.wid_30), 
                Label(value='W', layout=self.wid_30)
            ])
        self.widgets = VBox([
                first_row,
                self.hit_miss_row("Hits", newc[1], newc[2], 
                    SelectionGroup.hit_miss, [READ_HIT, WRITE_HIT]),
                self.hit_miss_row("Cap Misses", newc[4], newc[5], 
                    SelectionGroup.hit_miss, [READ_MISS, WRITE_MISS]),
                self.hit_miss_row("Comp Misses", newc[6], newc[8], 
                    SelectionGroup.hit_miss, [COMP_R_MISS, COMP_W_MISS]),
                self.create_checkbox("Reads", self.wid_270, 
                    SelectionGroup.read_write, [READ_HIT, READ_MISS, COMP_R_MISS]),
                self.create_checkbox("Writes", self.wid_270, 
                    SelectionGroup.read_write, [WRITE_HIT, WRITE_MISS, COMP_W_MISS]),
                self.cache_row("Cache", newc[3]),
                Label(value="", layout=Layout(border='1px solid black', height='0px', margin='5px 0 0 0')),
                self.get_datastructures(tags)
            ], layout=Layout(padding='10px', border='1px solid black', width='210px'))

    def hit_miss_row(self, desc, primary_clr, sec_clr, group, selections):
        return HBox([
            self.create_checkbox(desc, self.wid_150, group, selections),
            ColorPicker(concise=True, value=to_hex(primary_clr[0:3]), disabled=False, layout=self.wid_30),
            ColorPicker(concise=True, value=to_hex(sec_clr[0:3]), disabled=False, layout=self.wid_30)
        ])

    def cache_row(self, desc, clr):
        return HBox([
            Label(value=desc, layout=self.wid_150),
            ColorPicker(concise=True, value=to_hex(clr[0:3]), disabled=False, layout=self.wid_30)
        ])

    def get_datastructures(self, tags):
        max_id = max(tags, key=lambda x: x.id_).id_
        stats = self.df.count(binby=[self.df.Tag, self.df.Access], limits=[[0,max_id+1], [1,7]], shape=[max_id+1,6])
        return VBox([Label(value='Data Structures')]+[
            HBox([
                self.create_checkbox(tag.name, self.wid_150, 
                    SelectionGroup.data_structures, tag.id_),
                self.create_button(tag, stats)
                ], layout=Layout(min_height='35px'))
            for tag in tags], layout=Layout(max_height='210px', overflow_y='auto'))

    def create_button(self, tag, stats):
        stats_str = self.stats_to_str(tag.id_, stats)
        btn = Button(
                icon='search-plus',
                tooltip=self.tag_tooltip(tag) + stats_str,
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

    def tag_tooltip(self, tag):
        return ("(" + tag.access[0] + ", " + tag.access[1] + "), " +
        "(" + tag.address[0] + ", " + tag.address[1] + ")")

    def stats_to_str(self, ind, stats):
        total = sum(stats[ind])
        if total == 0:
            return ','.join([repr(stat) for stat in stats[ind]])
        hits = stats[ind][0] + stats[ind][1]
        return ','.join([repr(stat) for stat in stats[ind]]) + ",\n" + repr(hits/total) + "," + repr((total-hits)/total)

    def create_checkbox(self, desc, layout, group, selections):
        self.checkboxes.append(CheckBox(desc, layout, group, selections, self.handle_checkbox_change))
        return self.checkboxes[-1].widget

    def handle_checkbox_change(self, _): # TODO - move constants out
        if _.name == 'value':
            selections = set()
            for checkbox in self.checkboxes:
                if checkbox.group == SelectionGroup.data_structures:
                    if checkbox.widget.value == False:
                        selections.add('(Tag != %s)' % (checkbox.selections))
                else:
                    for selection in checkbox.selections:
                        if checkbox.widget.value == False:
                            selections.add('(Access != %d)' % (selection))
            self.df.select('&'.join(selections), mode='replace') # replace not necessary for correctness, but maybe perf?

class CheckBox():
    def __init__(self, desc, layout, group, selections, handle_fun):
        self.widget = Checkbox(description=desc, layout=layout,
                                value=True, disabled=False, indent=False)
        self.widget.observe(handle_fun)
        self.group = group
        self.selections = selections

