# CSE142/L MemoryTrace

See https://github.com/NVSL/CSE141pp-Explorer/blob/master/README.md
 for original tutorials.

## Getting Started

First clone the repository.
```
git clone https://github.com/NVSL/CSE141pp-Explorer

cd CSE141pp-Explorer
```

Build the Docker image and name it "memorytrace".
```
docker build -t memorytrace .
```

Start a detached docker container named "memtrace".
```
docker run --detach --name memtrace -p 8080:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes memorytrace bash -c "while true; do sleep 10;done"
```

Connect to the container.
```
docker exec -it memtrace bash
```

# Usage

## JupyterLab
First install the memorytrace extension.
```
cd memorytrace
jupyter labextension install . --no-build
```

Start the Jupyter Lab.
```
jupyter lab --allow-root --watch
```
Copy the last URL into the browser (change port as needed).

## Binary Instrumentation with PIN
The pintool folder is installed at /setup/pintool.
Example:
```
cd /setup/pintool/source/tools/ManualExamples

make obj-intel64/pinatrace.so TARGET=intel64

pin -t obj-intel64/pinatrace.so -- /bin/ls

head pinatrace.out
```