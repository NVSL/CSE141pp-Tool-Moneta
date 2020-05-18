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



df = vaex.open("/setup/converter/outfiles/trace.hdf5")
tag_map = vaex.open("/setup/converter/outfiles/tag_map.csv")
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
        
        if(name == "Reads"):
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
        
        if(name == "Hits"):
            targetRead = READ_HIT
            targetWrite = WRITE_HIT
        elif(name == "Capacity Misses"):
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
        
        
tagButtons = [Checkbox(description=name, value=True, disabled=False, indent=False) for name in namesFromFile]

rwButtons = [Checkbox(description="Reads ("+str(readCount)+")", value=True, disabled=False, indent=False),
             Checkbox(description="Writes ("+str(writeCount)+")", value=True, disabled=False, indent=False)]

hmButtons = [Checkbox(description="Hits ("+str(hitCount)+")", value=True, disabled=False, indent=False),
             Checkbox(description="Capacity Misses ("+str(missCount)+")", value=True, disabled=False, indent=False),
             Checkbox(description="Compulsory Misses ("+str(compMissCount)+")", value=True, disabled=False, indent=False)]

hmRates = [Label(value="Hit Rate: "+f"{hitCount*100/df.count():.2f}"+"%"),
           Label(value="Miss Rate: "+f"{missCount*100/df.count():.2f}"+"%"),
           Label(value="Compulsory Miss Rate: "+f"{compMissCount*100/df.count():.2f}"+"%")]
    
for i in range(numTags):
    tagButtons[i].observe(updateGraph)
    
for button in rwButtons:
    button.observe(updateReadWrite)
    
for button in hmButtons:
    button.observe(updateHitMiss)
    
checks = VBox([HBox([VBox(tagButtons), VBox(rwButtons), VBox(hmButtons)]),VBox(hmRates)])

newc = np.ones((11, 4))
newc[1] = [0, 0.4, 0, 1] # read_hits - 1, .125
newc[2] = [0, 0.7, 0, 1] # write_hits - 2, .25
newc[3] = [0, 0, 0, 1] # cache_size
newc[4] = [1, 0.2, 0, 1] # read_misses - 3, .375
newc[5] = [1, 0, 0.2, 1] # write_misses - 4, .5
newc[6] = [0.737, 0.401, 0.235, 1] # compulsory read misses - 5, .625
newc[8] = [0.745, 0.309, 0.235, 1] # compulsory write misses - 6, .75

custom_cmap = ListedColormap(newc)

vaex_extended.vaex_cache_size = int(CACHE_SIZE)*int(BLOCK_SIZE)
df.plot_widget(df.index, df.Address, what='max(Access)', colormap = custom_cmap, selection=[True], backend='bqplot_v2', tool_select=True)



display(checks)
