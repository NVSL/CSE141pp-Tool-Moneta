import re

f = open('./out_graph', 'r')
out = open('./edges', 'w+')

curr_block = []
while True:
    line = f.readline().strip(' ')

    if not line:
        break

    if line == '\n':
        first_addr = curr_block[0].strip(' \n').split('||')[0]
        jump_args = curr_block[-1].strip(' \n').split(' ')

        if len(jump_args) > 1:
            jump_addr = jump_args[-1]
 
            if re.search(r'^0x[0-9a-f]+$', jump_addr):
                first_addr = re.sub(r'0x0*', '0x', first_addr)
                jump_addr = re.sub(r'0x0*', '0x', jump_addr)
                out.write(f'{first_addr},{jump_addr}\n')

        curr_block = []
    else:
        curr_block.append(line)



f.close()
out.close()