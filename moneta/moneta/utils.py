from moneta.settings import ERROR_LABEL

def percent_string(count, total):
    return 'N/A' if total == 0 else f'{count/total:06.2%}'

def stats_string(label, count, total):
    return f'{label}: {count} ({percent_string(count, total)})'
    
def validate_zoom_args(zoom):
    err_message = f'{ERROR_LABEL} Invalid Zoom Format'

    if len(zoom) != 2:
        return err_message

    x_zoom = zoom[0]
    y_zoom = zoom[1]

    if len(x_zoom) != 2 or len(y_zoom) != 2:
        return err_message

    type_check = all([isinstance(i, int) or isinstance(i, float) for i in [*x_zoom, *y_zoom]])

    if not type_check:
        return err_message

    if x_zoom[0] >= x_zoom[1] or y_zoom[0] >= y_zoom[1]:
        return err_message
        
    return ''
