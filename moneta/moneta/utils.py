def percent_string(count, total):
    return 'N/A' if total == 0 else f'{count/total:06.2%}'

def stats_string(label, count, total):
    return f'{label}: {count} ({percent_string(count, total)})'
