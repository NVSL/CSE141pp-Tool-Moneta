import math

def percent_string(count, total):
    return 'N/A' if total == 0 else f'{count/total:06.2%}'

def stats_string(label, count, total = None):
    return f'{label}: {count}' + (f'({percent_string(count, total)})' if total else "")


def mem_accessed_stats(bytes, lines, total_lines):
    return f'{bytes/1024.}KB, {lines} of {total_lines} lines {lines/(total_lines+0.0)*100.0:2}%\n'
