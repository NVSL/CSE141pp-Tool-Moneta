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


df['index'] = np.arange(0, df.Address.count())

#Set up name-tag mapping
namesFromFile = (tag_map.Tag_Name.values).tolist()
tagsFromFile = (tag_map.Tag_Value.values).tolist()
numTags = len(namesFromFile)



#Define all selections here
df.select(True, name='structures')
df.select(True, name='rw')
df.select(True, name='hm')
df.select(True, name='total')


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
        elif(name == "Misses"):
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

rwButtons = [Checkbox(description="Reads", value=True, disabled=False, indent=False),
             Checkbox(description="Writes", value=True, disabled=False, indent=False)]

hmButtons = [Checkbox(description="Hits", value=True, disabled=False, indent=False),
             Checkbox(description="Misses", value=True, disabled=False, indent=False),
             Checkbox(description="Compulsory Misses", value=True, disabled=False, indent=False)]
    
    
for i in range(numTags):
    tagButtons[i].observe(updateGraph)
    
for button in rwButtons:
    button.observe(updateReadWrite)
    
for button in hmButtons:
    button.observe(updateHitMiss)
    
checks = HBox([VBox(tagButtons), VBox(rwButtons), VBox(hmButtons)])

newc = np.ones((11, 4))
newc[1] = [0, 0, 1, 1] # read_hits - 1, .125
newc[2] = [0, 1, 1, 1] # write_hits - 2, .25
newc[3] = [0.047, 1, 0, 1] # cache_size
newc[4] = [1, 1, 0, 1] # read_misses - 3, .375
newc[5] = [1, 0, 0, 1] # write_misses - 4, .5
newc[6] = [0.737, 0.745, 0.235, 1] # compulsory read misses - 5, .625
newc[8] = [0.745, 0.309, 0.235, 1] # compulsory write misses - 6, .75

custom_cmap = ListedColormap(newc)

vaex_extended.vaex_cache_size = int(CACHE_SIZE)*int(BLOCK_SIZE)
df.plot_widget(df.index, df.Address, what='max(Access)', colormap = custom_cmap, selection=[True], backend='bqplot_v2', tool_select=True)



display(checks)
