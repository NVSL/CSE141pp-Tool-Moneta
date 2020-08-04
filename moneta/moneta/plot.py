from .imports import *
from . import control

sys.path.append('../.setup/')

import vaex_extended
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot', 'BqplotBackend')

# Custom colormap
newc = np.ones((11, 4))

'''newc[1] = [0, 0.5, 0, 1] # read_hits - 1, .125
#newc[2] = [0, 0.7, 0, 1] # write_hits - 2, .25
newc[2] = [0, 0.5, 0, 1] # write_hits - 2, .25
newc[3] = [0, 0, 0, 1] # cache_size
newc[4] = [1, 0.5, 0, 1] # read_misses - 3, .375
#newc[5] = [1, 0, 0.2, 1] # write_misses - 4, .5
newc[5] = [1, 0.5, 0, 1] # write_misses - 4, .5
newc[6] = [0.235, 0.350, 0.745, 1] # compulsory read misses - 5, .625
newc[8] = [0.235, 0.350, 0.745, 1] # compulsory write misses - 6, .75'''

# Original colors below
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

class MonetaPlot():
  def __init__(self, trace_path, tag_path, meta_path, trace_name):
    self.widget = self.generate_plot(trace_path, tag_path, meta_path, trace_name)
  
  def show(self):
    display(self.widget)

  def generate_plot(self,trace_path, tag_path, meta_path, trace_name):
    """Plots interactive widget with all other UI controls for user interaction"""
    #global df
    #global self.tag_map
    global curr_trace
    if curr_trace != "":
      refresh()
    curr_trace = trace_name
    logging.info("Generating plot")

    #trace_path, tag_path, meta_path = trace_map[trace_name]
    self.df = vaex.open(trace_path)
    if tag_path:
      logging.debug("Found a tag map file")
      self.tag_map = vaex.open(tag_path)
      if len(self.tag_map.columns['Tag_Name']) == 0:
        print("No tags in file")
        return
    else:
      logging.debug("No tag map -- Full trace")
    num_accesses = self.df.Address.count()
    self.df['index'] = np.arange(0, num_accesses)

    if tag_path:
      #Set up name-tag mapping
      namesFromFile = (self.tag_map.Tag_Name.values).tolist()
      tagsFromFile = (self.tag_map.Tag_Value.values).tolist()
      startIndices = (self.tag_map.First_Access.values).tolist()
      startAddresses = (self.tag_map.Low_Address.values).tolist()
      endIndices = (self.tag_map.Last_Access.values).tolist()
      endAddresses = (self.tag_map.High_Address.values).tolist()
    
      numTags = len(namesFromFile)
      logging.debug("Number of tags: {}".format(numTags))
      logging.debug("Tags: {}".format(namesFromFile))


    # Initialize accessRanges dictionary in bqplot backend with file info
    from vaex_extended.jupyter.bqplot import accessRanges
    accessRanges.clear()
    if tag_path:
      for i in range(numTags):
        name = namesFromFile[i]
        accessRanges.update({name : {}})
    
        rangeData = accessRanges[name]
        rangeData.update({"startIndex" : startIndices[i]})
        rangeData.update({"endIndex" : endIndices[i]})
        rangeData.update({"startAddr" : startAddresses[i]})
        rangeData.update({"endAddr" : endAddresses[i]})

    #Define all selections here
    self.df.select(True, name='structures')
    self.df.select(True, name='rw')
    self.df.select(True, name='hm')
    self.df.select(True, name='total')

    #Initialize counts
    read_hits = self.df[self.df.Access == READ_HIT]
    write_hits = self.df[self.df.Access == WRITE_HIT]
    read_misses = self.df[self.df.Access == READ_MISS]
    write_misses = self.df[self.df.Access == WRITE_MISS]
    comp_read_misses = self.df[self.df.Access == COMP_R_MISS]
    comp_write_misses = self.df[self.df.Access == COMP_W_MISS]
    readCount = read_hits.count() + read_misses.count()
    writeCount = write_hits.count() + write_misses.count()
    hitCount = read_hits.count() + write_hits.count()
    missCount = read_misses.count() + write_misses.count()
    compMissCount = comp_read_misses.count() + comp_write_misses.count()

    accessCounts = [readCount, writeCount, hitCount, missCount, compMissCount]

    if tag_path:
      #Initialize selections
      for tag in tagsFromFile:
        self.df.select(self.df.Tag == tag, mode='or')


    """ #Handle all boolean combinations of independent checkboxes here
    def combineSelections():
      self.df.select("structures", mode='replace', name='total')
      self.df.select("rw", mode='and', name='total')
      self.df.select("hm", mode='and', name='total')

    def updateGraph(change):
      if(change.name == 'value'):

        name = change.owner.description
        tag = tagsFromFile[namesFromFile.index(name)]

        if(change.new == True):
          self.df.select(self.df.Tag == tag, mode='or', name='structures')
          combineSelections()
        else:
          self.df.select(self.df.Tag == tag, mode='subtract', name='structures')
          combineSelections()
      self.df.select('total')

    def updateReadWrite(change):
      if(change.name == 'value'):

        name = change.owner.description

        if(name.startswith("Reads")):
          targetHit = READ_HIT
          targetMiss = READ_MISS
          targetCMiss = COMP_R_MISS
        else:
          targetHit = WRITE_HIT
          targetMiss = WRITE_MISS
          targetCMiss = COMP_W_MISS

        if(change.new == True):
          self.df.select(self.df.Access == targetHit, mode='or', name='rw')
          self.df.select(self.df.Access == targetMiss, mode='or', name='rw')
          self.df.select(self.df.Access == targetCMiss, mode='or', name='rw')
          combineSelections()
          
          currentSelection[targetHit-1] = 1
          currentSelection[targetMiss-1] = 1
          currentSelection[targetCMiss-1] = 1
          
        else:
          self.df.select(self.df.Access == targetHit, mode='subtract', name='rw')
          self.df.select(self.df.Access == targetMiss, mode='subtract', name='rw')
          self.df.select(self.df.Access == targetCMiss, mode='subtract', name='rw')
          combineSelections()
          
          currentSelection[targetHit-1] = 0
          currentSelection[targetMiss-1] = 0
          currentSelection[targetCMiss-1] = 0
          
      self.df.select('total')

    def updateHitMiss(change): 
      if(change.name == 'value'):

        name = change.owner.description

        if(name.startswith("Hits")):
          targetRead = READ_HIT
          targetWrite = WRITE_HIT
        elif(name.startswith("Capacity")):
          targetRead = READ_MISS
          targetWrite = WRITE_MISS
        else:
          targetRead = COMP_R_MISS
          targetWrite = COMP_W_MISS

        if(change.new == True):
          self.df.select(self.df.Access == targetRead, mode='or', name='hm')
          self.df.select(self.df.Access == targetWrite, mode='or', name='hm')
          combineSelections()
          
          currentSelection[targetRead-1] = 1
          currentSelection[targetWrite - 1] = 1
          
        else:
          self.df.select(self.df.Access == targetRead, mode='subtract', name='hm')
          self.df.select(self.df.Access == targetWrite, mode='subtract', name='hm')
          combineSelections()  
          
          currentSelection[targetRead-1] = 0
          currentSelection[targetWrite - 1] = 0
          
      self.df.select('total')
    """
    def getCurrentView(frame):
      curView = frame[frame.index >= int(self.plot.limits[0][0])]
      curView = curView[curView.index <= int(self.plot.limits[0][1])+1]
      curView = curView[curView.Address >= int(self.plot.limits[1][0])]
      curView = curView[curView.Address <= int(self.plot.limits[1][1])+1]
      
      return curView
      
    def updateStats(self):
      curReadHits = getCurrentView(read_hits)
      curWriteHits = getCurrentView(write_hits)
      curReadMisses = getCurrentView(read_misses)
      curWriteMisses = getCurrentView(write_misses)
      curCompReadMisses = getCurrentView(comp_read_misses)
      curCompWriteMisses = getCurrentView(comp_write_misses)
      
      hitCount = curReadHits.count() + curWriteHits.count()
      missCount = curReadMisses.count() + curWriteMisses.count()
      compMissCount = curCompReadMisses.count() + curCompWriteMisses.count()
      totalCount = hitCount + missCount + compMissCount
      
      currentHitRate.value = "Hit Rate: "+f"{hitCount*100/totalCount:.2f}"+"%"
      currentCapMissRate.value = "Capacity Miss Rate: "+f"{missCount*100/totalCount:.2f}"+"%"
      currentCompMissRate.value = "Compulsory Miss Rate: "+f"{compMissCount*100/totalCount:.2f}"+"%"
    
    """ # Data Structures
    tagChecks = []
    tagChecksBox = []
    if tag_path:
      tagChecks = [HBox([
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

                  for name in namesFromFile]
      tagChecksBox = [Label(value='Data Structures'), VBox(tagChecks, 
          layout=Layout(max_height='210px', overflow_y = 'auto'))]

    rwChecks = [Checkbox(description="Reads ("+str(readCount)+")", value=True, disabled=False, indent=False),
                Checkbox(description="Writes ("+str(writeCount)+")", value=True, disabled=False, indent=False)]

    hmChecks = [Checkbox(description="Hits ("+str(hitCount)+")", value=True, disabled=False, indent=False),
                Checkbox(description="Capacity Misses ("+str(missCount)+")", value=True, disabled=False, indent=False),
                Checkbox(description="Compulsory Misses ("+str(compMissCount)+")", value=True, disabled=False, indent=False)] """

    hmRates = [Label(value="Total Trace Stats:", layout=Layout(width='200px')),
              Label(value="Hit Rate: "+f"{hitCount*100/self.df.count():.2f}"+"%"),
              Label(value="Capacity Miss Rate: "+f"{missCount*100/self.df.count():.2f}"+"%"),
              Label(value="Compulsory Miss Rate: "+f"{compMissCount*100/self.df.count():.2f}"+"%")]

    currentHitRate = Label(value="Hit Rate: "+f"{hitCount*100/self.df.count():.2f}"+"%")
    currentCapMissRate = Label(value="Capacity Miss Rate: "+f"{missCount*100/self.df.count():.2f}"+"%")
    currentCompMissRate = Label(value="Compulsory Miss Rate: "+f"{compMissCount*100/self.df.count():.2f}"+"%")
    currentHmRates = [Label(value="Trace Stats for Current View:", layout=Layout(width='200px')),
              currentHitRate, currentCapMissRate, currentCompMissRate]
    
    refreshRatesButton = Button(
            description='Refresh Stats',
            disabled=False,
            button_style='',
            layout= Layout(margin='10px 10px 0px 10px', width='200px', height='40px', border='1px solid black', flex='1'),
            style={'button_color': 'lightgray'},
            )
      
    """if tag_path:
      for i in range(numTags):
        tagChecks[i].children[0].observe(updateGraph)
      
    for check in rwChecks:
      check.observe(updateReadWrite)
      
    for check in hmChecks:
      check.observe(updateHitMiss) """
    
    
    refreshRatesButton.on_click(updateStats)
      
    """ if tag_path:
      checks = VBox([HBox([VBox(tagChecks), VBox(rwChecks), VBox(hmChecks)]), HBox([VBox(hmRates), VBox(currentHmRates), refreshRatesButton])])
    else:
      checks = VBox([HBox([VBox(rwChecks), VBox(hmChecks)]), HBox([VBox(hmRates), VBox(currentHmRates), refreshRatesButton])]) """


    """ def updateReadWrite2(change):
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
                self.df.select(self.df.Access == targetHit, mode='or', name='rw')
                self.df.select(self.df.Access == targetMiss, mode='or', name='rw')
                self.df.select(self.df.Access == targetCMiss, mode='or', name='rw')
                combineSelections()
            else:
                self.df.select(self.df.Access == targetHit, mode='subtract', name='rw')
                self.df.select(self.df.Access == targetMiss, mode='subtract', name='rw')
                self.df.select(self.df.Access == targetCMiss, mode='subtract', name='rw')
                combineSelections()
        self.df.select('total')  
                
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
                self.df.select(self.df.Access == targetRead, mode='or', name='hm')
                self.df.select(self.df.Access == targetWrite, mode='or', name='hm')
                combineSelections()
            else:
                self.df.select(self.df.Access == targetRead, mode='subtract', name='hm')
                self.df.select(self.df.Access == targetWrite, mode='subtract', name='hm')
                combineSelections()
        self.df.select('total')   """
    
    """ from matplotlib.colors import to_rgba
    def updateColorMap(change):
        if(change.name=='value'):
            newcmap = np.copy(self.plot.colormap.colors)
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
            self.plot.colormap = ListedColormap(newcmap)
            self.plot.backend.plot._update_image()
    
    cb_lyt=Layout(width='150px')
    cp_lyt=Layout(width='30px') """
  
    """ # Custom checkbox for Read/Writes
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
 """
    with open(meta_path) as meta_f:
      mlines = meta_f.readlines()
      m_split = mlines[0].split()
      logging.debug("Reading meta data: {}".format(m_split))

    vaex_extended.vaex_cache_size = int(m_split[0])*int(m_split[1])

    """ from matplotlib.colors import to_hex
    legendLabel = HBox([Label(value='Legend',layout=cb_lyt), Label(value='R',layout=cp_lyt), Label(value='W',layout=cp_lyt)])
    rwChecks2 = [Checkbox(description="Reads ("+str(readCount)+")",  value=True, disabled=False, indent=False,layout=Layout(width='270px')),
                Checkbox(description="Writes ("+str(writeCount)+")",  value=True, disabled=False, indent=False,layout=Layout(width='270px'))]
    hmChecks2 = [RWCheckbox(description="Hits ("+str(hitCount)+")", primary_color=newc[1], secondary_color=newc[2]),
                RWCheckbox(description="Capacity Misses ("+str(missCount)+")", primary_color=newc[4], secondary_color=newc[5]),
                RWCheckbox(description="Compulsory Misses ("+str(compMissCount)+")", primary_color=newc[6], secondary_color=newc[8])]
    cacheChecks2 = [CacheLabel(description="Cache ("+str(int(m_split[0]) * int(m_split[1]))+" bytes)", color_value=newc[3])]
    checks2 = VBox([VBox(children=[legendLabel] + hmChecks2 +  rwChecks2 + cacheChecks2 + [VBox(tagChecksBox,layout=Layout())],
                        layout=Layout(padding='10px',border='1px solid black')
                        )])
    for check in rwChecks2:
        check.observe(updateReadWrite2)
    for check in [hbox.children[0] for hbox in hmChecks2]:
        check.observe(updateHitMiss2)
    for colorpicker in [hbox.children[1] for hbox in hmChecks2] + [hbox.children[2] for hbox in hmChecks2] + [hbox.children[1] for hbox in cacheChecks2]:
        colorpicker.observe(updateColorMap) """
    
    #Code for simple_legend
    #import matplotlib.pyplot as plt
    #import ipywidgets as widgets

    #colors = [[0.047, 1, 0, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 0, 1], [1, 0, 0, 1], [0.737, 0.745, 0.235, 1], [0.745, 0.309, 0.235, 1]]
    #f = lambda m,c: plt.plot([],[],marker=m, color=c, ls="none")[0]
    #handles = [f("s", colors[i]) for i in range(7)]
    #labels = ["Cache", "Read Hits", "Write Hits", "Read Misses", "Write Misses", "Compulsory Read Misses", "Compulsory Write Misses"]
    #legend = plt.legend(handles, labels, loc=3, framealpha=1, frameon=True, prop={"size":15})
    #def export_legend(legend, filename="legend.png", expand=[-10,-10,10,10]):
    #  fig  = legend.figure
    #  fig.canvas.draw()
    #  bbox  = legend.get_window_extent()
    #  bbox = bbox.from_extents(*(bbox.extents + np.array(expand)))
    #  bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
    #  fig.savefig(filename, dpi="figure", bbox_inches=bbox)
      
    #simple_legend = widgets.Output()
    #with simple_legend:
    #   export_legend(legend)
    #   plt.gca().set_axis_off()
    #   plt.show()
    
    #replace checks2 with simple_legend to display the simple_legend over current legend

    #legend = VBox([])
    legend = control.MonetaLegend(readCount, writeCount, hitCount, missCount, compMissCount, m_split, namesFromFile, tagsFromFile, tag_path,numTags)

    """ self.plot = self.df.plot_widget(self.df.index, self.df.Address, what='max(Access)',
                  colormap = custom_cmap, selection=[True],
                  backend='bqplot_v2', tool_select=True, legend=checks2, update_stats = updateStats, type='custom_plot1') """

    x_lim = [self.df.index.min()[()], self.df.index.max()[()]]
    y_lim = [self.df.Address.min()[()], self.df.Address.max()[()]]
    self.plot = self.df.plot_widget(self.df.index, self.df.Address, what='max(Access)',
                  colormap = custom_cmap, selection=[True],limits = [x_lim, y_lim],
                  backend='bqplot_v2', tool_select=True, legend=legend.widget, update_stats = updateStats, type='custom_plot1')
    
    legend.link_plot(self)

    """ if tag_path:
      for i in range(numTags):
        tagChecks[i].children[1].on_click(self.plot.backend.zoomSection) """
          
    #display(checks)

    def selectDF(inDF):
      if(currentSelection[READ_MISS-1] == 1):
          inDF.select(inDF.Access == READ_MISS, mode='or')
      if(currentSelection[READ_HIT-1] == 1):
          inDF.select(inDF.Access == READ_HIT, mode='or')
      if(currentSelection[COMP_R_MISS-1] == 1):
          inDF.select(inDF.Access == COMP_R_MISS, mode='or')
      if(currentSelection[WRITE_MISS-1] == 1):
          inDF.select(inDF.Access == WRITE_MISS, mode='or')
      if(currentSelection[WRITE_HIT-1] == 1):
          inDF.select(inDF.Access == WRITE_HIT, mode='or')
      if(currentSelection[COMP_W_MISS-1] == 1):
          inDF.select(inDF.Access == COMP_W_MISS, mode='or')

      # Create a duplicate plot with current limits as the initial state of plot
    def indSubPlot(b):
        dfNew = vaex.from_pandas(self.df)
        #intial selection not functioning, diplays all data from original df
        dfNew.plot_widget(dfNew.index, dfNew.Address, what='max(Access)', colormap = custom_cmap, backend='bqplot_v2', tool_select=True, selection=True, limits=self.plot.limits, type='custom_plot1')
        selectDF(dfNew)

    indSubPlotButton = Button(
            description='Create Independent Subplot',
            disabled=False,
            button_style='',
            layout= Layout(margin='10px 10px 0px 10px', width='200px', height='40px', border='1px solid black', flex='1'),
            style={'button_color': 'lightgray'},
            )
    indSubPlotButton.on_click(indSubPlot)
    display(indSubPlotButton)

    def depSubPlot(b):
        self.df.plot_widget(self.df.index, self.df.Address, what='max(Access)', colormap = custom_cmap, backend='bqplot_v2', tool_select=True, selection=self.plot.selection, limits=self.plot.limits,type='custom_plot1')


    dSubPlotButton = Button(
            description='Create Dependent Subplot',
            disabled=False,
            button_style='',
            layout= Layout(margin='10px 10px 0px 10px', width='200px', height='40px', border='1px solid black', flex='1'),
            style={'button_color': 'lightgray'},
            )
    dSubPlotButton.on_click(depSubPlot)
    display(dSubPlotButton)

    return

