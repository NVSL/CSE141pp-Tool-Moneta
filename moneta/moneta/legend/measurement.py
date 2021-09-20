from ipywidgets import VBox, Layout, Label
from moneta.settings import STATS_HITS, STATS_CAP_MISS, STATS_COMP_MISS, INDEX, ADDRESS, READ_HIT, WRITE_HIT, READ_MISS, WRITE_MISS, COMP_R_MISS, COMP_W_MISS
from moneta.utils import stats_string

class PlotMeasure():
    def __init__(self, model):
        self.model = model
        self.cache_info_title = Label(value='Cache Information:')
        cacheInfo = str(self.model.curr_trace.cache_block) + '-byte Block, ' + str(self.model.curr_trace.cache_lines) + ' Lines, Total size ' + str(self.model.curr_trace.cache_lines * self.model.curr_trace.cache_block) + ' bytes'
        self.cache_info = Label(value= cacheInfo)
        self.cache_information = VBox(
                           [self.cache_info_title, self.cache_info],
                           layout=Layout(width='300px', padding="5px")
                           )

        self.curr_selected_title = Label(value='Current Selected Area:')

        self.selected_area_size = Label(value='Selected area size: Loading...')
        self.unique_cache_lines = Label(value='Number of unique cache lines: Loading...')
        self.accesses = Label(value='Number of accesses: Loading...')
        self.curr_selected = VBox(
                          [self.curr_selected_title, self.selected_area_size, self.unique_cache_lines, self.accesses],
                          layout=Layout(width='300px', padding="5px")
                          )

        self.curr_stat_title = Label(value='Current Selected Stats:')

        self.curr_hits = Label(value='Hits: Loading...')
        self.curr_cap_misses = Label(value='Cap. Misses: Loading...')
        self.curr_comp_misses = Label(value='Comp. Misses: Loading...')
        self.curr_stats = VBox(
                          [self.curr_stat_title, self.curr_hits, self.curr_cap_misses, self.curr_comp_misses],
                          layout=Layout(width='250px', padding="5px")
                          )

        self.widgets = VBox([self.cache_information, self.curr_selected, self.curr_stats])
    
    def update(self, selected_area_size, unique_cache_lines, accesses, df, init=False):
        total_count, hit_count, cap_miss_count, comp_miss_count = self.get_curr_stats(df)

        if(init):
            self.total_hits.value = stats_string(STATS_HITS, hit_count, total_count)
            self.total_cap_misses.value = stats_string(STATS_CAP_MISS, cap_miss_count, total_count)
            self.total_comp_misses.value = stats_string(STATS_COMP_MISS, comp_miss_count, total_count)

        self.curr_hits.value = stats_string(STATS_HITS, hit_count, total_count)
        self.curr_cap_misses.value = stats_string(STATS_CAP_MISS, cap_miss_count, total_count)
        self.curr_comp_misses.value = stats_string(STATS_COMP_MISS, comp_miss_count, total_count)

        if(init):
            self.selected_area_size.value = 'Selected area size: ' + str(selected_area_size) + ' bytes'
            self.unique_cache_lines.value = 'Number of unique cache lines: ' + str(unique_cache_lines) + ' lines'
            self.accesses.value = 'Number of accesses: ' + str(accesses) + ' accesses'

        self.selected_area_size.value = 'Selected area size: ' + str(selected_area_size) + ' bytes'
        self.unique_cache_lines.value = 'Number of unique cache lines: ' + str(unique_cache_lines) + ' lines'
        self.accesses.value = 'Number of accesses: ' + str(accesses) + ' accesses'

    def get_curr_stats(self, df):
        # Limit min/max is min/max value of Access enum, shape is number of types of access
        stats = df.count(binby=['Access'], limits=[1,7], shape=6)
        
        hit_count = stats[READ_HIT - 1] + stats[WRITE_HIT - 1]
        cap_miss_count = stats[READ_MISS - 1] + stats[WRITE_MISS - 1]
        comp_miss_count = stats[COMP_R_MISS - 1] + stats[COMP_W_MISS - 1]
        total_count = hit_count + cap_miss_count + comp_miss_count

        return total_count, hit_count, cap_miss_count, comp_miss_count


    