from ipywidgets import Output
from moneta.settings import INDEX_LABEL, ADDRESS_LABEL, CUSTOM_CMAP, newc
from scipy.spatial.distance import cdist
import numpy as np
import matplotlib.pyplot as mpl_plt
mpl_plt.ioff()

import vaex
class ClickZoom():
    def __init__(self, model):
        print("Click zoom init")
        self.model = model
        self.widget = Output(layout={'border': '1px solid black'})
        self.df = self.model.curr_trace.df
        print(self.df)
        print(self.df.columns)
        #with self.widget:
        #    self.df.plot(self.df[INDEX_LABEL], self.df[ADDRESS_LABEL], colormap = CUSTOM_CMAP, what='max(Access)', limits=[self.model.curr_trace.x_lim, self.model.curr_trace.y_lim], shape=512, colorbar=False, figsize=(10,10))

    def update_click_zoom(self, x, y, found_point):
        with self.widget:
            self.widget.clear_output()
            print("updating click zoom ", x, y)

            x_lim = [x-500, x+500]
            y_lim = [y-500, y+500]
            x_diff = 500
            y_diff = 500

            if found_point:
                print("found point")
            else:
                print("did not find point")
                res = cdist([[int(x),int(y)]], self.df[["Access_Number", ADDRESS_LABEL]]).argmin()
                #mres = cdist([[int(x),int(y)]], self.df[["Access_Number", ADDRESS_LABEL]], metric='cityblock').argmin()
                #print(res)
                #print(mres)
                #print(res, self.df[res])
                #print(self.df)
                #print(self.df.columns)
                print(self.df.columns["Access_Number"][res])
                print(self.df.columns[ADDRESS_LABEL][res])
                buff = 2
                x_diff = abs(int(x) - self.df.columns["Access_Number"][res])*buff
                y_diff = abs(int(y) - self.df.columns[ADDRESS_LABEL][res])*buff
                x_lim = [x-x_diff, x+x_diff]
                y_lim = [y-y_diff, y+y_diff]
            resdf = self.df[(self.df['Access_Number'] >= x-x_diff) & (self.df['Access_Number'] <= x + x_diff) & (self.df[ADDRESS_LABEL] >= y - y_diff) & (self.df[ADDRESS_LABEL] <= y+y_diff)]
            print(resdf.Tag.max())
            mpl_plt.scatter(resdf.Access_Number.values, resdf.Bytes.values, s=0.5, c=resdf.Access.values, cmap=CUSTOM_CMAP, vmin=0, vmax=10)
            print(resdf.Access_Number.values[:10])
            print(resdf.Bytes.values[:10])
            print(resdf.Tag.values[:10])
            mpl_plt.xlim(x-x_diff, x+x_diff)
            mpl_plt.ylim(y-y_diff, y+y_diff)
            mpl_plt.show()

            #z = self.df.plot(self.df[INDEX_LABEL], self.df[ADDRESS_LABEL], colormap = CUSTOM_CMAP, what='max(Access)', limits=[x_lim, y_lim], shape=512, colorbar=False, figsize=(10,10))
            #print(dir(z))
            #print(type(z.figure))
            #print(dir(z.figure))
            #print(z.set_visible())
            #z.show()
            #display(z)
            #display(z.figure)

