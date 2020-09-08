from ipywidgets import Output
from moneta.settings import INDEX_LABEL, ADDRESS_LABEL, CUSTOM_CMAP
from scipy.spatial.distance import cdist
import numpy as np
import vaex
class ClickZoom():
    def __init__(self, model):
        print("Click zoom init")
        self.model = model
        self.widget = Output(layout={'border': '1px solid black'})
        self.df = self.model.curr_trace.df
        print(self.df)
        print(self.df.columns)
        with self.widget:
            self.df.plot(self.df[INDEX_LABEL], self.df[ADDRESS_LABEL], colormap = CUSTOM_CMAP, what='max(Access)', limits=[self.model.curr_trace.x_lim, self.model.curr_trace.y_lim], shape=512, colorbar=False, figsize=(10,10))

    def update_click_zoom(self, x, y, found_point):
        with self.widget:
            self.widget.clear_output()
            print("updating click zoom ", x, y)

            x_lim = [x-500, x+500]
            y_lim = [y-500, y+500]

            if found_point:
                print("found point")
            else:
                print("did not find point")
                res = cdist([[x,y]], self.df[["Access_Number", ADDRESS_LABEL]]).argmin()
                print(res)
                print(res, self.df[res])
                print(self.df)

            display(self.df.plot(self.df[INDEX_LABEL], self.df[ADDRESS_LABEL], colormap = CUSTOM_CMAP, what='max(Access)', limits=[x_lim, y_lim], shape=512, colorbar=False, figsize=(10,10)))
