import threading
import time
from subprocess import Popen, PIPE, STDOUT
from tkinter import Toplevel, DISABLED, Label, WORD, Button, NORMAL, Wm, END, Tk, LEFT, BOTH
from tkinter.scrolledtext import ScrolledText
from typing import Optional


class RunWindow(Toplevel):
    def __init__(self, app_name: str, command: str, **kwargs) -> None:
        super().__init__(**kwargs)

        self._command: str = command
        self._process: Optional[Popen] = None
        self._start_time: Optional[float] = None
        self._running: bool = False

        self.title("Run command")

        # Component creation
        font = ("Helvetica", 10, "bold"),
        self._lbl_title: Label = Label(self, text=f"Executing: {app_name}", font=font)

        self._txt_output: ScrolledText = ScrolledText(self, wrap=WORD, height=15, width=80)
        self._txt_output.config(state=DISABLED)

        self._lbl_time: Label = Label(self, text="Time: 0.0s", font=font)

        self._btn_stop: Button = Button(self, text="Stop execution", command=self._stop_execution, font=font)
        self._btn_close: Button = Button(self, text="Close", command=self._close_window, font=font)

        # Component location
        if isinstance(self.master, Wm):
            self.geometry(self.master.geometry())
            self.grab_set()

        self._lbl_title.pack(pady=10)
        self._txt_output.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self._lbl_time.pack(pady=5)
        self._btn_stop.pack(side=LEFT, expand=True, padx=10, pady=10)
        self._btn_close.pack(side=LEFT, expand=True, padx=10, pady=10)

        # Events
        self.protocol("WM_DELETE_WINDOW", self._close_window)

        # Run command
        self._run_command()

    def _run_command(self) -> None:
        self._running = True
        self._start_time = time.time()
        self._process = Popen(self._command, stdout=PIPE, stderr=STDOUT, text=True, shell=True)

        threading.Thread(target=self._monitor_output, daemon=True).start()

        self._update_time()

    def _monitor_output(self) -> None:
        for line in iter(self._process.stdout.readline, ""):
            if not self._running:
                break
            self._append_output(line)

        self._process.stdout.close()
        self._process.wait()
        self._running = False

        if self.winfo_exists():
            # Disable stop button when done, only if the window was not already closed
            self._btn_stop.config(state=DISABLED)

    def _append_output(self, text: str) -> None:
        self._txt_output.config(state=NORMAL)
        self._txt_output.insert(END, text)
        self._txt_output.yview(END)  # Auto-scroll to bottom
        self._txt_output.config(state=DISABLED)

    def _update_time(self) -> None:
        elapsed_time = time.time() - self._start_time

        if self._running:
            self._lbl_time.config(text=f"Time: {elapsed_time:.1f}s")
            self.after(100, self._update_time)  # Repeat the process asynchronously
        else:
            self._lbl_time.config(text=f"Time: {elapsed_time:.1f}s (Finished)")

    def _stop_execution(self) -> None:
        if self._running and self._process:
            self._running = False

            self._process.terminate()

            self._append_output("\n========== Process terminated ==========\n")
            self._btn_stop.config(state=DISABLED)

    def _close_window(self) -> None:
        self._stop_execution()
        self.destroy()
