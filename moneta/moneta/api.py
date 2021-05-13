from IPython.display import clear_output
from moneta import Moneta

def load_trace(path, trace_name):
    model = Moneta()
    model.ready_next_trace()
    clear_output(wait=True)

    print(f'Loading {trace_name}\n')

    err_message = model.load_trace(path, trace_name)

    if err_message is not None:
        print(err_message)
        return

    model.create_plot()

    if model.plot is None:
        print("Couldn't load plot")
        return

    model.plot.show()
    model.legend.stats.update(init=True)



