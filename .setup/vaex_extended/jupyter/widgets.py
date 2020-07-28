from vaex.jupyter.widgets import *

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
    <v-navigation-drawer
      v-model="model"
      :permanent="type === 'permanent'"
      :temporary="type === 'temporary'"
      :clipped="clipped"
      :floating="floating"
      :mini-variant="mini"
      absolute
      overflow
    >

        <control-widget/>

      </v-list>

    </v-navigation-drawer>

    <v-navigation-drawer
      v-model="show_output"
      :temporary="type === 'temporary'"
      clipped
      right
      absolute
      overflow
    >
      <h3>Output</h3>
      <output-widget />
    </v-navigation-drawer>

    <v-app-bar :clipped-left="clipped" absolute dense>
      <v-app-bar-nav-icon v-show="false"
        v-if="type !== 'permanent'"
        @click.stop="model = !model"
      ></v-app-bar-nav-icon>
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
      <toolbox/>      
      <v-spacer></v-spacer>


      <v-btn icon @click.stop="show_output = !show_output; new_output=false">
        <v-badge color="red" overlap>
          <template v-slot:badge v-if="new_output">
            <span>!</span>
          </template>
          <v-icon>error_outline</v-icon>
        </v-badge>
      </v-btn>


    </v-app-bar>
    <v-content class="mt-12">
          <main-widget/>
    </v-content>
</v-app>
''').tag(sync=True)


