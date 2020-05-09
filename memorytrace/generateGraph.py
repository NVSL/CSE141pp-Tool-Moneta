import ipywidgets as widgets
from ipywidgets import Checkbox, VBox, HBox
import os
from os import path
import sys
sys.path.append('../')
import vaex
import vaex.jupyter
import numpy as np
import pylab as plt
import vaex.jupyter.plot
vaex.jupyter.plot.backends['bqplot_v2'] = ('vaex_extended.jupyter.bqplot', 'BqplotBackend')

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


#Enumerations
WRITE_MISS = 4
READ_MISS = 8
WRITE_HIT = 16
READ_HIT = 32



df = vaex.open(path.expanduser("/setup/converter/outfiles/trace.hdf5"))
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
        else:
            targetHit = WRITE_HIT
            targetMiss = WRITE_MISS
        
        if(change.new == True):
            df.select(df.Access == targetHit, mode='or', name='rw')
            df.select(df.Access == targetMiss, mode='or', name='rw')
            combineSelections()
        else:
            df.select(df.Access == targetHit, mode='subtract', name='rw')
            df.select(df.Access == targetMiss, mode='subtract', name='rw')
            combineSelections()
    df.select('total')
            
        
            
            
def updateHitMiss(change):
    if(change.name == 'value'):
        
        name = change.owner.description
        
        if(name == "Hits"):
            targetRead = READ_HIT
            targetWrite = WRITE_HIT
        else:
            targetRead = READ_MISS
            targetWrite = WRITE_MISS
        
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
             Checkbox(description="Misses", value=True, disabled=False, indent=False)]
    
    
for i in range(numTags):
    tagButtons[i].observe(updateGraph)
    
for button in rwButtons:
    button.observe(updateReadWrite)
    
for button in hmButtons:
    button.observe(updateHitMiss)
    
checks = HBox([VBox(tagButtons), VBox(rwButtons), VBox(hmButtons)])

df.plot_widget(df.index, df.Address, selection=[True], backend='bqplot_v2', tool_select=True)



display(checks)
