from ipywidgets import VBox, Layout, Label
from moneta.utils import (
    get_curr_stats,
    stats_percent,
    stats_hit_string,
    stats_cap_miss_string,
    stats_comp_miss_string
)

class PlotStats():
    def __init__(self, model):
        self.model = model
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

        self.widgets = VBox([self.total_stats, self.curr_stats])

    def update(self, init=False):
        print("udpate")
        total_count, hit_count, cap_miss_count, comp_miss_count = get_curr_stats(self.model.plot, self.model.legend.get_select_string())

        if(init):
            self.total_hits.value = stats_hit_string(hit_count, total_count)
            self.total_cap_misses.value = stats_cap_miss_string(cap_miss_count, total_count)
            self.total_comp_misses.value = stats_comp_miss_string(comp_miss_count, total_count)

        self.curr_hits.value = stats_hit_string(hit_count, total_count)
        self.curr_cap_misses.value = stats_cap_miss_string(cap_miss_count, total_count)
        self.curr_comp_misses.value = stats_comp_miss_string(comp_miss_count, total_count)
