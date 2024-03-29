from imports import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


#sys.path.append('/setup/') # Uncomment this line for master branch
sys.path.append('../') # Uncomment this line for development branch
import vaex_extended
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot', 'BqplotBackend')


#Enumerations
COMP_W_MISS = 6
COMP_R_MISS = 5
WRITE_MISS = 4
READ_MISS = 3
WRITE_HIT = 2
READ_HIT = 1


if(load):
    # hdf5Load and tagmapLoad declared in checkFiles.py depending on user input
    hdf5Path = hdf5Load
    tagmapPath = tagmapLoad
else:
    hdf5Path = "/setup/converter/outfiles/trace.hdf5"
    tagmapPath = "/setup/converter/outfiles/tag_map.csv"


df = vaex.open(hdf5Path)
tag_map = vaex.open(tagmapPath)
numAccesses = df.Address.count()

df['index'] = np.arange(0, numAccesses)

#Set up name-tag mapping
namesFromFile = (tag_map.Tag_Name.values).tolist()
tagsFromFile = (tag_map.Tag_Value.values).tolist()
startIndices = (tag_map.First_Access.values).tolist()
startAddresses = (tag_map.Low_Address.values).tolist()
endIndices = (tag_map.Last_Access.values).tolist()
endAddresses = (tag_map.High_Address.values).tolist()

numTags = len(namesFromFile)


# Initialize accessRanges dictionary in bqplot backend with file info
from vaex_extended.jupyter.bqplot import accessRanges
accessRanges.clear()
for i in range(numTags):
    name = namesFromFile[i]
    accessRanges.update({name : {}})

    rangeData = accessRanges[name]
    rangeData.update({"startIndex" : startIndices[i]})
    rangeData.update({"endIndex" : endIndices[i]})
    rangeData.update({"startAddr" : startAddresses[i]})
    rangeData.update({"endAddr" : endAddresses[i]})




#Define all selections here
df.select(True, name='structures')
df.select(True, name='rw')
df.select(True, name='hm')
df.select(True, name='total')

#Initialize counts
read_hits = df[df.Access == READ_HIT]
write_hits = df[df.Access == WRITE_HIT]
read_misses = df[df.Access == READ_MISS]
write_misses = df[df.Access == WRITE_MISS]
comp_read_misses = df[df.Access == COMP_R_MISS]
comp_write_misses = df[df.Access == COMP_W_MISS]
readCount = read_hits.count() + read_misses.count()
writeCount = write_hits.count() + write_misses.count()
hitCount = read_hits.count() + write_hits.count()
missCount = read_misses.count() + write_misses.count()
compMissCount = comp_read_misses.count() + comp_write_misses.count()

#Initialize selections
for tag in tagsFromFile:
    df.select(df.Tag == tag, mode='or')

    
#Handle all boolean combinations of independent checkboxes here
def combineSelections():
    df.select("structures", mode='replace', name='total')
    df.select("rw", mode='and', name='total')
    df.select("hm", mode='and', name='total')
    
    
def updateGraph(change):
    if(change.name == 'value'):
        
        name = change.owner.description
        tag = tagsFromFile[namesFromFile.index(name)]

        if(change.new == True):
            df.select(df.Tag == tag, mode='or', name='structures')
            combineSelections()
        else:
            df.select(df.Tag == tag, mode='subtract', name='structures')
            combineSelections()
    df.select('total')
        
        
        
def updateReadWrite(change):
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
            df.select(df.Access == targetHit, mode='or', name='rw')
            df.select(df.Access == targetMiss, mode='or', name='rw')
            df.select(df.Access == targetCMiss, mode='or', name='rw')
            combineSelections()
        else:
            df.select(df.Access == targetHit, mode='subtract', name='rw')
            df.select(df.Access == targetMiss, mode='subtract', name='rw')
            df.select(df.Access == targetCMiss, mode='subtract', name='rw')
            combineSelections()
    df.select('total')
            
        
            
            
def updateHitMiss(change):
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
            df.select(df.Access == targetRead, mode='or', name='hm')
            df.select(df.Access == targetWrite, mode='or', name='hm')
            combineSelections()
        else:
            df.select(df.Access == targetRead, mode='subtract', name='hm')
            df.select(df.Access == targetWrite, mode='subtract', name='hm')
            combineSelections()
    df.select('total')  
        
        
tagChecks = [HBox([widgets.Button(
                                  icon='search-plus',
                                  tooltip=name,
                                  layout=Layout(height='35px', 
                                                width='35px', 
                                                border='none',
                                                align_items='center'
                                                ),
                                    style={'button_color': 'transparent'}
                                 ),

                    widgets.Checkbox(description=name, 
                                    value=True, 
                                    disabled=False, 
                                    indent=False)
                  ])
             for name in namesFromFile]


rwChecks = [widgets.Checkbox(description="Reads ("+str(readCount)+")", value=True, disabled=False, indent=False),
            widgets.Checkbox(description="Writes ("+str(writeCount)+")", value=True, disabled=False, indent=False)]

hmChecks = [widgets.Checkbox(description="Hits ("+str(hitCount)+")", value=True, disabled=False, indent=False),
            widgets.Checkbox(description="Capacity Misses ("+str(missCount)+")", value=True, disabled=False, indent=False),
            widgets.Checkbox(description="Compulsory Misses ("+str(compMissCount)+")", value=True, disabled=False, indent=False)]

hmRates = [widgets.Label(value="Hit Rate: "+f"{hitCount*100/df.count():.2f}"+"%"),
           widgets.Label(value="Capacity Miss Rate: "+f"{missCount*100/df.count():.2f}"+"%"),
           widgets.Label(value="Compulsory Miss Rate: "+f"{compMissCount*100/df.count():.2f}"+"%")]
    
for i in range(numTags):
    tagChecks[i].children[1].observe(updateGraph)
    
for check in rwChecks:
    check.observe(updateReadWrite)
    
for check in hmChecks:
    check.observe(updateHitMiss)
    
checks = VBox([HBox([VBox(tagChecks), VBox(rwChecks), VBox(hmChecks)]),VBox(hmRates)])

newc = np.ones((11, 4))
newc[1] = [0, 0.5, 0, 1] # read_hits - 1, .125
#newc[2] = [0, 0.7, 0, 1] # write_hits - 2, .25
newc[2] = [0, 0.5, 0, 1] # write_hits - 2, .25
newc[3] = [0, 0, 0, 1] # cache_size
newc[4] = [1, 0.5, 0, 1] # read_misses - 3, .375
#newc[5] = [1, 0, 0.2, 1] # write_misses - 4, .5
newc[5] = [1, 0.5, 0, 1] # write_misses - 4, .5
newc[6] = [0.235, 0.350, 0.745, 1] # compulsory read misses - 5, .625
newc[8] = [0.235, 0.350, 0.745, 1] # compulsory write misses - 6, .75

# Original colors below
newc[1] = [0, 0, 1, 1] # read_hits - 1, .125
#newc[2] = [0, 0.7, 0, 1] # write_hits - 2, .25
newc[2] = [0, 1, 1, 1] # write_hits - 2, .25
newc[3] = [0.047, 1, 0, 1] # cache_size
newc[4] = [1, 1, 0, 1] # read_misses - 3, .375
#newc[5] = [1, 0, 0.2, 1] # write_misses - 4, .5
newc[5] = [1, 0, 0, 1] # write_misses - 4, .5
newc[6] = [0.737, 0.745, 0.235, 1] # compulsory read misses - 5, .625
newc[8] = [0.745, 0.309, 0.235, 1] # compulsory write misses - 6, .75
custom_cmap = ListedColormap(newc)

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
            df.select(df.Access == targetHit, mode='or', name='rw')
            df.select(df.Access == targetMiss, mode='or', name='rw')
            df.select(df.Access == targetCMiss, mode='or', name='rw')
            combineSelections()
        else:
            df.select(df.Access == targetHit, mode='subtract', name='rw')
            df.select(df.Access == targetMiss, mode='subtract', name='rw')
            df.select(df.Access == targetCMiss, mode='subtract', name='rw')
            combineSelections()
    df.select('total')  
            
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
            df.select(df.Access == targetRead, mode='or', name='hm')
            df.select(df.Access == targetWrite, mode='or', name='hm')
            combineSelections()
        else:
            df.select(df.Access == targetRead, mode='subtract', name='hm')
            df.select(df.Access == targetWrite, mode='subtract', name='hm')
            combineSelections()
    df.select('total')  
from matplotlib.colors import to_rgba
def updateColorMap(change):
    if(change.name=='value'):
        name=change.owner.name
        if(re.search('^Hits', name)):
            plot.colormap.colors[1] = to_rgba(change.new,1)
            plot.colormap.colors[2] = to_rgba(change.new,1)
        elif(re.search('^Cache', name)):
            plot.colormap.colors[3] = to_rgba(change.new,1)
        elif(re.search('^Capacity', name)):
            plot.colormap.colors[4] = to_rgba(change.new,1)
            plot.colormap.colors[5] = to_rgba(change.new,1)
        else:
            plot.colormap.colors[6] = to_rgba(change.new,1)
            plot.colormap.colors[8] = to_rgba(change.new,1)
cb_lyt=widgets.Layout(width='180px')
cp_lyt=widgets.Layout(width='30px')
# Read Write custom checkbox
def RWCheckbox(description, color_value):
    rwcp = widgets.ColorPicker(concise=True, value=color_value, disabled=False,layout=cp_lyt)
    rwcp.name=description
    return HBox([widgets.Checkbox(description=description, value=True, disabled=False, indent=False,layout=cb_lyt),
                rwcp])
from matplotlib.colors import to_hex
rwChecks2 = [widgets.Checkbox(description="Reads ("+str(readCount)+")",  value=True, disabled=False, indent=False,layout=widgets.Layout(width='270px')),
            widgets.Checkbox(description="Writes ("+str(writeCount)+")",  value=True, disabled=False, indent=False,layout=widgets.Layout(width='270px'))]
hmChecks2 = [RWCheckbox(description="Hits ("+str(hitCount)+")", color_value=to_hex([0, 0.5, 0])),
            RWCheckbox(description="Capacity Misses ("+str(missCount)+")", color_value=to_hex([1, 0.5, 0])),
            RWCheckbox(description="Compulsory Misses ("+str(compMissCount)+")", color_value=to_hex([0.235, 0.350, 0.745]))]
cacheChecks2 = [RWCheckbox(description="Cache ("+str(int(CACHE_SIZE) * int(BLOCK_SIZE))+" bytes)", color_value=to_hex([0, 0, 0]))]
checks2 = VBox([VBox(children=[widgets.Label(value='Legend')] + rwChecks2 +  hmChecks2 + cacheChecks2,
                     layout=widgets.Layout(padding='10px',border='1px solid black')
                    )])
for check in rwChecks2:
    check.observe(updateReadWrite2)
for check in [hbox.children[0] for hbox in hmChecks2]:
    check.observe(updateHitMiss2)
for colorpicker in [hbox.children[1] for hbox in hmChecks2]:
    colorpicker.observe(updateColorMap)
    
vaex_extended.vaex_cache_size = int(CACHE_SIZE)*int(BLOCK_SIZE)
plot = df.plot_widget(df.index, df.Address, what='max(Access)', colormap = custom_cmap, selection=[True], legend=checks2, type='custom_plot1', backend='bqplot_v2', tool_select=True)

backend = plot.backend
for i in range(numTags):
    tagChecks[i].children[0].on_click(backend.zoomSection)



display(checks)