import moneta_tags as moneta
import random


#moneta.DUMP_START_ALL("init", True);
t = [random.random() for _ in range(0,10000)]
#moneta.DUMP_STOP("init")
moneta.START_TRACE()
moneta.DUMP_START_ALL("sort", True);
s = t.sort()
moneta.DUMP_STOP("sort")

moneta.DUMP_START_ALL("shuffle", True);
s = random.shuffle(t)
moneta.DUMP_STOP("shuffle")
