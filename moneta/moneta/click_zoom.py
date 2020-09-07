from ipywidgets import Output
from moneta.settings import INDEX_LABEL, ADDRESS_LABEL, CUSTOM_CMAP
import numpy as np
import vaex
class ClickZoom():
    def __init__(self):
        print("Click zoom init")
        self.widget = Output()
        df = vaex.open('.output/full_trace_iter_fib.hdf5')
        df.rename_column('Address', ADDRESS_LABEL)
        num_accs = df[ADDRESS_LABEL].count()
        df[INDEX_LABEL] = np.arange(0, num_accs)
        x_lim = [df[INDEX_LABEL].min()[()], df[INDEX_LABEL].max()[()]]
        y_lim = [df[ADDRESS_LABEL].min()[()], df[ADDRESS_LABEL].max()[()]]
        with self.widget:
            #df.plot(df[INDEX_LABEL], df[ADDRESS_LABEL], what='max(Access)', colormap = CUSTOM_CMAP, selection=[True], limits=[x_lim, y_lim])
            df.plot(df[INDEX_LABEL], df[ADDRESS_LABEL], colormap = CUSTOM_CMAP, what='max(Access)', limits=[x_lim, y_lim], shape=512, colorbar=False, figsize=(10,10))

