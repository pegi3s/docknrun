FROM pegi3s/docker:29.0.1

ENV DEBIAN_FRONTEND=noninteractive
ENV BROWSER=firefox

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y universe && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      gnupg \
      ca-certificates \
      wget \
      tar \
      xz-utils \
      xvfb \
      libgtk-3-0 \
      libdbus-glib-1-2 \
      libx11-xcb1 \
      libasound2t64 \
      fonts-liberation \
      dbus-x11 \
      x11-xserver-utils \
      xclip \
      python3 python3-tk python3-pil python3-pil.imagetk python3-opencv python3-pyperclip python3-requests \
    && rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/firefox.tar.xz \
      "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar -xJf /tmp/firefox.tar.xz -C /opt && \
    ln -sf /opt/firefox/firefox /usr/local/bin/firefox && \
    rm -f /tmp/firefox.tar.xz

RUN mkdir -p /opt/firefox/defaults/pref && \
    printf '%s\n' \
      'lockPref("datareporting.policy.firstRunURL", "");' \
      'lockPref("datareporting.policy.dataSubmissionEnabled", false);' \
      'lockPref("datareporting.healthreport.service.enabled", false);' \
      'lockPref("datareporting.healthreport.uploadEnabled", false);' \
      'lockPref("trailhead.firstrun.branches", "nofirstrun-empty");' \
      'lockPref("browser.aboutwelcome.enabled", false);' \
    > /opt/firefox/mozilla.cfg && \
    printf '%s\n' \
      'pref("general.config.filename", "mozilla.cfg");' \
      'pref("general.config.obscure_value", 0);' \
    > /opt/firefox/defaults/pref/local-settings.js

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
