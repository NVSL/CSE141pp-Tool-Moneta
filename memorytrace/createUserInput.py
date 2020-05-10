from imports import *

showFullDescription = {'description_width': '150px'}

cache = Text(
            value='4096',
            placeholder='',
            description='Cache Lines:',
            style=showFullDescription,
            layout= Layout(width='90%'),
            disabled=False
        )
lines = Text(
            value='1000000000',
            placeholder='',
            description='Lines to Output:',
            style=showFullDescription,
            layout= Layout(width='90%'),
            disabled=False
        )

block = Text(
            value='64',
            placeholder='',
            description='Block Size (Bytes):',
            style=showFullDescription,
            layout= Layout(width='90%'),
            disabled=False
        )

infile = Text(
            value='./Examples/build/sorting',
            placeholder='',
            description='Executable Path',
            style=showFullDescription,
            layout= Layout(width='90%'),
            disabled=False
        )

run = Button(
        description='Run',
        disabled=False,
        button_style='',
        layout= Layout(margin='10px 0px 0px 0px', height='40px', width='90%', border='1px solid black'),
        style={'button_color': 'lightgray'}
    )


inputs = VBox(
            children=[cache, lines, block, infile, run],
            layout=Layout(width="400px")
        )

run.on_click(runTool)
display(inputs)
