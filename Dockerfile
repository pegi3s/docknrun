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
RUN apt-get install -y dbus-x11
RUN apt-get install -y python3-requests

RUN \
  FIREFOX_SETTING="/usr/lib/firefox/browser/defaults/preferences/firefox.js" && \
  echo 'pref("datareporting.policy.firstRunURL", "");' > ${FIREFOX_SETTING} && \
  echo 'pref("datareporting.policy.dataSubmissionEnabled", false);' >> ${FIREFOX_SETTING} && \
  echo 'pref("datareporting.healthreport.service.enabled", false);' >> ${FIREFOX_SETTING} && \
  echo 'pref("datareporting.healthreport.uploadEnabled", false);' >> ${FIREFOX_SETTING} && \
  echo 'pref("trailhead.firstrun.branches", "nofirstrun-empty");' >> ${FIREFOX_SETTING} && \
  echo 'pref("browser.aboutwelcome.enabled", false);' >> ${FIREFOX_SETTING}

ENV DISPLAY=:0

COPY main.py /opt
COPY play_video.py /opt
COPY find_versions.py /opt
COPY network.py /opt
COPY environment.py /opt
COPY nested_menu.py /opt
COPY email_button.py /opt
COPY docker_manager_button.py /opt
COPY run_window.py /opt
COPY secondary_window.py /opt
COPY tooltip.py /opt
COPY docker_explainVideo.mp4 /opt
COPY pegi3s_logo.png /opt

WORKDIR /opt

ENTRYPOINT ["python3", "main.py"]
