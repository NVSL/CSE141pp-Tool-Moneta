# Moneta

Generate and visualize billions of memory accesses with this project built on PIN and HDF5.

## Getting Started

### Building the Image
First clone the repository.
```
git clone https://github.com/NVSL/CSE141pp-Tool-Moneta
cd CSE141pp-Tool-Moneta
```

Build the Docker image and name it `moneta-img`.
```
docker build -t moneta-img .
```


### Creating the Container

Due to the way Windows interprets paths, these next few instructions may differ slightly depending on your operating system. If you are using Windows, [skip to this section](#windows).

<a name="port"></a>Start a detached docker container named `moneta`. **Take note of the `####:8888` in the command.** The `####` will be your **port number** for running the notebook. The port number will be `8888` here but can be changed if there are any conflicts. **Note that you will have to change the Jupyter Notebook URL port to the port set here when you run the `moneta` command.**
```
docker run --detach --name moneta -p 8888:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes moneta-img bash -c "while true; do sleep 10;done"
```

Connect to the container.
```
docker exec -it moneta bash
```

#### <a name="windows"></a>Windows: Run the following instead

```
MSYS_NO_PATHCONV=1 docker run --detach --name moneta -p 8888:8888  -v "$PWD":/home/jovyan/work --user root -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes moneta-img bash -c "while true; do sleep 10;done"
```

To connect to the container, you may need be prompted to use `winpty`:
```
winpty docker exec -it moneta bash
```

### Opening the Notebook
Run `moneta` from any directory to start the local Jupyter Notebook server where the Moneta Jupyter Notebook will be hosted on.

You should see a list of URLs appear. Go to your preferred web browser and paste the link that looks like the following:

```
http://127.0.0.1<b>:8888</b>/?token=...
```
**Notice the `8888` in the link. If you used a port number other than `8888` when [creating the Docker container](#port), replace `8888` with your port number.**

**Note For Docker Toolbox**: If you are using Docker Toolbox (this is different from Docker Desktop) as your Docker environment, you will also have to replace `127.0.0.1` with `192.168.99.100` to access the link.

```
http://192.168.99.100<b>:8888</b>/?token=...
```

If you were able to successfully connect, you will see a Jupyter tab on your browser with a list of the files/subdirectories in the `~/work/moneta` directory. Open the `Moneta.ipynb` file.

## Developers
 - Amithab Arumugam
 - Ashwin Rao
 - Christie Lincoln
 - Elvis Tran
 - Jad Barrere
 - Kevin Tang
 - Sam Liu
 - Stephanie Hernandez
