from ipywidgets import VBox, Layout, Label
from moneta.settings import STATS_HITS, STATS_CAP_MISS, STATS_COMP_MISS, INDEX, ADDRESS, READ_HIT, WRITE_HIT, READ_MISS, WRITE_MISS, COMP_R_MISS, COMP_W_MISS
from moneta.utils import stats_string

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
        total_count, hit_count, cap_miss_count, comp_miss_count = self.get_curr_stats()

        if(init):
            self.total_hits.value = stats_string(STATS_HITS, hit_count, total_count)
            self.total_cap_misses.value = stats_string(STATS_CAP_MISS, cap_miss_count, total_count)
            self.total_comp_misses.value = stats_string(STATS_COMP_MISS, comp_miss_count, total_count)

        self.curr_hits.value = stats_string(STATS_HITS, hit_count, total_count)
        self.curr_cap_misses.value = stats_string(STATS_CAP_MISS, cap_miss_count, total_count)
        self.curr_comp_misses.value = stats_string(STATS_COMP_MISS, comp_miss_count, total_count)

    def get_curr_stats(self):
        plot = self.model.plot
        selection = self.model.legend.get_select_string()
        df = plot.dataset
        
        x_min = f'({INDEX} >= {int(plot.limits[0][0])})'
        x_max = f'({INDEX} <= {int(plot.limits[0][1])})'
        y_min = f'({ADDRESS} >= {int(plot.limits[1][0])})'
        y_max = f'({ADDRESS} <= {int(plot.limits[1][1])})'

        # Inner df returns an expression, doesn't actually create the new dataframe
        selection += " &" if selection else ""
        df = df[df[f'{selection} {x_min} & {x_max} & {y_min} & {y_max}']]
        
        # Limit min/max is min/max value of Access enum, shape is number of types of access
        stats = df.count(binby=['Access'], limits=[1,7], shape=6)
        
        hit_count = stats[READ_HIT - 1] + stats[WRITE_HIT - 1]
        cap_miss_count = stats[READ_MISS - 1] + stats[WRITE_MISS - 1]
        comp_miss_count = stats[COMP_R_MISS - 1] + stats[COMP_W_MISS - 1]
        total_count = hit_count + cap_miss_count + comp_miss_count

        return total_count, hit_count, cap_miss_count, comp_miss_count