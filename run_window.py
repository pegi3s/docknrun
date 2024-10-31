import subprocess
import threading
import time
import tkinter as tk


def open_run_window(master, command):
    def update_text_box(line):
        info_running_text_box.config(state="normal")  # Activate to allow editing
        info_running_text_box.insert("end", line + "\n")  # Adds text
        info_running_text_box.see("end")  # Automated rulling
        info_running_text_box.config(state="disabled")  # Disable

    def display_close_button(running_time):
        runtime_label.configure(text=f"Runtime: {running_time:.2f} seconds")
        runtime_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)  # Shows execution time
        close_window_button.place(relx=0.5, rely=0.965, anchor=tk.CENTER)  # Button to get to default state

    def update_output(process):
        for line in process.stdout:
            run_window.after(0, lambda: update_text_box(line.strip()))

    def close_window():
        run_window.destroy()

    run_window = tk.Toplevel(master)
    run_window.title("Run Docker Image")

    # Shows that image is running
    running_text = tk.Label(run_window, text="Running:", fg="black", font=("sans-serif", 25))

    # Creates a non-interactive text box
    info_running_text_box = tk.Text(run_window, state=tk.DISABLED, height=30, width=55)
    close_window_button = tk.Button(run_window, text="Okay", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"),
                                    relief="raised", width=16, height=1,
                                    command=close_window)  # Opens image documentation
    runtime_label = tk.Label(run_window, fg="black", font=("sans-serif", 15))

    running_text.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
    info_running_text_box.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    info_running_text_box.config(state="normal")  # Set state to normal to enable editing
    info_running_text_box.delete("1.0", "end")  # Clear all text from the text box
    info_running_text_box.config(state="disabled")  # Set state back to disabled to disable editing

    # Acts as a modal dialog
    run_window.geometry(master.geometry())
    run_window.grab_set()

    start_time = time.time()

    # Reads line by line
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)

    thread = threading.Thread(target=update_output, args=(process,))
    thread.start()

    # Waits until process is finnished
    process.wait()

    running_time = time.time() - start_time

    # Shows the button again
    if display_close_button(running_time):
        display_close_button(running_time)
