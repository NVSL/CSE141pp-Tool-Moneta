from ipywidgets import Button, HBox, Label, Layout, VBox
import ipyvuetify as v
from moneta.settings import (
        vdiv, lvdiv, hdiv, lhdiv,
        LEGEND_CLICK_ZOOM, newc, CUSTOM_CMAP, INDEX, ADDRESS, 
        ACCESS, TextStyle, WARNING_LABEL, INDEX_LABEL, ADDRESS_LABEL
)
from vaex.jupyter.utils import debounced
import vaex
import matplotlib.pyplot as mpl_plt
import ipywidgets as widgets
import numpy as np

global click_zoom_x
click_zoom_x = 0
global click_zoom_y
click_zoom_y = 0

class Click_Zoom():
    def __init__(self, model, accesses, tags):
        mpl_plt.ioff()
        self.model = model
        self.colors = np.copy(newc)
        self.click_zoom_widget = widgets.Output()
        self.widgets = self.create_click_zoom()
        self.accesses = accesses
        self.tags = tags

    def set_plot(self, plot):
        self.plot = plot
        self.click_zoom_obj = self.click_zoom_observer(self.plot, self.plot.backend, self.click_zoom_widget, self.czoom_button, self.model, self.accesses, self.tags)

    def create_click_zoom(self):
        czoom_xaxis = widgets.IntSlider(value=50, min=20, max=5000, step=10, description='Access Range', disabled=False, 
                                  continuous_update=False, orientation='horizontal', readout=True, readout_format='d')
        czoom_yaxis = widgets.IntSlider(value=100, min=50, max=10000, step=10, description='Bytes Range', disabled=False, 
                                  continuous_update=False, orientation='horizontal', readout=True, readout_format='d')
        #czoom_xaxis.layout.visibility = "hidden"
        #czoom_yaxis.layout.visibility = "hidden"
        global click_zoom_x
        click_zoom_x = czoom_xaxis.value
        global click_zoom_y
        click_zoom_y = czoom_yaxis.value
        click_zoom_button_layout = widgets.Layout(width='auto', height='40px') #set width and height

        self.czoom_button = widgets.Button(
            description='Zoom to Area',
            disabled=False,
            display='flex',
            flex_flow='column',
            align_items='stretch', 
            layout = click_zoom_button_layout
        )
        self.czoom_button.layout.display = 'none'
        def on_x_value_change(change):
            global click_zoom_x
            click_zoom_x = change['new']

        def on_y_value_change(change):
            global click_zoom_y
            click_zoom_y = change['new']
 
        czoom_xaxis.observe(on_x_value_change, names='value')
        czoom_yaxis.observe(on_y_value_change, names='value')

        def czoom_zoom(b):
            self.plot.backend.scale_x.min = self.click_zoom_obj.x_coormin
            self.plot.backend.scale_x.max = self.click_zoom_obj.x_coormax
            self.plot.backend.scale_y.min = self.click_zoom_obj.y_coormin
            self.plot.backend.scale_y.max = self.click_zoom_obj.y_coormax
            self.plot.backend._update_limits()

        self.czoom_button.on_click(czoom_zoom)

        czoom_layout = widgets.Layout(display='flex',width='400px',overflow_y='auto',padding='10px')
        czoom_box = VBox([self.click_zoom_widget] + [czoom_xaxis] + [czoom_yaxis] + [self.czoom_button],
                         layout=Layout(overflow_y='auto', padding='10px'))
        return czoom_box

    class click_zoom_observer:
        def __init__(self, plot, observable, widget, button, model, accesses, tags):
            self.observable = observable
            self.model = model
            self.accesses = accesses
            self.tags = tags
            self.plot = plot
            self.df = self.model.curr_trace.df
            #self.selections = 
            self.widget = widget
            self.button = button
            #this line is to get this object to update whenever the selected coords are updated
            self.observable.bind_to(self.update_click_zoom_coords)
            self.x_coormin = 0
            self.x_coormax = 0
            self.y_coormin = 0
            self.y_coormax = 0

        def update_df_selections(self, df):
            self.df = df

        def update_selection(self): 
            selection = self.get_select_string()
            if len(selection) is not 0:
                tmp_df = self.model.curr_trace.df
                tmp_df.select(self.get_select_string())
                selected_address = tmp_df.evaluate(self.df[ADDRESS], selection=True)
                selected_index = tmp_df.evaluate(self.df[INDEX], selection=True)
                selected_access = tmp_df.evaluate(self.df[ACCESS], selection=True)
                #if constants are changed, the following code line must change accordingly
                #using non-constants here for column names because non-constants do not work
                selected_array = vaex.from_arrays(Access=selected_access, Address=selected_address, index=selected_index)
                self.update_df_selections(selected_array)
            else:
                self.update_df_selections(self.model.curr_trace.df)

        def get_select_string(self): # TODO - move constants out
            selections = set()
            for checkbox in self.accesses.checkboxes:
                if checkbox.widget.v_model == False:
                    selections.add('(Access != %d)' % (checkbox.acc_type))
            for checkbox in self.tags.checkboxes:
                if checkbox.widget.v_model == False:
                    selections.add('((%s < %s) | (%s > %s))' % (INDEX, checkbox.start, INDEX, checkbox.stop))
            return '&'.join(selections)

        def update_color_map(self):
            newc = np.ones((7, 4))
            newc[1] = self.plot.colormap.colors[1]
            newc[2] = self.plot.colormap.colors[2]
            newc[3] = self.plot.colormap.colors[4]
            newc[4] = self.plot.colormap.colors[5]
            newc[5] = self.plot.colormap.colors[6]
            newc[6] = self.plot.colormap.colors[8]
            self.colors = newc
            #indices = [1, 2, 4, 5, 6, 8]
            #self.colors = np.take(self.plot.colormap.colors, indices)

        @debounced(0.5, method=True)
        def update_click_zoom_coords(self, data, updating):
            self.update_selection()
            self.update_color_map()
            #first check if there is no data to zoom into
            if updating is not True:
              print(f"{WARNING_LABEL}{TextStyle.YELLOW} no data for click zoom to zoom in{TextStyle.END}")
              return

            czoom_df_filter1 = self.df[self.df[INDEX] < self.observable.czoom_xmax]
            czoom_df_filter2 = czoom_df_filter1[self.df[INDEX] > self.observable.czoom_xmin]
            czoom_df_filter3 = czoom_df_filter2[self.df[ADDRESS] > self.observable.czoom_ymin]
            czoom_df_filter4 = czoom_df_filter3[self.df[ADDRESS] < self.observable.czoom_ymax]

            #second check if there is no data to zoom into
            try: 
              zoom_x = czoom_df_filter4[INDEX].values[-1]
            except:
              print(f"{WARNING_LABEL}{TextStyle.YELLOW} no data for click zoom to zoom in{TextStyle.END}")
              return

            zoom_y = czoom_df_filter4[ADDRESS].values[-1]
            global click_zoom_x
            global click_zoom_y
            #set limits for data
            self.x_coormin = zoom_x - click_zoom_x/2
            self.x_coormax = zoom_x + click_zoom_x/2
            self.y_coormin = zoom_y - click_zoom_y/2
            self.y_coormax = zoom_y + click_zoom_y/2

            #filter data to only those limits from newly created dataframe
            df_filter1 = self.df[self.df[INDEX] < self.x_coormax]
            df_filter2 = df_filter1[self.df[INDEX] > self.x_coormin]
            df_filter3 = df_filter2[self.df[ADDRESS] > self.y_coormin]
            df_filter4 = df_filter3[self.df[ADDRESS] < self.y_coormax]
            colors = self.colors[df_filter4[ACCESS].values]
            
	    #df_filter4.evaluate(selection=True)
            self.plot_click_zoom(df_filter4, colors, self.x_coormin, self.x_coormax, self.y_coormin, self.y_coormax)
 
        def plot_click_zoom(self, dataset, colors, xlim_min, xlim_max, ylim_min, ylim_max):
            plot_message = "Done plotting click zoom"
            print(f"{TextStyle.GREEN}{TextStyle.BOLD}\n"
                  f"{plot_message}\n"
                  f"{TextStyle.END}\n")
            self.widget.clear_output()
            if self.button.layout.display == "none":
                self.button.layout.display = "block"
            with self.widget:
                #filter for indices and addresses and their access type that are currently displayed in main widget
                mpl_plt.scatter(dataset[INDEX].values, dataset[ADDRESS].values, c=colors, s=0.5, cmap=self.plot.colormap)
                mpl_plt.title('Mini Zoom')
                mpl_plt.xlabel(INDEX_LABEL)
                mpl_plt.ylabel(ADDRESS_LABEL)
                #set limits
                mpl_plt.xlim(xlim_min, xlim_max)
                mpl_plt.ylim(ylim_min, ylim_max)
                mpl_plt.show()
    
