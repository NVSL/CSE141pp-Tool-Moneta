from IPython.display import clear_output, display

def percent_string(count, total):
    return 'N/A' if total == 0 else f'{count/total:06.2%}'

def stats_string(label, count, total):
    return f'{label}: {count} ({percent_string(count, total)})'

def handle_load_trace(file_chooser, model):
    model.ready_next_trace()
    clear_output(wait=True)
    display(file_chooser)

    path = file_chooser.selected_path
    trace_name = file_chooser.selected_filename
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