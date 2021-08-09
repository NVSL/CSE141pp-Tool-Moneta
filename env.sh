
if ! ( [ -e env.sh ] && [ -d moneta ] && [ -d moneta/moneta ] && [ -d moneta/moneta/vaextended ]  );then
    echo YOU ARE IN THE WRONG DIRCECTORY
else
    export MONETA_ROOT=$PWD
    export LD_LIBRARY_PATH=$MONETA_ROOT/moneta/src:$LD_LIBRARY_PATH
    PATH=$PATH:$MONETA_ROOT/bin
fi
