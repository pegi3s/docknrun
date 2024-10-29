# plays the video

import cv2
import tkinter as tk
from PIL import Image, ImageTk
import webbrowser
import threading

def play_video(root, video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = int(1000 / fps)

    # Create the video frame
    video_frame = tk.Frame(root, width=640, height=360)  # Updated to a higher resolution
    video_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    # Configuring the video display area
    video_label = tk.Label(video_frame, cursor="hand2")
    video_label.pack()
    video_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.youtube.com/@pegi3s"))

    def play():
        while True:
            for i in range(total_frames):
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (391, 220), interpolation=cv2.INTER_AREA)  # Using INTER_AREA for resizing
                    img = Image.fromarray(frame)
                    img = ImageTk.PhotoImage(image=img)

                    video_label.config(image=img)
                    video_label.image = img

                    # Frames do video (25ms entre frames / 40 fps)
                    video_label.after(frame_delay)
                    video_label.update()
                else:
                    # If frame not read properly, break the loop
                    break
            # Reset the video capture to the beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Initializing video playback in a separate thread
    thread = threading.Thread(target=play)
    thread.daemon = True
    thread.start()

    # Function to stop video playback and release resources
    def stop_video():
        cap.release()
        root.destroy()

    # Binds the stop_video function to the window's close event
    root.protocol("WM_DELETE_WINDOW", stop_video)