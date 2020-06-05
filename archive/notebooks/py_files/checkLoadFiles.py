from imports import *

load = True
err = False

clear_output(wait=True)
display(inputs)

hdf5Load = path.expanduser(hdf5Infile.value)
tagmapLoad = path.expanduser(tagmapInfile.value)

if(not path.isfile(hdf5Load)):
    print("File \"{}\" not found".format(hdf5Load))
    err = True
    sys.exit()


if(not re.search('\.hdf5$', hdf5Load)):
    print("File \"{}\" is not a HDF5 file".format(hdf5Load))
    err = True
    sys.exit()


if(not path.isfile(tagmapLoad)):
    print("File \"{}\" not found".format(tagmapLoad))
    err = True
    sys.exit()


if(not re.search('\.csv$', tagmapLoad)):
    print("File \"{}\" is not a csv file".format(tagmapLoad))
    err = True
    sys.exit()


# Right now, we can't load files correctly because we don't store the cache info anywhere,
# so for now we will pull from the widget textboxes until it is added to tag_map
CACHE_SIZE = cache.value
NUM_LINES = lines.value
BLOCK_SIZE = block.value

if(CACHE_SIZE < 0 or NUM_LINES < 0 or BLOCK_SIZE < 0):
    print("Cache Lines, Lines to Output, and Block Size must be positive integers")
    err = True
    sys.exit()
