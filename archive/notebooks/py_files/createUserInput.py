from imports import *

showFullDescription = {'description_width': '125px'}

cache = widgets.IntText(
            value=4096,
            description='Cache Lines:',
            style=showFullDescription,
            disabled=False
        )
lines = widgets.IntText(
            value=100000000,
            description='Lines to Output:',
            style=showFullDescription,
            disabled=False
        )

block = widgets.IntText(
            value=64,
            description='Block Size (Bytes):',
            style=showFullDescription,
            disabled=False
        )

execInfile = widgets.Text(
            value='./Examples/build/sorting',
            placeholder='',
            description='Executable Path',
            style=showFullDescription,
            disabled=False
        )

execOutfile = widgets.Text(
            value='trace',
            placeholder='',
            description='Outfile Name:',
            style=showFullDescription,
            disabled=False
        )

hdf5Infile = widgets.Text(
            value='',
            placeholder='',
            description='HDF5 Path',
            style=showFullDescription,
            disabled=False
        )

tagmapInfile = widgets.Text(
            value='',
            placeholder='',
            description='Tag Map Path',
            style=showFullDescription,
            disabled=False
        )

runBtn = widgets.Button(
        description='Run',
        disabled=False,
        button_style='',
        layout= Layout(margin='10px 30px 0px 30px', height='40px', border='1px solid black', flex='1'),
        style={'button_color': 'lightgray'}
    
        )

loadBtn = widgets.Button(
        description='Load',
        disabled=False,
        button_style='',
        layout= Layout(margin='10px 30px 0px 30px', height='40px', border='1px solid black', flex='1'),
        style={'button_color': 'lightgray'}
        )



loadFileDropdown = widgets.Dropdown(
            options=['None'],
            value='None',
            description='Load File: ',
            style=showFullDescription,
            disabled=False,
            )


cacheTextBox = VBox(children=[cache, lines, block, execOutfile, execInfile],
                    layout=Layout(flex='1')
                   )
loadFileText = VBox(children=[loadFileDropdown, hdf5Infile, tagmapInfile],
                    layout=Layout(flex='1')
                   )


buttons = HBox(children=[runBtn, loadBtn],
               layout=Layout(width='950px', display='flex', justify_content='center')  
              )

textboxes = HBox(children=[cacheTextBox, loadFileText],
                 layout=Layout(width='950px', display='flex', justify_content='center', align_items='flex-end')
                )

inputs = VBox(
            children=[textboxes, buttons],
            layout=Layout(width='950px')
         )

# Functions defined in Notebook cell
runBtn.on_click(runTool)
loadBtn.on_click(loadFile)


traceFiles = subprocess.run(['ls', '/setup/converter/outfiles'],capture_output=True).stdout.decode('utf-8')
traceFiles = traceFiles.split('\n')
traceFiles = list(filter(lambda file : 
                            re.search('^trace.*\.hdf5$', file), 
                         traceFiles))

loadFileDropdown.options = traceFiles
loadFileDropdown.value = traceFiles[0]


display(inputs)

