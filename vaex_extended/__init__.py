from vaex import *

# Alternate: Overwrite existing backend
# vaex.jupyter.plot.backends['bqplot'] = ('vaex_extended.jupyter.bqplot','BqplotBackend')

# Added additonal backend
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot','BqplotBackend')

