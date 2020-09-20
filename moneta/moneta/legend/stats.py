from ipywidgets import VBox, Layout, Label

class PlotStats():
    def __init__(self):
        self.total_stat_title = Label(value='Total Stats:')
        self.total_hits = Label(value='Hits: Loading...')
        self.total_cap_misses = Label(value='Cap. Misses: Loading...')
        self.total_comp_misses = Label(value='Comp. Misses: Loading...')
        self.total_stats = VBox(
                           [self.total_stat_title, self.total_hits, self.total_cap_misses, self.total_comp_misses],
                           layout=Layout(width='250px', padding="5px")
                           )

        self.curr_stat_title = Label(value='Current View Stats:')

        self.curr_hits = Label(value='Hits: Loading...')
        self.curr_cap_misses = Label(value='Cap. Misses: Loading...')
        self.curr_comp_misses = Label(value='Comp. Misses: Loading...')
        self.curr_stats = VBox(
                          [self.curr_stat_title, self.curr_hits, self.curr_cap_misses, self.curr_comp_misses],
                          layout=Layout(width='250px', padding="5px")
                          )

        self.widget = VBox([self.total_stats, self.curr_stats])