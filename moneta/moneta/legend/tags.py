from ipywidgets import VBox, HBox, Layout, Button
import ipyvuetify as v
from moneta.utils import stats_percent
from moneta.settings import ADDRESS

class Tags():
    def __init__(self, model, update_selection):
        self.model = model
        self.update_selection = update_selection
        self.checkboxes = []
        self.widgets = self.init_widgets()

    def init_widgets(self):
        self.all_check = v.Checkbox(v_on='tooltip.on', prepend_icon='fa-globe', label="All", v_model=True, class_='ma-0 mt-1 pa-0')
        self.all_check_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': self.all_check}],
                children=["Select all tags"])
        self.all_check.on_event('change', self.check_all)
        all_row = [v.Row(children=[self.all_check_tp], class_='ml-7')]

        tag_rows = []
        treenodelabel = v.Html(tag='style', children=[(".vuetify-styles .v-treeview-node__label {"
            "margin-left: 0px;"
            "overflow: visible;"
            "}"
            ".vuetify-styles .v-input--selection-controls:not(.v-input--hide-details) .v-input__slot {"
            "margin-bottom: 0px;"
            "}"
            ".vuetify-styles .v-treeview-node__root .v-icon.v-icon.v-icon--link {"
            "margin-bottom: 10px;"
            "}"
            ".vuetify-styles .v-treeview-node--leaf {"
            "margin-left: 0px;"
            "}"
            ".vuetify-styles .v-treeview--dense .v-treeview-node__root {"
            "min-height: 21px;"
            "}"
        )]) 
        for tag in self.model.curr_trace.tags:
            chk = Checkbox(tag)
            self.checkboxes.append(chk)
            chk.widget.on_event('change', self.update_all_checkbox)
            stats = self.get_stats(tag)
            btn, tooltip = self.create_zoom_button(tag, stats=stats)
            statss = self.dropdown_str(tag, stats).splitlines()

            tag_row = v.Row(children=[
                btn,
                chk.widget
                ], class_='ml-0')
            items = [{
              'id': 1,
              'name': '',
              'children': [{'id': i+2, 'name': stat} for i, stat in enumerate(statss)],
            }]
            treeview = v.Treeview(items=items, dense=True)
            tag_rows.append(v.Container(row=False, class_="d-flex justify-start ma-0 pa-0",children=[
                    v.Col(cols=1, children=[treeview], class_="ma-0 pa-0"),
                    v.Col(cols=12, children=[tag_row], class_="pt-0 pb-0")
                    ]))
        tag_rows.append(v.Container(row=False, children=[treenodelabel]))
        return VBox([v.List(children=(all_row + tag_rows), dense=True, nav=True, max_height="300px", max_width="200px")])

    def create_zoom_button(self, tag, stats=None): #TODO move constants out
        if stats is None:
            stats = self.get_stats(tag)

        tooltip = self.tag_tooltip(tag, stats)
        btn = Button(icon='search-plus', tooltip=self.tag_tooltip(tag, stats), 
                style={'button_color': 'transparent'},
                layout=Layout(height='35px', width='35px',
                    borders='none', align_items='center'
                ))
        def zoom_to_selection(*_):
            self.zoom_sel_handler(float(tag.access[0]), float(tag.access[1])+1,
                                    float(tag.address[0]), float(tag.address[1])+1)
        btn.on_click(zoom_to_selection)
        return btn, tooltip

    def set_zoom_sel_handler(self, f):
        self.zoom_sel_handler = f

    def get_stats(self, tag):
        df = self.model.curr_trace.df
        rows = df[int(tag.access[0]):int(tag.access[1])+1]
        return rows[rows[f'({ADDRESS} >= {tag.address[0]}) & ({ADDRESS} <= {tag.address[1]})']].count(binby=[df.Access], limits=[1,7], shape=[6])

    def dropdown_str(self, tag, stats):
        total = sum(stats)
        m = len(str(total))
        final_str = (
                f'Access Range: {tag.access[0]}, {tag.access[1]}\n'
                f'Address Range: {tag.address[0]}, {tag.address[1]}\n'
                f'Total: {total}\n'
                f'{stats[0]:0{m}} ({stats_percent(stats[0],total)}), {stats[1]:0{m}} ({stats_percent(stats[1],total)}) Hits\n'
                f'{stats[2]:0{m}} ({stats_percent(stats[2],total)}), {stats[3]:0{m}} ({stats_percent(stats[3],total)}) Caps\n'
                f'{stats[4]:0{m}} ({stats_percent(stats[4],total)}), {stats[5]:0{m}} ({stats_percent(stats[5],total)}) Comp\n'
        )
        return final_str

    def tag_tooltip(self, tag, stats):
        total = sum(stats)
        final_tooltip = (
                f'Access Range: {tag.access[0]}, {tag.access[1]}\n'
                f'Address Range: 0x{int(tag.address[0]):X}, 0x{int(tag.address[1]):X}\n'
                f'Total: {total}\n'
                f'Read Hits: {stats[0]} ({stats_percent(stats[0],total)}) \n'
                f'Write Hits: {stats[1]} ({stats_percent(stats[1],total)}) \n'
                f'Capacity Read Misses: {stats[2]} ({stats_percent(stats[2],total)}) \n'
                f'Capacity Write Misses: {stats[3]} ({stats_percent(stats[3],total)}) \n'
                f'Compulsory Read Misses: {stats[4]} ({stats_percent(stats[4],total)}) \n'
                f'Compulsory Write Misses: {stats[5]} ({stats_percent(stats[5],total)}) \n'
        )
        return final_tooltip

    def check_all(self, _checkbox, _, new):
        self.all_check.indeterminate = False
        for checkbox in self.checkboxes:
            checkbox.widget.v_model = new
        self.update_selection()

    def update_all_checkbox(self, *_):
        on = 0
        off = 0
        for checkbox in self.checkboxes:
            if checkbox.widget.v_model:
                on+=1
            else:
                off+=1
        self.all_check.v_model = on == len(self.checkboxes)
        self.all_check.indeterminate = on > 0 and off > 0
        self.update_selection()

class Checkbox:
    def __init__(self, tag):
        self.widget = v.Checkbox(label=tag.name, v_model=True, class_='ma-0 mt-1 pa-0')
        self.start = tag.access[0] # Could fix x-axis being 1 access here aka access[0] == access[1]
        self.stop = tag.access[1]
        self.top = tag.address[1]
        self.bottom = tag.address[0]

