#from vaex.jupyter.widgets import *
import ipyvuetify as v
import ipywidgets as widgets
from traitlets import *

class PlotTemplate(v.VuetifyTemplate):
    show_output = Bool(False).tag(sync=True)
    new_output = Bool(False).tag(sync=True)
    default_title = Unicode('Moneta')
    title = default_title.tag(sync=True)

    drawer = Bool(True).tag(sync=True)
    clipped = Bool(False).tag(sync=True)
    model = Any(True).tag(sync=True)
    floating = Bool(False).tag(sync=True)
    dark = Bool(False).tag(sync=True)
    mini = Bool(False).tag(sync=True)
    components = Dict(None, allow_none=True).tag(sync=True, **widgets.widget.widget_serialization)
    items = Any([]).tag(sync=True)
    type = Unicode('temporary').tag(sync=True)
    items = List(['red', 'green', 'purple']).tag(sync=True)
    button_text = Unicode('menu').tag(sync=True)
    drawers = Any(['Default (no property)', 'Permanent', 'Temporary']).tag(sync=True)
    edit_title = Bool(False).tag(sync=True)
    template = Unicode('''

<v-app>
    <v-app-bar :clipped-left="clipped" absolute dense>
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-toolbar-title v-on="on" v-show="edit_title == false"
            @click="function() {edit_title = true}"
          >{{title}}</v-toolbar-title>
        </template>
        <span>Edit title</span>
      </v-tooltip>
      <v-text-field v-show="edit_title" @input="function(val) {title = val}"
        dense placeholder="Plot Title" :value=title
        filled append-icon='check' height='12px'
        @click:append="function() {edit_title = false; if (title === '') title = default_title}"
        @keydown="function (e) {if (e.keyCode == 13 || e.keyCode == 27) \
          {edit_title = false; if (title === '') title = default_title}}"
      ></v-text-field>
      <v-spacer></v-spacer>
      <extra-widget />
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-main>
    <v-container>
          <main-widget/>
          </v-container>
    </v-main>
</v-app>
''').tag(sync=True)

