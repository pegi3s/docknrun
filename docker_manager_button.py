#docker-manager button in main window

import subprocess

def open_docker_manager_wrapper():
    # Enable X11 forwarding
    subprocess.call("xhost +", shell=True)
    
    # Define the Docker command to run
    docker_command = (
        "docker run --rm -ti -e USERID=$UID -e USER=$USER -e DISPLAY=$DISPLAY "
        "-v /var/db:/var/db:Z -v /tmp/.X11-unix:/tmp/.X11-unix "
        "-v $HOME/.Xauthority:/home/developer/.Xauthority "
        "-v /var/run/docker.sock:/var/run/docker.sock "
        "-v /tmp:/tmp pegi3s/docker-manager"
    )

    # Run the Docker command
    subprocess.call(docker_command, shell=True)