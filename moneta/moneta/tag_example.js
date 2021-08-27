const moneta = require( '../build/release/moneta.node');

t = Array.from({length: 1000}, () => Math.floor(Math.random() * 1000));
moneta.JS_START_TRACE();
// moneta.JS_DUMP_START_ALL("sort", true);
s = t.sort();
moneta.JS_DUMP_STOP("sort");
moneta.JS_DUMP_STOP("sort");
moneta.JS_NEW_TRACE("shuffle");
moneta.JS_DUMP_START_ALL("shuffle", true);
s = t.sort(()=> Math.random() - 0.5);
moneta.JS_DUMP_STOP("shuffle");