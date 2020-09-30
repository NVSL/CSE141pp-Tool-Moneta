from moneta.settings import NO_TAGS, INDEX, ADDRESS, LO_ADDR, HI_ADDR, F_ACC, L_ACC, TAG_NAME
import numpy as np
import vaex
import csv

import logging
log = logging.getLogger(__name__)

class Tag():
    def __init__(self, tag_dict):
        self.address = (tag_dict[LO_ADDR], tag_dict[HI_ADDR])
        self.access = (tag_dict[F_ACC], tag_dict[L_ACC])
        self.name = tag_dict[TAG_NAME]

class Trace():
    def __init__(self, name, trace_path, tag_path, meta_path):
        log.info("__init__")
        self.name = name
        self.trace_path = trace_path
        self.tag_path = tag_path
        self.meta_path = meta_path

        self.err_message = None
        self.retrieve_tags()
        if len(self.tags) == 0:
            self.err_message = NO_TAGS
            return
        self.init_df()
        self.retrieve_cache_info()
        self.legend_state = None


    def retrieve_tags(self):
        self.tags = []
        try:
            with open(self.tag_path) as f:
                rows = csv.DictReader(f)
                for row in rows:
                    self.tags.append(Tag(row))
        except:
            pass

    def retrieve_cache_info(self):
        with open(self.meta_path) as f:
            lines = f.readlines()
            lines_split = lines[0].split()
        self.cache_lines = int(lines_split[0])
        self.cache_block = int(lines_split[1])

    def init_df(self):
        self.df = vaex.open(self.trace_path)
        num_accs = self.df[ADDRESS].count()
        self.df[INDEX] = np.arange(0, num_accs)
        self.x_lim = [self.df[INDEX].min()[()], self.df[INDEX].max()[()] + 1]
        self.y_lim = [self.df[ADDRESS].min()[()], self.df[ADDRESS].max()[()]+1]

