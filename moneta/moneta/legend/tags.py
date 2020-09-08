from ipywidgets import VBox, HBox, Layout
import ipyvuetify as v
class Tags():
    def __init__(self, model, update_selection):
        self.model = model
        self.update_selection = update_selection
        self.checkboxes = []
        self.widgets = self.init_widgets()

    def init_widgets(self):
        max_id = max(self.model.curr_trace.tags, key=lambda x: x.id_).id_
        df = self.model.curr_trace.df
        stats = df.count(binby=[df.Tag, df.Access], limits=[[0,max_id+1], [1,7]], shape=[max_id+1,6])

        self.all_check = v.Checkbox(v_on='tooltip.on', prepend_icon='fa-globe', label="All", v_model=True, class_='ma-0 mt-1 pa-0')
        self.all_check_tp = v.Tooltip(bottom=True, v_slots=[{'name': 'activator', 'variable': 'tooltip', 'children': self.all_check}],
                children=["Select all tags"])
        self.all_check.on_event('change', self.check_all)


        all_row = [v.Row(children=[self.all_check_tp], class_='ml-1')]

        tag_rows = []
        for tag in self.model.curr_trace.tags:
            chk = Checkbox(tag.name, tag.id_)
            self.checkboxes.append(chk)
            chk.widget.on_event('change', self.update_all_checkbox)
            tag_rows.append(v.Row(children=[
                self.create_zoom_button(tag, stats),
                chk.widget
                ], class_='ml-0'))
        return VBox([v.List(children=(all_row + tag_rows), dense=True, nav=True, max_height="240px", max_width="200px")])

    def create_zoom_button(self, tag, stats):
        btn = v.Btn(v_on='tooltip.on', icon=True, children=[v.Icon(
            children=['fa-search-plus'])])
        def zoom_to_selection(*_):
            self.zoom_sel_handler(float(tag.access[0]), float(tag.access[1]),
                                    float(tag.address[0]), float(tag.address[1]))
        btn.on_event('click', zoom_to_selection)
        btn_tp = v.Tooltip(bottom=True, v_slots=[{
            'name': 'activator', 'variable': 'tooltip', 'children': btn}],
            children=[self.tag_tooltip(tag, stats)])
        return btn_tp

    def set_zoom_sel_handler(self, f):
        self.zoom_sel_handler = f

    def tag_tooltip(self, tag, stats):
        return ("(" + tag.access[0] + ", " + tag.access[1] + "), " +
        "(" + tag.address[0] + ", " + tag.address[1] + ")" + self.stats_to_str(tag.id_, stats))

    def stats_to_str(self, ind, stats):
        total = sum(stats[ind])
        if total == 0:
            return ','.join([repr(stat) for stat in stats[ind]])
        hits = stats[ind][0] + stats[ind][1]
        return ','.join([repr(stat) for stat in stats[ind]]) + ",\n" + repr(hits/total) + "," + repr((total-hits)/total)


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
    def __init__(self, name, tag_id):
        self.widget = v.Checkbox(label=name, v_model=True, class_='ma-0 mt-1 pa-0')
        self.tag_id = tag_id

