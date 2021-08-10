from ipywidgets import VBox, Layout, Label

class PlotMeasure():
    def __init__(self, model):
        self.model = model
        self.cache_information_title = Label(value='Cache informaion:')
        self.cache_lines = Label(value='Number of cache lines: ' + str(self.model.curr_trace.cache_lines) + ' lines')
        self.cache_blocks = Label(value='Size of cache block: ' + str(self.model.curr_trace.cache_block) + ' bytes')
        self.cache_size = Label(value='Total cache size: ' + str(self.model.curr_trace.cache_lines * self.model.curr_trace.cache_block) + ' bytes')
        self.cache_information = VBox(
                           [self.cache_information_title, self.cache_lines, self.cache_blocks, self.cache_size],
                           layout=Layout(width='250px', padding="5px")
                           )

        self.curr_selected_title = Label(value='Current selected area:')

        self.selected_area_size = Label(value='Selected area size: Loading...')
        self.unique_cache_lines = Label(value='Number of unique cache lines: Loading...')
        self.accesses = Label(value='Number of accesses: Loading...')
        self.curr_selected = VBox(
                          [self.curr_selected_title, self.selected_area_size, self.unique_cache_lines, self.accesses],
                          layout=Layout(width='250px', padding="5px")
                          )

        self.widgets = VBox([self.cache_information, self.curr_selected])
    
    def update(self, selected_area_size, unique_cache_lines, accesses, init=False):

        if(init):
            self.selected_area_size.value = 'Selected area size: ' + str(selected_area_size) + ' bytes'
            self.unique_cache_lines.value = 'Number of unique cache lines: ' + str(unique_cache_lines) + ' lines'
            self.accesses.value = 'Number of accesses: ' + str(accesses) + ' accesses'

        self.selected_area_size.value = 'Selected area size: ' + str(selected_area_size) + ' bytes'
        self.unique_cache_lines.value = 'Number of unique cache lines: ' + str(unique_cache_lines) + ' lines'
        self.accesses.value = 'Number of accesses: ' + str(accesses) + ' accesses'


    