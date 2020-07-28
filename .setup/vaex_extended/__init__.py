from vaex import *
import vaex.jupyter.plot

# Alternate: Overwrite existing backend
# vaex.jupyter.plot.backends['bqplot'] = ('vaex_extended.jupyter.bqplot','BqplotBackend')

# Added additonal backend
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot','BqplotBackend')
vaex_cache_size = 4096*64


from vaex_extended.jupyter.plot import Plot2dDefault as custom_plot1
vaex.jupyter.plot.type_map['custom_plot1'] = custom_plot1

