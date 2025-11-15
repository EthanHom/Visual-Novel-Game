# Docker Environment for CSE 111

This docker container provides a linux system with the SQLite program installed.
Students may use docker to begin learning SQL without installing SQLite natively.

To get started with Docker, install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Windows/MacOS) or [Docker Engine](https://docs.docker.com/engine/install/) (for Linux).

*Note: Docker for Windows requires installing [WSL 2](https://docs.docker.com/desktop/setup/install/windows-install/#wsl-verification-and-setup).*

Make sure Docker is running when you proceed through the next steps.

## VS Code Instructions (Recommended)

### Prerequisites
- [VS Code](https://code.visualstudio.com/)
- Dev Containers extension by Microsoft
- Docker Desktop or Docker Engine should be running

### Open in VS Code
- Open this folder in VS Code, which should detect the `.devcontainer` folder and prompt: "Reopen in Container?"
- Accept the prompt and VS Code should reopen inside the container
- You can then edit files and execute code within the container

## Command Line Instructions (Alternative to VS Code)

### Step 1: Build the Docker Image
Open Terminal (MacOS/Linux) or Command Prompt (Windows) and navigate to the project folder.
Then run:
```bash
docker build -t tpch-sqlite-lab .
```
- `-t tpch-sqlite-lab`: Tags the image with a name
- `.`: Tells Docker to use the current directory (where the Dockerfile is)

### Step 2: Start the Container
To launch an interactive sesssion:
```bash
docker run -it --name cse111-lab -v "$(pwd):/workspace" tpch-sqlite-lab
```
- `--name cse111-lab`: Names the container `cse111-lab`. Otherwise, Docker will generate a random name.  
- `v "$(pwd):/workspace"`: Mounts the current folder as the `/workspace` folder inside the container.
- You can edit files in VS Code and still use them in the container.

### Restarting the Container
After exiting the container, you can restart it:
```bash
docker start -ai cse111-lab
```
It's important to use this `start` command, instead of `run`, which would create another container.