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

def calculate_bounds(model, bounds, dim):
    
    if isinstance(bounds, str):
        bounds = [bounds]

    if all(map(lambda x: isinstance(x,str), bounds)):  # we handle lists of strings.
        tags = []
        for tag in bounds:
            t = model.curr_trace.get_tag(tag)
            if t is None:
                print(f'{WARNING_LABEL} Tag for zoom_access not found...using default')
                print(f'Avaliable tags are: ')
                print("\n".join(model.curr_trace.get_tag_names()))
                return None
            
            tags.append(t)

        lb = min(map(lambda x:int(getattr(x, dim)[0]), tags))
        ub = max(map(lambda x:int(getattr(x, dim)[1]), tags))
        return (lb, ub)
    else: # everything else will fail elsewhere if it's not valid.
        return bounds
        
def parse_zoom_args(model, zoom_access, zoom_address):

    zoom_access = calculate_bounds(model, zoom_access, "access")
    if not valid_bounds(zoom_access):
        return None
    
    zoom_address = calculate_bounds(model, zoom_address, "address")
    if not valid_bounds(zoom_address):
        return None

    return [tuple(zoom_access), tuple(zoom_address)]
