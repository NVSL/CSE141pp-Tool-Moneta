from ipywidgets import VBox, HBox, Layout, Button, ToggleButton
import ipyvuetify as v
from moneta.settings import ADDRESS, THREAD_ID


from moneta.utils import percent_string
from moneta.settings import ADDRESS
import logging
log = logging.getLogger(__name__)


class Tags():
    def __init__(self, model, update_selection, tag_type):
        self.model = model
        self.tag_type = tag_type
        self.update_selection = update_selection
        self.checkboxes = []
        self.widgets = self.init_widgets(tag_type)

    def init_widgets(self, tag_type):
        self.all_check = v.Checkbox(v_on='tooltip.on', prepend_icon='fa-globe', label="All", v_model=True, class_='ma-0 mt-1 pa-0')
        self.all_check_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': self.all_check}],
                children=["Select all"])
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
            if tag.tag_type == tag_type:
                chk = Checkbox(tag)
                self.checkboxes.append(chk)
                chk.widget.on_event('change', self.update_all_checkbox)
                stats = self.get_stats(tag)
                btn, tooltip = self.create_zoom_button(tag, stats=stats)
                highlight_btn, highlight_tooltip = self.create_highlight_toggle(tag, stats=stats)
                statss = self.tag_tooltip(tag, stats).splitlines()

                tag_row = v.Row(children=[
                    btn,
                    highlight_btn,
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
            self.model.plot.backend.zoom_sel(float(tag.access[0]), float(tag.access[1])+1,
                                    float(tag.address[0]), float(tag.address[1])+1)
        btn.on_click(zoom_to_selection)
        return btn, tooltip

    def create_highlight_toggle(self, tag, stats=None): #TODO move constants out
        if stats is None:
            stats = self.get_stats(tag)

        tooltip = self.tag_tooltip(tag, stats)
        toggle_btn = ToggleButton(
                value=False,
                description='',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Press to toggle highlighting of the tag region.',
                icon='binoculars', # (FontAwesome names without the `fa-` prefix)
                layout=Layout(height='35px', width='35px',
                    borders='none', align_items='center'
                )
            )
        
        def highlight(toggle_value):
            self.model.plot.backend.highlight_selection(float(tag.access[0]), float(tag.access[1])+1,
                                                        float(tag.address[0]), float(tag.address[1])+1, toggle_value, tag)

        toggle_btn.observe(highlight, 'value')



        return toggle_btn, tooltip

    def get_stats(self, tag):
        df = self.model.curr_trace.df
        return df[df[tag.query_string()]].count(binby=[df.Access], limits=[1,7], shape=[6])


    def dropdown_str(self, tag, stats):
        total = sum(stats)
        m = len(str(total))
        final_str = (
                f'Access Range: {tag.access[0]}, {tag.access[1]}\n'
                f'Address Range: 0x{int(tag.address[0]):X}, 0x{int(tag.address[1]):X}\n'
                f'Total: {total}\n'
                f'{stats[0]:0{m}} ({percent_string(stats[0],total)}), {stats[1]:0{m}} ({percent_string(stats[1],total)}) Hits\n'
                f'{stats[2]:0{m}} ({percent_string(stats[2],total)}), {stats[3]:0{m}} ({percent_string(stats[3],total)}) Caps\n'
                f'{stats[4]:0{m}} ({percent_string(stats[4],total)}), {stats[5]:0{m}} ({percent_string(stats[5],total)}) Comp\n'
        )
        return final_str

    def tag_tooltip(self, tag, stats):
        total = sum(stats)
        final_tooltip = (
                f'Access Range: {tag.access[0]}, {tag.access[1]}\n'
                f'Address Range: 0x{int(tag.address[0]):X}, 0x{int(tag.address[1]):X}\n'
                f'Total: {total}\n'
                f'Read Hits: {stats[0]} ({percent_string(stats[0],total)}) \n'
                f'Write Hits: {stats[1]} ({percent_string(stats[1],total)}) \n'
                f'Total Hits: {stats[0]+stats[1]} ({percent_string(stats[0]+stats[1],total)}) \n'
                f'Capacity Read Misses: {stats[2]} ({percent_string(stats[2],total)}) \n'
                f'Capacity Write Misses: {stats[3]} ({percent_string(stats[3],total)}) \n'
                f'Total Capacity Misses: {stats[2]+stats[3]} ({percent_string(stats[2]+stats[3],total)}) \n'
                f'Compulsory Read Misses: {stats[4]} ({percent_string(stats[4],total)}) \n'
                f'Compulsory Write Misses: {stats[5]} ({percent_string(stats[5],total)}) \n'
                f'Total Compulsory Misses: {stats[4]+stats[5]} ({percent_string(stats[4]+stats[5],total)}) \n'
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
        self.widget = v.Checkbox(label=tag.display_name(), v_model=True, class_='ma-0 mt-1 pa-0')
        self.start = tag.access[0] # Could fix x-axis being 1 access here aka access[0] == access[1]
        self.stop = tag.access[1]
        self.top = tag.address[1]
        self.bottom = tag.address[0]
        self.tag = tag
