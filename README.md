# Moneta

Generate and visualize billions of memory accesses with this project built on PIN and HDF5.

## Getting Started

First clone the repository.
```
git clone https://github.com/NVSL/CSE141pp-Tool-MemoryTrace

cd CSE141pp-Tool-MemoryTrace
```

Build the Docker image and name it `memorytrace`.
```
docker build -t memorytrace .
```

<a name="port"></a>Start a detached docker container named `memtrace`. Take note of the `XXXX:8888` in the command. the `XXXX` will be your port number for running the notebook. The port number will be `8080` here but can be changed if there are any conflicts.
```
docker run --detach --name memtrace -p 8080:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes memorytrace bash -c "while true; do sleep 10;done"
```

**Windows:** Run the following instead:
```
MSYS_NO_PATHCONV=1 docker run --detach --name memtrace -p 8080:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes memorytrace bash -c "while true; do sleep 10;done"
```

Connect to the container.
```
docker exec -it memtrace bash
```

**Windows:** You may need add `winpty` if prompted:
```
winpty docker exec -it memtrace bash
```


## For Devs Only

See Setup/ and documentation/
