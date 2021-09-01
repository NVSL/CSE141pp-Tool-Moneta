from moneta.settings import WARNING_LABEL

def percent_string(count, total):
    return 'N/A' if total == 0 else f'{count/total:06.2%}'

def stats_string(label, count, total):
    return f'{label}: {count} ({percent_string(count, total)})'
 

def valid_bounds(bound):
    if len(bound) != 2:
        return False

    if not all([isinstance(i, int) or isinstance(i, float) for i in bound]):
        return False

    if bound[0] >= bound[1]:
        return False

    return True

def parse_zoom_args(model, zoom_access, zoom_address):

    initial_zoom = model.curr_trace.get_initial_zoom()

    if isinstance(zoom_access, str):
        tag = model.curr_trace.get_tag(zoom_access)

        if not tag:
            print(f'{WARNING_LABEL} Tag for zoom_access not found...using default zoom_access')
            print(f'Avaliable tags are: ')
            print("\n".join(model.curr_trace.get_tag_names()))
            
            bound_access = initial_zoom[0]
        else:
            bound_access = [int(i) for i in tag.access]

    else:
        if not valid_bounds(zoom_access):
            return None
            
        bound_access = zoom_access



    if isinstance(zoom_address, str):
        tag = model.curr_trace.get_tag(zoom_address)

        if not tag:
            print(f'{WARNING_LABEL} Tag for zoom_address not found...using default zoom_address')    
            bound_address = initial_zoom[1]
        else:
            bound_address = [int(i) for i in tag.address]

    else:
        if not valid_bounds(zoom_address):
            return None
            
        bound_address = zoom_address


    return [tuple(bound_access), tuple(bound_address)]
