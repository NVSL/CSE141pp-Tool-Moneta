from ipywidgets import VBox, HBox, Layout, Label, ColorPicker, GridBox
import ipyvuetify as v
vdiv = HBox([
    VBox(layout=Layout(
        padding='0',
        border='1px solid black',
        width='0',
        height='50px', margin='0'))
    ], layout=Layout(justify_content='center'))
lvdiv = HBox([
    VBox(layout=Layout(
        padding='0',
        border='1px solid #cccbc8',
        width='0',
        height='50px', margin='0'))
            ], layout=Layout(justify_content='center'))
hdiv = VBox([
    HBox(layout=Layout(
        padding='0',
        border='1px solid black',
        width='0',
        height='70px'))
    ], layout=Layout(justify_content='center'))
lhdiv = VBox([
    HBox(layout=Layout(
        padding='0',
        border='1px solid #cccbc8',
        width='0',
        height='50px'))
            ], layout=Layout(justify_content='center'))
class Checks():
    def __init__(self, model):
        self.model = model
        self.widgets = self.init_widgets()

    def init_widgets(self):
        read_hit = ChildCheckbox(self.compute_all)
        write_hit = ChildCheckbox(self.compute_all)
        read_miss = ChildCheckbox(self.compute_all)
        write_miss = ChildCheckbox(self.compute_all)
        read_capmiss = ChildCheckbox(self.compute_all)
        write_capmiss = ChildCheckbox(self.compute_all)
        chks = [read_hit, write_hit, read_miss,
                write_miss, read_capmiss, write_capmiss]


        self.all_check = ParentCheckbox(chks, self.compute_all, prepend_icon='fa-globe')
        self.read_check = ParentCheckbox([read_hit, read_miss, read_capmiss], self.compute_all, label="R")
        self.write_check = ParentCheckbox([write_hit, write_miss, write_capmiss], self.compute_all, label="W")
        self.hit_check = ParentCheckbox([read_hit, write_hit], self.compute_all, prepend_icon="fa-dot-circle-o")
        self.miss_check = ParentCheckbox([read_miss, write_miss], self.compute_all, prepend_icon="fa-legal")
        self.capmiss_check = ParentCheckbox([read_capmiss, write_capmiss], self.compute_all, prepend_icon="fa-battery")
        self.parentcheckboxes = [self.all_check, self.read_check, self.write_check, 
                self.hit_check, self.miss_check, self.capmiss_check]

        def colbox(check):
            return HBox([check.widget], layout=Layout(align_items="center", overflow="hidden"))

        def primbox(check):
            return HBox([check.widget, ColorPicker(concise=True,disabled=False,
                            value="red",layout=Layout(width="30px",margin="0 0 0 -3px", padding="-5"))],
                layout=Layout(justify_content="center",align_items="center",overflow="hidden"))

        alls = colbox(self.all_check)

        read = HBox([self.read_check.widget], layout=Layout(margin="0 0 0 6px", align_items="center", overflow="hidden"))
        write = HBox([self.write_check.widget], layout=Layout(margin="0 0 0 6px", align_items="center", overflow="hidden"))

        hits = colbox(self.hit_check)
        misses = colbox(self.miss_check)
        capmisses = colbox(self.capmiss_check)

        gridbox = HBox([GridBox([alls, vdiv, read, vdiv, write,
            hdiv, hdiv, hdiv, hdiv, hdiv,
            hits, vdiv, primbox(read_hit), lvdiv, primbox(write_hit),
            hdiv, hdiv, lhdiv, lhdiv, lhdiv,
            misses, vdiv, primbox(read_miss), lvdiv, primbox(write_miss),
            hdiv, hdiv, lhdiv, lhdiv, lhdiv,
            capmisses, vdiv, primbox(read_capmiss), lvdiv, primbox(write_capmiss)],
            layout=Layout(grid_template_rows="50px 2px 50px 2px 50px 2px 50px", grid_template_columns="70px 5px 70px 5px 70px"))], layout=Layout(margin="20px"))

        return gridbox

    def compute_all(self, *_):
        for parent in self.parentcheckboxes:
            parent.update()


class ParentCheckbox:
    def __init__(self, children, compute_all, label=None, prepend_icon=None):
        if label is None and prepend_icon is None:
            raise SystemError
        if label is None:
            self.widget = v.Checkbox(prepend_icon=prepend_icon, v_model=False)
        else:
            self.widget = v.Checkbox(label=label, v_model=False)
        self.widget.on_event('change', self.handler)
        self.children = children
        self.compute_all = compute_all

    def handler(self, checkbox, _, new):
        self.widget.indeterminate = False
        for child in self.children:
            child.widget.v_model = new
        self.compute_all()

    def update(self):
        on = 0
        off = 0
        for child in self.children:
            if child.widget.v_model:
                on+=1
            else:
                off+=1
        self.widget.v_model = on == len(self.children)
        self.widget.indeterminate = on > 0 and off > 0

class ChildCheckbox:
    def __init__(self, handler):
        self.widget = v.Checkbox(ripple=False, v_model=False, color='primary')
        self.widget.on_event('change', handler)
