from moneta.settings import NO_TAGS, INDEX, ADDRESS, LO_ADDR, HI_ADDR, F_ACC, L_ACC, TAG_NAME, ERROR_LABEL, TAG_FILE_THREAD_ID, TAG_FILE_TAG_TYPE, THREAD_ID
import numpy as np
import vaex
import csv
import os

import logging
log = logging.getLogger(__name__)

TAG_TYPE_SPACETIME = "space-time"
TAG_TYPE_THREAD = "thread"
class Tag():
    def __init__(self, tag_dict):
        self.address = (tag_dict[LO_ADDR], tag_dict[HI_ADDR])
        self.access = (tag_dict[F_ACC], tag_dict[L_ACC])
        self.name = tag_dict[TAG_NAME]
        self.thread_id = int(tag_dict.get(TAG_FILE_THREAD_ID, "0"))
        self.tag_type = tag_dict.get(TAG_FILE_TAG_TYPE, TAG_TYPE_SPACETIME)

    def is_thread(self):
        return self.tag_type == TAG_TYPE_THREAD

    @classmethod
    def create(cls, tag_dict):
        tag_type = tag_dict.get(TAG_FILE_TAG_TYPE, TAG_TYPE_SPACETIME)
        tag_type_map = {
            TAG_TYPE_SPACETIME: SpaceTimeTag,
            TAG_TYPE_THREAD: ThreadTag
            }
        return tag_type_map[tag_type](tag_dict)
    
class ThreadTag(Tag):
    def __init__(self, tag_dict):
        super(ThreadTag, self).__init__(tag_dict)

    def query_string(self):
        return f'({THREAD_ID} == {self.thread_id})'

    def display_name(self):
        return f"Thread {self.thread_id}"

class SpaceTimeTag(Tag):
    def __init__(self, tag_dict):
        super(SpaceTimeTag, self).__init__(tag_dict)

    def query_string(self):
        return (f"({ADDRESS} >= {self.address[0]}) & ({ADDRESS} <= {self.address[1]}) &" +
                f"({INDEX} >= {self.access[0]}) & ({INDEX} <= {self.access[1]})")

    def display_name(self):
        return self.name
    
class Trace():
    def __init__(self, name, trace_path, tag_path, meta_path):
        self.name = name
        self.trace_path = trace_path
        self.tag_path = tag_path
        self.meta_path = meta_path

        self.err_message = None

        path_err = self.validate_paths()
        if path_err:
            self.err_message = path_err
            return

        self.retrieve_tags()
        if len(self.tags) == 0:
            self.err_message = NO_TAGS
            return

        self.init_df()
        self.retrieve_meta_data()
        self.legend_state = None

    def retrieve_tags(self):
        self.tags = []
        with open(self.tag_path) as f:
            rows = csv.DictReader(f)
            for row in rows:
                log.debug(f"found tag '{row['Tag_Name']}': {row}")
                self.tags.append(Tag.create(row))
                
    def retrieve_meta_data(self):
        with open(self.meta_path) as f:
            lines = f.readlines()
            lines_split = lines[0].split()
        self.cache_lines = int(lines_split[0])
        self.cache_block = int(lines_split[1])
        log.debug(f"cache_lines = {self.cache_lines}")
        log.debug(f"cache_block = {self.cache_block}")
        if len(lines) > 1:
            self.threads = map(int,lines[1].split())
        else:
            self.threads = [0]
        log.debug(f"threads: {self.threads}")
            
    def init_df(self):
        self.df = vaex.open(self.trace_path)
        self.x_lim = [self.df[INDEX].min()[()], self.df[INDEX].max()[()] + 1]
        self.y_lim = [self.df[ADDRESS].min()[()], self.df[ADDRESS].max()[()]+1]

    def get_tag_names(self):
        return [t.name for t in self.tags]
    
    def get_tag(self, name):
        for tag in self.tags:
            if tag.name == name:
                return tag

        return None

    def get_initial_zoom(self):
        return [self.x_lim, self.y_lim]

    def validate_paths(self):
        for path in [self.trace_path, self.tag_path, self.meta_path]:
            if not os.path.exists(path):
                return f'{ERROR_LABEL} {path} could not be found!\n'
                
