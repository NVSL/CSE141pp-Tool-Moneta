from ipywidgets import VBox, HBox, Layout
import ipyvuetify as v
class Tags():
    def __init__(self, model):
        self.model = model
        self.widgets = self.init_widgets()

    def init_widgets(self):
        max_id = max(self.model.curr_trace.tags, key=lambda x: x.id_).id_
        df = self.model.curr_trace.df
        stats = df.count(binby=[df.Tag, df.Access], limits=[[0,max_id+1], [1,7]], shape=[max_id+1,6])

        all_row = [v.Row(children=[
                        v.Btn(icon=True, children=[v.Icon(children=['fa-search-plus'],dense=True)]),
                        v.Checkbox(label="All", v_model=True, class_='ma-0 mt-1 pa-0')
                        ], class_='ml-0')]

        tag_rows = [v.Row(children=[
                        v.Btn(icon=True, children=[v.Icon(children=['fa-search-plus'])]),
                        v.Checkbox(label=tag.name, v_model=True, class_='ma-0 mt-1 pa-0')
                        ], class_='ml-0') for tag in self.model.curr_trace.tags]
        return VBox([v.List(children=(all_row + tag_rows), dense=True, nav=True, max_height="240px", max_width="200px")])
