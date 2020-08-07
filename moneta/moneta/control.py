from .imports import *
from matplotlib.colors import to_hex, to_rgba

cb_lyt=Layout(width='150px')
cp_lyt=Layout(width='30px')

newc = np.ones((11, 4))
newc[1] = [0, 0, 1, 1] # read_hits - 1, .125
#newc[2] = [0, 0.7, 0, 1] # write_hits - 2, .25
#newc[2] = [0, 1, 1, 1] # write_hits - 2, .25
newc[2] = [0, 153/255, 204/255, 1] # write_hits - 2, .25
newc[3] = [0.047, 1, 0, 1] # cache_size
#newc[4] = [1, 1, 0, 1] # read_misses - 3, .375
newc[4] = [1, .5, 0, 1] # read_misses - 3, .375
#newc[5] = [1, 0, 0.2, 1] # write_misses - 4, .5
newc[5] = [1, 0, 0, 1] # write_misses - 4, .5
#newc[6] = [0.737, 0.745, 0.235, 1] # compulsory read misses - 5, .625
newc[6] = [0.5, 0.3, 0.1, 1] # compulsory read misses - 5, .625
newc[8] = [0.745, 0.309, 0.235, 1] # compulsory write misses - 6, .75
custom_cmap = ListedColormap(newc)

# Custom checkbox for Read/Writes
def RWCheckbox(description, primary_color, secondary_color):
    cp_read = ColorPicker(concise=True, value=to_hex(primary_color[0:3]), disabled=not COLORPALETTE_EDITABLE,layout=cp_lyt)
    cp_write = ColorPicker(concise=True, value=to_hex(secondary_color[0:3]), disabled=not COLORPALETTE_EDITABLE,layout=cp_lyt)
    cp_read.name= "Read " + description
    cp_write.name= "Write " + description
    return HBox([Checkbox(description=description, value=True, disabled=False, indent=False,layout=cb_lyt),
                cp_read, cp_write])

# Custom checkbox for Cache
def CacheLabel(description, color_value):
    cp_cache = ColorPicker(concise=True, value=to_hex(color_value[0:3]), disabled=not COLORPALETTE_EDITABLE,layout=cp_lyt)
    cp_cache.name=description
    #return HBox([Checkbox(description=description, value=True, disabled=False, indent=False,layout=cb_lyt),
    return HBox([Label(value=description,layout=Layout(width='150px')),cp_cache])

class MonetaLegend():
    def __init__(self,readCount, writeCount, hitCount, missCount, compMissCount, m_split, namesFromFile, tagsFromFile, tag_path, numTags):
        self.namesFromFile = namesFromFile
        self.tagsFromFile = tagsFromFile
        self.tag_path = tag_path
        self.accesses = AccessTypeLegend(readCount, writeCount, hitCount, missCount, compMissCount, m_split)
        self.structures = DataStructureLegend(self.namesFromFile,self.tag_path, numTags, tagsFromFile)
        self.statistics = StatisticsLegend()

        self.widget = VBox([self.accesses.widget, self.structures.widget])
    def show(self):
        return self.widget
    def link_plot(self, plot):
        self.accesses.link_plot(plot)
        self.structures.link_plot(plot)
        self.statistics.link_plot(plot)

class AccessTypeLegend():
    def __init__(self,readCount, writeCount, hitCount, missCount, compMissCount, m_split):
        self.legendLabel = HBox([Label(value='Legend',layout=cb_lyt), Label(value='R',layout=cp_lyt), Label(value='W',layout=cp_lyt)])
        self.rwChecks2 = [Checkbox(description="Reads ("+str(readCount)+")",  value=True, disabled=False, indent=False,layout=Layout(width='270px')),
                    Checkbox(description="Writes ("+str(writeCount)+")",  value=True, disabled=False, indent=False,layout=Layout(width='270px'))]
        self.hmChecks2 = [RWCheckbox(description="Hits ("+str(hitCount)+")", primary_color=newc[1], secondary_color=newc[2]),
                    RWCheckbox(description="Capacity Misses ("+str(missCount)+")", primary_color=newc[4], secondary_color=newc[5]),
                    RWCheckbox(description="Compulsory Misses ("+str(compMissCount)+")", primary_color=newc[6], secondary_color=newc[8])]
        self.cacheChecks2 = [CacheLabel(description="Cache ("+str(int(m_split[0]) * int(m_split[1]))+" bytes)", color_value=newc[3])]
        self.checks2 = VBox(children=[self.legendLabel] + self.hmChecks2 +  self.rwChecks2 + self.cacheChecks2,
                            layout=Layout(padding='10px',border='1px solid black'))
        self.widget = self.checks2
    def link_plot(self, plot):
        self.plot = plot
        
        def combineSelections():
            self.plot.df.select("structures", mode='replace', name='total')
            self.plot.df.select("rw", mode='and', name='total')
            self.plot.df.select("hm", mode='and', name='total')
        
        def updateReadWrite2(change):
            if(change.name == 'value'):
                
                name = change.owner.description
                
                if(re.search('^Reads', name)):
                    targetHit = READ_HIT
                    targetMiss = READ_MISS
                    targetCMiss = COMP_R_MISS
                else:
                    targetHit = WRITE_HIT
                    targetMiss = WRITE_MISS
                    targetCMiss = COMP_W_MISS
                
                if(change.new == True):
                    self.plot.df.select(self.plot.df.Access == targetHit, mode='or', name='rw')
                    self.plot.df.select(self.plot.df.Access == targetMiss, mode='or', name='rw')
                    self.plot.df.select(self.plot.df.Access == targetCMiss, mode='or', name='rw')
                    combineSelections()
                else:
                    self.plot.df.select(self.plot.df.Access == targetHit, mode='subtract', name='rw')
                    self.plot.df.select(self.plot.df.Access == targetMiss, mode='subtract', name='rw')
                    self.plot.df.select(self.plot.df.Access == targetCMiss, mode='subtract', name='rw')
                    combineSelections()
            self.plot.df.select('total')  
                
        def updateHitMiss2(change):
            if(change.name == 'value'):
                
                name = change.owner.description
                
                if(re.search('^Hits', name)):
                    targetRead = READ_HIT
                    targetWrite = WRITE_HIT
                elif(re.search('^Capacity', name)):
                    targetRead = READ_MISS
                    targetWrite = WRITE_MISS
                else:
                    targetRead = COMP_R_MISS
                    targetWrite = COMP_W_MISS
                
                if(change.new == True):
                    self.plot.df.select(self.plot.df.Access == targetRead, mode='or', name='hm')
                    self.plot.df.select(self.plot.df.Access == targetWrite, mode='or', name='hm')
                    combineSelections()
                else:
                    self.plot.df.select(self.plot.df.Access == targetRead, mode='subtract', name='hm')
                    self.plot.df.select(self.plot.df.Access == targetWrite, mode='subtract', name='hm')
                    combineSelections()
            self.plot.df.select('total')  
        
        def updateColorMap(change):
            if(change.name=='value'):
                newcmap = np.copy(self.plot.plot.colormap.colors)
                name=change.owner.name
                if(re.search('^Read Hits', name)):
                    newcmap[1] = to_rgba(change.new,1)
                if(re.search('^Write Hits', name)):
                    newcmap[2] = to_rgba(change.new,1)
                if(re.search('^Cache', name)):
                    newcmap[3] = to_rgba(change.new,1)
                if(re.search('^Read Capacity', name)):
                    newcmap[4] = to_rgba(change.new,1)
                if(re.search('^Write Capacity', name)):
                    newcmap[5] = to_rgba(change.new,1)
                if(re.search('^Read Compulsory Miss', name)):
                    newcmap[6] = to_rgba(change.new,1)
                if(re.search('^Write Compulsory Miss', name)):
                    newcmap[8] = to_rgba(change.new,1)
                self.plot.plot.colormap = ListedColormap(newcmap)
                self.plot.plot.backend.plot._update_image()

        for check in self.rwChecks2:
            check.observe(updateReadWrite2)
        for check in [hbox.children[0] for hbox in self.hmChecks2]:
            check.observe(updateHitMiss2)
        for colorpicker in [hbox.children[1] for hbox in self.hmChecks2] + [hbox.children[2] for hbox in self.hmChecks2] + [hbox.children[1] for hbox in self.cacheChecks2]:
            colorpicker.observe(updateColorMap)

class DataStructureLegend():
    def __init__(self,namesFromFile,tag_path,numTags,tagsFromFile):
        self.namesFromFile = namesFromFile
        self.tagsFromFile = tagsFromFile
        self.tag_path = tag_path
        self.numTags = numTags
        # Data Structures
        self.tagChecks = []
        tagChecksBox = []
        if self.tag_path:
            self.tagChecks = [HBox([
                            Checkbox(description=name, 
                                            value=True, 
                                            disabled=False, 
                                            indent=False,
                                            layout=Layout(width='150px')),
                            Button(
                                    icon='search-plus',
                                    tooltip=name,
                                    layout=Layout(height='35px', 
                                                width='35px', 
                                                border='none',
                                                align_items='center'
                                                ),
                                            style={'button_color': 'transparent'}
                                    )
                            ],layout=Layout(min_height='35px'))

                        for name in self.namesFromFile]
        tagChecksBox = [Label(value='Data Structures'), VBox(self.tagChecks, 
            layout=Layout(max_height='210px', overflow_y = 'auto'))]
        self.widget = VBox(tagChecksBox)
    def link_plot(self, plot):
        self.plot = plot
        
        #Handle all boolean combinations of independent checkboxes here
        def combineSelections():
            self.plot.df.select("structures", mode='replace', name='total')
            self.plot.df.select("rw", mode='and', name='total')
            self.plot.df.select("hm", mode='and', name='total')

        def updateGraph(change):
            if(change.name == 'value'):

                name = change.owner.description
                tag = self.tagsFromFile[self.namesFromFile.index(name)]

                if(change.new == True):
                    self.plot.df.select(self.plot.df.Tag == tag, mode='or', name='structures')
                    combineSelections()
                else:
                    self.plot.df.select(self.plot.df.Tag == tag, mode='subtract', name='structures')
                    combineSelections()
            self.plot.df.select('total')

        if self.tag_path:
            for i in range(self.numTags):
                self.tagChecks[i].children[0].observe(updateGraph)
                self.tagChecks[i].children[1].on_click(self.plot.plot.backend.zoomSection)

class StatisticsLegend():
    def __init__(self):
        # TODO
        pass
    def link_plot(self, plot):
        # TODO
        self.plot = plot