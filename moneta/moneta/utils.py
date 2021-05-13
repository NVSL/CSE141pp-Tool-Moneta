import math

def percent_string(count, total):
    return 'N/A' if total == 0 else f'{count/total:06.2%}'

def stats_string(label, count, total = None):
    return f'{label}: {count}' + (f'({percent_string(count, total)})' if total else "")

def compute_working_set(df, cache_line_size=64):
    bits = int(math.log(cache_line_size, 2))
    working_set = df['Address'].unique()
    shifted  = map(lambda x: x >> bits, working_set)
    count = len(set(shifted))
    bytes = count * cache_line_size
    return count, bytes
    

def mem_accessed_stats(bytes, lines, total_lines):
    return f'{bytes/1024.}KB, {lines} of {total_lines} lines {lines/(total_lines+0.0)*100.0:2}%\n'
