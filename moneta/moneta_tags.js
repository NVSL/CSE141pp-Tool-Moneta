const moneta = require( './build/release/moneta.node');

arr = Array.from({length: 1000}, () => Math.floor(Math.random() * 1000));
moneta.JS_START_TRACE();
// moneta.JS_DUMP_START_ALL("sort", true);
s = arr.sort();
moneta.JS_DUMP_STOP("sort");