from ipywidgets import VBox, HBox, Layout
import ipyvuetify as v
class Tags():
    def __init__(self, model):
        self.model = model
        self.checkboxes = []
        self.widgets = self.init_widgets()

    def init_widgets(self):
        max_id = max(self.model.curr_trace.tags, key=lambda x: x.id_).id_
        df = self.model.curr_trace.df
        stats = df.count(binby=[df.Tag, df.Access], limits=[[0,max_id+1], [1,7]], shape=[max_id+1,6])

        self.all_check = v.Checkbox(label="All", v_model=True, class_='ma-0 mt-1 pa-0')
        self.all_check.on_event('change', self.check_all)

        all_row = [v.Row(children=[
                        v.Btn(icon=True, children=[v.Icon(children=['fa-search-plus'],dense=True)]),
                        self.all_check
                        ], class_='ml-0')]

        tag_rows = []
        for tag in self.model.curr_trace.tags:
            self.checkboxes.append(v.Checkbox(label=tag.name, v_model=True, class_='ma-0 mt-1 pa-0'))
            self.checkboxes[-1].on_event('change', self.update_all_checkbox)
            tag_rows.append(v.Row(children=[
                v.Btn(icon=True, children=[v.Icon(children=['fa-search-plus'])]),
                self.checkboxes[-1]
                ], class_='ml-0'))
        #tag_rows = [v.Row(children=[
        #                v.Btn(icon=True, children=[v.Icon(children=['fa-search-plus'])]),
        #                v.Checkbox(label=tag.name, v_model=True, class_='ma-0 mt-1 pa-0')
        #                ], class_='ml-0') for tag in self.model.curr_trace.tags]
        return VBox([v.List(children=(all_row + tag_rows), dense=True, nav=True, max_height="240px", max_width="200px")])

    def check_all(self, _checkbox, _, new):
        for checkbox in self.checkboxes:
            checkbox.v_model = new

    def update_all_checkbox(self, *_):
        on = 0
        off = 0
        for checkbox in self.checkboxes:
            if checkbox.v_model:
                on+=1
            else:
                off+=1
        self.all_check.v_model = on == len(self.checkboxes)
        self.all_check.indeterminate = on > 0 and off > 0

