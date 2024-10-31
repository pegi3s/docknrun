FROM pegi3s/docker

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update
RUN apt-get install -y wget gnupg snap
RUN apt-get install -y python3
RUN apt-get install -y python3-tk
RUN apt-get install -y python3-pil python3-pil.imagetk
RUN apt-get install -y python3-opencv
RUN apt-get install -y python3-pyperclip
RUN apt-get install -y firefox
RUN apt-get install -y x11-xserver-utils
RUN apt-get install -y xclip


ENV DISPLAY=:0

COPY main.py /opt
COPY play_video.py /opt
COPY find_versions.py /opt
COPY download_test_data.py /opt
COPY prepare_docker_command.py /opt
COPY prepare_project.py /opt
COPY pegi3s_logo.png /opt
COPY nested_menu.py /opt
COPY docker_explainVideo.mp4 /opt
COPY download_test_results.py /opt
COPY email_button.py /opt
COPY docker_manager_button.py /opt
COPY run_window.py /opt
COPY secondaryWindow.py /opt


WORKDIR /opt

ENTRYPOINT ["python3", "main.py"]

#docker run --rm -ti -e USERID=$UID -e USER=$USER -e DISPLAY=$DISPLAY -v /var/db:/var/db:Z -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/.Xauthority:/home/developer/.Xauthority -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp -v /mnt/c/Users/jbvie/Documents/Docker/docknrun1.0/Tests_and_documentation:/data pegi3s/docknrun
