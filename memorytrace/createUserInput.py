from imports import *

showFullDescription = {'description_width': '150px'}

cache = IntText(
            value=4096,
            description='Cache Lines:',
            style=showFullDescription,
            layout= Layout(width='90%'),
            disabled=False
        )
lines = IntText(
            value=100000000,
            description='Lines to Output:',
            style=showFullDescription,
            layout= Layout(width='90%'),
            disabled=False
        )

block = IntText(
            value=64,
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
