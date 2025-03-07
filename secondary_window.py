import json
import os
import webbrowser
from datetime import datetime
from tkinter import Frame, Toplevel, Label, Button, Menu, StringVar, Entry, filedialog, Misc, LabelFrame, \
    messagebox
from tkinter.constants import CENTER, W, BOTH, EW, E, NSEW, END, DISABLED, X, LEFT, RIGHT, NORMAL
from tkinter.scrolledtext import ScrolledText
# ttk's Radiobutton is used because default one is now properly working when value change is cancelled in _on_mode_change
from tkinter.ttk import Notebook, Radiobutton, Style
from typing import List, Optional, Final, Any, Callable

import requests

from environment import load_config_file, DocknrunPaths
from find_versions import find_image_versions
from network import generate_manual_url, generate_pegi3s_url
from run_window import RunWindow
from tooltip import ToolTip

_PATH_DEFAULT_DOCKER_COMMAND_DATA_DIR: Final[str] = "/your/data/dir"
_RUN_COMMAND_VERSION_LINE_PREFIX: Final[str] = "# version=pegi3s/"

_GUI_INVOCATION_GENERAL: Final[str] = f"""
xhost + && docker run --rm -ti -e USERID=$UID -e USER=$USER -e DISPLAY=$DISPLAY -v /var/db:/var/db:Z -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/.Xauthority:/home/developer/.Xauthority -v \"{_PATH_DEFAULT_DOCKER_COMMAND_DATA_DIR}:/data\" -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp pegi3s/
""".strip()

_BUTTON_DEFAULTS = {
    "bg": "#3498db",
    "fg": "white",
    "font": ("Helvetica", 10, "bold"),
    "relief": "raised",
    "width": 20,
    "pady": 8
}
_TITLE_LABEL_DEFAULTS = {
    "fg": "black",
    "font": ("sans-serif", 12)
}
_SCROLLED_TEXT_DEFAULTS = {
    "width": 60,
    "height": 6
}

_LABEL_FRAME_DEFAULTS = {
    "font": _TITLE_LABEL_DEFAULTS["font"],
    "padx": 10,
    "pady": 10
}

_RADIOBUTTON_DEFAULTS = {
    "style": "Custom.TRadiobutton"
}


class _ComponentBuilder:
    def __init__(self, default_master: Misc):
        self._default_master: Misc = default_master

        self._rb_style: Style = Style()
        self._rb_style.configure("Custom.TRadiobutton", font=("sans-serif", 12))

    def _build_params(self, defaults, **kwargs):
        defaults = defaults.copy()
        defaults["master"] = self._default_master

        return {**defaults, **kwargs}

    def build_button(self, **kwargs) -> Button:
        return Button(**self._build_params(_BUTTON_DEFAULTS, **kwargs))

    def build_title_label(self, **kwargs) -> Label:
        return Label(**self._build_params(_TITLE_LABEL_DEFAULTS, **kwargs))

    def build_scrolled_text(self, **kwargs) -> ScrolledText:
        return ScrolledText(**self._build_params(_SCROLLED_TEXT_DEFAULTS, **kwargs))

    def build_label_frame(self, **kwargs) -> LabelFrame:
        return LabelFrame(**self._build_params(_LABEL_FRAME_DEFAULTS, **kwargs))

    def build_radio_button(self, **kwargs) -> Radiobutton:
        return Radiobutton(**self._build_params(_RADIOBUTTON_DEFAULTS, **kwargs))


class _RunPanel(Frame):
    def __init__(self,
                 image_data,
                 paths: DocknrunPaths,
                 gui: bool = False,
                 fill_run_command: bool = True,
                 version_change_callback: Callable[[str], bool] = lambda _: True,
                 **kwargs):
        super().__init__(**kwargs)

        self._image_data = image_data
        self._gui: bool = gui
        self._paths: DocknrunPaths = paths
        self._default_paths: DocknrunPaths = DocknrunPaths.build_default_paths()
        self._version_change_callback: Callable[[str], bool] = version_change_callback

        self._builder: _ComponentBuilder = _ComponentBuilder(self)

        # Component creation
        self._lbl_run_command: Label = self._builder.build_title_label(text="Run Command")
        ToolTip.for_widget(self._lbl_run_command, "Change the parameters below as you better see fit")
        self._txt_run_command: ScrolledText = self._builder.build_scrolled_text()
        if not gui:
            self._btn_test_data_invocation: Button = self._builder.build_button(text="Load test invocation")
        self._btn_latest_invocation: Button = self._builder.build_button(text="Load past invocation")

        # Component location
        for col in range(3):
            self.grid_columnconfigure(col, weight=1)
        self.grid_columnconfigure(3, weight=0)

        self._lbl_run_command.grid(row=101, column=0, columnspan=4, sticky=W)
        self._txt_run_command.grid(row=102, column=0, rowspan=2, columnspan=3, sticky=NSEW)
        if gui:
            self._btn_latest_invocation.grid(row=102, column=3, rowspan=2)
        else:
            self._btn_test_data_invocation.grid(row=102, column=3)
            self._btn_latest_invocation.grid(row=103, column=3)

        # Events
        if not gui:
            self._btn_test_data_invocation.config(command=self._on_test_data_invocation)
        self._btn_latest_invocation.config(command=self._on_past_invocation_load)

        # Run command
        if fill_run_command:
            self._set_text_in_run_command(self._build_run_command())

    @property
    def run_command(self) -> str:
        return self._txt_run_command.get("1.0", END).strip()

    def _is_run_command_changed(self) -> bool:
        return self.run_command != self._build_run_command()

    def _build_run_command(self) -> str:
        if self._gui:
            return self._image_data["gui_command"]
        else:
            run_command_usual_invocation_specific = self._image_data["usual_invocation_specific"]
            usual_invocation_specific_comments = self._image_data["usual_invocation_specific_comments"]

            if run_command_usual_invocation_specific == "":
                if len(usual_invocation_specific_comments) > 0:
                    run_command_text = "# " + "\n# ".join(usual_invocation_specific_comments)
                else:
                    run_command_text = "# This image doesn't require user input"
            else:
                run_command_text = run_command_usual_invocation_specific

                if len(usual_invocation_specific_comments) > 0:
                    run_command_text += "\n\n# " + "\n# ".join(usual_invocation_specific_comments)

            return run_command_text.strip()

    def _set_text_in_run_command(self, run_command: str) -> None:
        initial_state = self._txt_run_command.cget("state")
        self._txt_run_command.config(state=NORMAL)
        self._txt_run_command.delete("1.0", END)
        self._txt_run_command.insert(END, run_command)
        self._txt_run_command.config(state=initial_state)

    def _on_test_data_invocation(self) -> None:
        run_command = self._image_data["test_invocation_specific"]
        run_command = run_command.replace(self._default_paths.base_path, self._paths.base_path)
        self._set_text_in_run_command(run_command)

    def _on_past_invocation_load(self) -> bool:
        past_invocations_path = os.path.join(self._paths.doc_past_invocations_path, self._image_data["name"])

        os.makedirs(past_invocations_path, exist_ok=True)

        file_path = filedialog.askopenfilename(initialdir=past_invocations_path, title="Choose a past invocation",
                                               filetypes=(("Script files", "*.sh"), ("All", "*.*")), parent=self)
        if file_path:
            version_prefix = f"{_RUN_COMMAND_VERSION_LINE_PREFIX}{self._image_data['name']}:"

            # Extracts text from selected archive
            with open(file_path, "r") as file:
                run_command = ""
                for line in file.readlines():
                    if len(run_command) == 0:  # First line
                        if line.startswith(version_prefix):
                            version = line.replace(version_prefix, "").strip()

                            if self._version_change_callback(version):
                                continue
                            else:
                                return False

                    run_command += line

                self._set_text_in_run_command(run_command.strip())

                return True

        return False


class _IORunPanel(_RunPanel):
    def __init__(self,
                 image_data,
                 paths: DocknrunPaths,
                 gui: bool = False,
                 version_change_callback: Callable[[str], bool] = lambda _: True,
                 **kwargs):
        super().__init__(image_data, paths, gui, fill_run_command=False,
                         version_change_callback=version_change_callback, **kwargs)

        self._input_data_widgets: dict[str, tuple[Entry, Button]] = {}

        # Component creation
        self._sv_mode: StringVar = StringVar(value="auto")
        self._lbl_mode: Label = self._builder.build_title_label(text="Edition mode:")
        self._frame_mode: Frame = Frame(self)
        self._rbt_auto: Radiobutton = self._builder.build_radio_button(master=self._frame_mode, text="Automatic",
                                                                       variable=self._sv_mode, value="auto")
        self._rbt_manual: Radiobutton = self._builder.build_radio_button(master=self._frame_mode, text="Manual",
                                                                         variable=self._sv_mode, value="manual")

        self._lbl_input: Label = self._builder.build_title_label(text="Input files")
        self._frame_input: Frame = Frame(self)
        if self._requires_input_data():
            for i, data_type in enumerate(self._input_data):
                default_input_path = self._build_path_for_input_data_type(data_type)

                ent_input: Entry = Entry(self._frame_input, readonlybackground="lightyellow")
                btn_input: Button = self._builder.build_button(master=self._frame_input,
                                                               text=f"Select a {data_type} file")
                ent_input.insert(0, default_input_path)
                ent_input.config(state="readonly")

                ent_input.grid(row=i, column=0, columnspan=3, sticky=EW)
                btn_input.grid(row=i, column=3, columnspan=1)

                self._input_data_widgets[data_type] = (ent_input, btn_input)
        else:
            self._lbl_no_input: Label = Label(self._frame_input, text="This image doesn't require input",
                                              font=("Arial", 14), bg="lightblue")
            self._lbl_no_input.grid(row=0, column=0, columnspan=4, sticky=NSEW)

        self._lbl_output: Label = self._builder.build_title_label(text="Output folder")
        self._ent_output: Entry = Entry(self, readonlybackground="lightyellow")
        self._btn_output: Button = self._builder.build_button(text="Select output folder")

        self._ent_output.insert(0, self._paths.output_folder_path)
        self._ent_output.config(state="readonly")

        if self._is_auto_mode():
            self._txt_run_command.config(state=DISABLED, background="lightyellow")

        # Component location
        for col in range(3):
            self._frame_input.grid_columnconfigure(col, weight=1)
        self._frame_input.grid_columnconfigure(3, weight=0)

        self._lbl_mode.grid(row=0, column=0, sticky=W)
        self._frame_mode.grid(row=0, column=1, columnspan=3, sticky=EW)
        self._lbl_input.grid(row=1, column=0, columnspan=4, sticky=W)
        self._frame_input.grid(row=2, column=0, columnspan=4, sticky=NSEW)
        self._lbl_output.grid(row=3, column=0, columnspan=4, sticky=W)
        self._ent_output.grid(row=4, column=0, columnspan=3, sticky=EW)
        self._btn_output.grid(row=4, column=3)

        self._rbt_auto.pack(side=LEFT, fill=X, expand=True)
        self._rbt_manual.pack(side=RIGHT, fill=X, expand=True)

        # Events
        self._trace_mode_id = self._sv_mode.trace_add("write", self._on_mode_change)

        # Input data files
        for data_type, (ent_input, btn_input) in self._input_data_widgets.items():
            btn_input.config(command=lambda dt=data_type: self._on_choose_input_file(dt))

        # Output data file
        self._btn_output.config(command=self._on_output_push)

        self._set_text_in_run_command(self._build_run_command())

    @property
    def _input_data(self) -> Optional[List[str]]:
        return self._image_data["input_data_type"] if "input_data_type" in self._image_data else None

    def _is_auto_mode(self) -> bool:
        return self._sv_mode.get() == "auto"

    def _build_path(self, sub_path: str) -> str:
        return os.path.join(self._paths.base_path, sub_path)

    def _build_default_path(self, sub_path: str) -> str:
        return f"{self._default_paths.base_path}/{sub_path}"  # Do not use os.path.join here! (/ separator must be used)

    def _build_path_for_input_data_type(self, data_type) -> str:
        return self._build_path(f"{data_type}File")

    def _build_default_path_for_input_data_type(self, data_type) -> str:
        return self._build_default_path(f"{data_type}File")

    def _count_input_data(self) -> int:
        return len(self._input_data) if self._input_data is not None else 0

    def _requires_input_data(self) -> bool:
        return self._count_input_data() > 0

    def _change_input_data(self, data_type: str, path: str) -> None:
        entry = self._input_data_widgets[data_type][0]
        entry.config(state=NORMAL)
        entry.delete(0, END)
        entry.insert(0, path)  # Insert the selected file path
        entry.config(state="readonly")

        self._set_text_in_run_command(self._build_run_command())

    def _change_output_data(self, output_data_path: str) -> None:
        self._ent_output.config(state=NORMAL)
        self._ent_output.delete(0, END)
        self._ent_output.insert(0, output_data_path)
        self._ent_output.config(state="readonly")

        self._set_text_in_run_command(self._build_run_command())

    def _build_run_command(self) -> str:
        run_command = super()._build_run_command()

        for data_type, (entry, _) in self._input_data_widgets.items():
            input_path = entry.get()
            run_command = run_command.replace(self._build_default_path_for_input_data_type(data_type), input_path)

        run_command = run_command.replace(self._default_paths.output_folder_path, self._ent_output.get())

        return run_command

    def _replace_text_in_run_command(self, to_replace: str, replacement: str) -> None:
        run_command = self.run_command

        run_command = run_command.replace(to_replace, replacement)

        self._set_text_in_run_command(run_command)

    def _on_test_data_invocation(self) -> None:
        super()._on_test_data_invocation()

        if self._is_auto_mode():
            self._sv_mode.set("manual")

    def _on_past_invocation_load(self) -> None:
        if super()._on_past_invocation_load():
            if self._is_auto_mode():
                self._sv_mode.set("manual")

    def _on_choose_input_file(self, data_type: str) -> None:
        input_path = filedialog.askopenfilename(parent=self, initialdir=self._paths.base_path)

        if input_path:
            self._change_input_data(data_type, input_path)

    def _on_output_push(self) -> None:
        output_path = filedialog.askdirectory(parent=self, initialdir=self._paths.base_path)

        if output_path:
            self._change_output_data(output_path)

    def _on_mode_change(self, *args) -> None:
        if self._is_auto_mode():
            if (not self._is_run_command_changed() or
                messagebox.askyesno("Confirm",
                                    "Switching to automatic mode will discard any changes done in 'Run Command'. Do you want to continue?",
                                    parent=self)):

                for entry, button in self._input_data_widgets.values():
                    entry.config(state="readonly")
                    button.config(state=NORMAL)

                self._ent_output.config(state="readonly")
                self._btn_output.config(state=NORMAL)

                self._set_text_in_run_command(self._build_run_command())
                self._txt_run_command.config(state=DISABLED, background="lightyellow")
            else:
                # Change cancelled
                self._sv_mode.trace_remove("write", self._trace_mode_id)
                self._sv_mode.set("manual")
                self._trace_mode_id = self._sv_mode.trace_add("write", self._on_mode_change)
        else:
            for entry, button in self._input_data_widgets.values():
                entry.config(state=DISABLED)
                button.config(state=DISABLED)

            self._ent_output.config(state=DISABLED)
            self._btn_output.config(state=DISABLED)

            self._txt_run_command.config(state=NORMAL, background="white")


class SecondaryWindow(Toplevel):
    def __init__(self, image_data, paths: DocknrunPaths, master=None, cnf=None, **kwargs):
        super().__init__(master, {} if cnf is None else cnf, **kwargs)

        self.title("Run Docker Image")

        self._image_data = image_data
        self._paths: DocknrunPaths = paths
        self._default_paths: DocknrunPaths = DocknrunPaths.build_default_paths()
        self._config: dict[str, str] = load_config_file(os.path.join(self._paths.base_path, "config"))
        self._image_versions: List[str] = self._load_image_versions()
        current_version: str = self._image_versions[-1]

        # Component creation
        self._frame: Frame = Frame(self)
        self._frame.pack(anchor=CENTER, fill=BOTH, expand=True, padx=20, pady=20)

        self._builder: _ComponentBuilder = _ComponentBuilder(self._frame)

        self._lbl_title: Label = Label(self._frame, text=image_data["name"], fg="black", font=("sans-serif", 25))

        self._sv_image_version: StringVar = StringVar(value=current_version)
        self._btn_menu_version: Button = self._builder.build_button(textvariable=self._sv_image_version)

        self._menu_version: Menu = Menu(self._frame, tearoff=0)
        self._menu_version_visible: bool = False
        for version in self._image_versions:
            self._menu_version.add_command(label=version, command=lambda v=version: self._on_change_version(v))

        self._btn_documentation: Button = self._builder.build_button(text="Open Documentation")
        self._btn_pegi3s: Button = self._builder.build_button(text="Open pegi3s")

        self._run_panel_container: Optional[Notebook | LabelFrame] = None
        self._run_panel: Optional[_RunPanel] = None
        if self._has_cli() and self._has_gui():
            self._run_panel_container: Notebook = Notebook(self._frame)

            tab_cli = _IORunPanel(self._image_data, self._paths, False,
                                  version_change_callback=self._on_change_version_by_loading_past_invocation,
                                  master=self._run_panel_container)
            tab_gui = _RunPanel(self._image_data, self._paths, True,
                                version_change_callback=self._on_change_version_by_loading_past_invocation,
                                master=self._run_panel_container)

            self._run_panel_container.add(tab_cli, text="CLI", padding=10)
            self._run_panel_container.add(tab_gui, text="GUI", padding=10)
        elif self._has_cli():
            self._run_panel_container: LabelFrame = self._builder.build_label_frame(text="CLI")
            self._run_panel = _IORunPanel(self._image_data, self._paths, False,
                                          version_change_callback=self._on_change_version_by_loading_past_invocation,
                                          master=self._run_panel_container)
            self._run_panel.pack(fill=BOTH, expand=True)
        elif self._has_gui():
            self._run_panel_container: LabelFrame = self._builder.build_label_frame(text="GUI")
            self._run_panel = _RunPanel(self._image_data, self._paths, True,
                                        version_change_callback=self._on_change_version_by_loading_past_invocation,
                                        master=self._run_panel_container)
            self._run_panel.pack(fill=BOTH, expand=True)
        else:
            raise RuntimeError("Image should have a GUI or a CLI")

        # Component location
        self._lbl_developer_notes: Label = self._builder.build_title_label(text="Developer Notes")
        self._txt_developer_notes: ScrolledText = self._builder.build_scrolled_text(background="lightyellow")

        self._lbl_user_notes: Label = self._builder.build_title_label(text="User Notes")
        self._txt_user_notes: ScrolledText = self._builder.build_scrolled_text()
        self._user_notes_save_job: Any = None

        self._btn_run: Button = self._builder.build_button(text="Run")

        self._btn_create_executable_file: Button = self._builder.build_button(text="Create executable file")

        for col in range(3):
            self._frame.grid_columnconfigure(col, weight=1)
        self._frame.grid_columnconfigure(3, weight=0)

        self._lbl_title.grid(row=0, column=0, rowspan=2, columnspan=4, pady=10, sticky=EW)
        self._btn_menu_version.grid(row=1, column=3, columnspan=1, sticky=E)
        self._btn_documentation.grid(row=2, column=0, pady=10, columnspan=2)
        self._btn_pegi3s.grid(row=2, column=2, pady=10, columnspan=2)
        self._run_panel_container.grid(row=3, column=0, columnspan=10, rowspan=4, sticky=NSEW)
        self._lbl_developer_notes.grid(row=7, column=0, columnspan=4, sticky=W)
        self._txt_developer_notes.grid(row=8, column=0, columnspan=3, sticky=NSEW)
        self._lbl_user_notes.grid(row=9, column=0, columnspan=4, sticky=W)
        self._txt_user_notes.grid(row=10, column=0, columnspan=3, sticky=NSEW)
        self._btn_run.grid(row=14, column=0, columnspan=2, pady=10)
        self._btn_create_executable_file.grid(row=14, column=2, columnspan=2, pady=10)

        # Version
        self._btn_menu_version.config(command=self._on_show_menu_version)

        # Manual and pegi3s buttons
        manual_url = generate_manual_url(image_data)
        if manual_url is None:
            self._btn_documentation.config(state=DISABLED)
        else:
            self._btn_documentation.config(command=lambda: webbrowser.open(manual_url))

        pegi3s_url = generate_pegi3s_url(image_data)
        if manual_url is None:
            self._btn_pegi3s.config(state=DISABLED)
        else:
            self._btn_pegi3s.config(command=lambda: webbrowser.open(pegi3s_url))

        # User notes
        self._txt_user_notes.insert("1.0", self._load_user_notes())
        self._txt_user_notes.bind("<FocusOut>", self._on_user_notes_change)
        self._txt_user_notes.bind("<KeyRelease>", lambda event: self._on_user_notes_change(500))

        # Developer notes
        self._txt_developer_notes.insert(END, self._build_developer_notes())
        self._txt_developer_notes.config(state=DISABLED)

        # Create executable file
        self._btn_create_executable_file.config(command=self._on_create_executable_file)

        # Run command
        self._btn_run.config(command=self._on_run_command)

    @property
    def _image_name(self) -> str:
        return self._image_data["name"]

    @property
    def _image_version(self):
        return self._sv_image_version.get()

    @property
    def _host_dir(self) -> str:
        return self._config["dir"]

    def _get_config_path(self, path_name: str, default_path: str) -> str:
        if path_name in self._config and len(self._config[path_name].strip()) > 0:
            return os.path.join(self._paths.base_path, self._config[path_name].strip())
        else:
            return os.path.join(self._paths.base_path, default_path)

    def _has_gui(self) -> bool:
        return self._image_data["gui"]

    def _has_cli(self) -> bool:
        return len(self._image_data["usual_invocation_specific"].strip()) > 0

    def _is_gui_selected(self) -> bool:
        if isinstance(self._run_panel_container, LabelFrame):
            return self._has_gui()
        elif isinstance(self._run_panel_container, Notebook):
            return self._run_panel_container.tab(self._run_panel_container.select(), "text") == "GUI"
        else:
            raise RuntimeError("Unexpected type for self._run_panel_container")

    def _is_cli_selected(self) -> bool:
        if isinstance(self._run_panel_container, LabelFrame):
            return self._has_cli()
        elif isinstance(self._run_panel_container, Notebook):
            return self._run_panel_container.tab(self._run_panel_container.select(), "text") == "CLI"
        else:
            raise RuntimeError("Unexpected type for self._run_panel_container")

    def _get_active_run_panel(self) -> _RunPanel:
        if isinstance(self._run_panel_container, LabelFrame):
            return self._run_panel
        elif isinstance(self._run_panel_container, Notebook):
            return self._run_panel_container.nametowidget(self._run_panel_container.select())
        else:
            raise RuntimeError("Unexpected type for self._run_panel_container")

    def _load_user_notes(self) -> str:
        file_path = self._build_user_notes_path()

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        else:
            return ""

    def _save_user_notes(self) -> None:
        file_path = self._build_user_notes_path()

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self._txt_user_notes.get("1.0", END))

    def _build_user_notes_path(self):
        return os.path.join(self._paths.doc_user_notes_path, self._image_name + ".txt")

    def _build_developer_notes(self) -> str:
        developer_notes = ""

        if len(self._image_data["comments"]) > 0:
            developer_notes = "Comments:\n  - " + "\n  - ".join(self._image_data["comments"])
            developer_notes += "\n"

        if len(self._image_data["bug_found"]) > 0:
            dn_bug = ""

            for bug in self._image_data["bug_found"]:
                if len(bug["description"].strip()) == 0:
                    dn_bug += f"  - {bug['version']}\n"
                else:
                    dn_bug += f"  - {bug['version']}: {bug['description']}\n"

            developer_notes += f"\nA bug has been found in the following versions:\n{dn_bug}"

        if len(self._image_data["not_working"]) > 0:
            dn_not_working = ", ".join(self._image_data["not_working"])

            developer_notes += f"\nThese versions no longer work: {dn_not_working}"

        if len(self._image_data["no_longer_tested"]) > 0:
            dn_no_longer_tested = ", ".join(self._image_data["no_longer_tested"])

            developer_notes += f"\nThe following versions are no longer tested: {dn_no_longer_tested}"

        if len(self._image_data["recommended"]) > 0:
            dn_recommended_last_tested = ""

            for recommended in self._image_data["recommended"]:
                if len(recommended["date"].strip()) == 0:
                    dn_recommended_last_tested += f"  - {recommended['version']}\n"
                else:
                    dn_recommended_last_tested += f"  - {recommended['version']} [{recommended['date']}]\n"

            developer_notes += f"\nThe recommended version has been last tested on:\n{dn_recommended_last_tested}"

        if self._image_data["podman"] == "untested":
            developer_notes += "\nImage untested for podman"
        elif self._image_data["podman"] == "tested":
            developer_notes += "\nImage tested for podman"
        else:
            developer_notes += "\nImage doesn't work for podman"

        if self._image_data["singularity"] == "untested":
            developer_notes += "\nImage untested for singularity"
        elif self._image_data["singularity"] == "tested":
            developer_notes += "\nImage tested for singularity"
        else:
            developer_notes += "\nImage doesn't work for singularity"

        return developer_notes.strip()

    def _load_image_versions(self) -> List[str]:
        response = requests.get("http://evolution6.i3s.up.pt/static/pegi3s/dockerfiles/images-and-tags.txt")
        if response.status_code == 200:
            versions = find_image_versions(self._image_name, response.text)
            if "latest" in versions:
                versions.remove("latest")

            # return [f"{self._image_name}:{version}" for version in versions if version != "latest"]
            return versions
        else:
            raise IOError("Couldn't download image versions")

    def _create_executable_file(self, creation_time: Optional[str] = None, run_command: Optional[str] = None) -> None:
        self._create_script_file(self._paths.doc_executable_files_path, creation_time, run_command)

    def _create_latest_invocation_file(self, creation_time: Optional[str] = None,
                                       run_command: Optional[str] = None) -> None:
        self._create_script_file(self._paths.doc_past_invocations_path, creation_time, run_command)

    def _create_script_file(self, scripts_path: str, creation_time: Optional[str] = None,
                            run_command: Optional[str] = None) -> None:
        if creation_time is None:
            creation_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        if run_command is None:
            run_command = self._get_active_run_panel().run_command

        executables_path = os.path.join(self._paths.base_path, scripts_path, self._image_name)
        os.makedirs(executables_path, exist_ok=True)

        interface_type = "CLI" if self._is_cli_selected() else "GUI"
        executable_file_name = f"{self._image_name}_{interface_type}_{creation_time}.sh"

        with open(os.path.join(executables_path, executable_file_name), "w") as executable_file:
            executable_file.write(run_command)

    def _build_docker_run_command(self, run_command: Optional[str] = None) -> str:
        if run_command is None:
            run_command = self._get_active_run_panel().run_command

        if self._is_cli_selected():
            docker_invocation = self._image_data["invocation_general"].strip() + ":" + self._image_version
        else:
            docker_invocation = f"{_GUI_INVOCATION_GENERAL}{self._image_name}:{self._image_version}"

        docker_invocation = docker_invocation.replace(_PATH_DEFAULT_DOCKER_COMMAND_DATA_DIR, self._config["dir"])
        run_command = run_command.replace(self._paths.base_path, self._default_paths.base_path)

        return docker_invocation + " " + run_command

    def _on_change_version_by_loading_past_invocation(self, version: str) -> bool:
        current_version = self._image_version

        if version == current_version:
            return True
        else:
            if version in self._image_versions:
                response = messagebox.askyesnocancel("Change version",
                                                     f"This past invocation was configured for the {version} version of {self._image_data['name']}. Do you want to switch to this version?",
                                                     parent=self)
                if response is None:
                    return False
                else:
                    if response:
                        self._sv_image_version.set(version)

                    return True
            else:
                return messagebox.askokcancel("Unknown version",
                                              f"This past invocation was configured for the {version} version of {self._image_data['name']}, which is not registered. Do you want to continue loading this invocation?",
                                              parent=self)


    def _on_change_version(self, version: str) -> None:
        self._sv_image_version.set(version)
        self._menu_version_visible = False

    def _on_show_menu_version(self) -> None:
        if self._menu_version_visible:
            self._menu_version.unpost()
            self._menu_version_visible = False
        else:
            self._menu_version.post(self._btn_menu_version.winfo_rootx(),
                                    self._btn_menu_version.winfo_rooty() + self._btn_menu_version.winfo_height())
            self._menu_version_visible = True

    def _on_user_notes_change(self, event_or_delay) -> None:
        if self._user_notes_save_job is not None:
            self._txt_user_notes.after_cancel(self._user_notes_save_job)
            self._user_notes_save_job = None

        if type(event_or_delay) == "int":
            self._user_notes_save_job = self.after(event_or_delay, self._save_user_notes)
        else:
            self._save_user_notes()

    def _on_create_executable_file(self) -> None:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        run_command = self._get_active_run_panel().run_command
        docker_run_command = self._build_docker_run_command(run_command)

        run_command = f"{_RUN_COMMAND_VERSION_LINE_PREFIX}{self._image_name}:{self._image_version}\n\n{run_command}\n"

        self._create_executable_file(current_time, docker_run_command)
        self._create_latest_invocation_file(current_time, run_command)

        messagebox.showinfo("Create executable", "Executable file and past invocation file successfully created.",
                            parent=self)

    def _on_run_command(self) -> None:
        run_command = self._get_active_run_panel().run_command
        docker_run_command = self._build_docker_run_command(run_command)

        self._create_latest_invocation_file(run_command=run_command)

        RunWindow(self._image_name, docker_run_command, master=self)


if __name__ == "__main__":
    with open("metadata.json", "r") as metadata:
        image_datas = json.load(metadata)
        image_data = next(image_data for image_data in image_datas if image_data["name"] == "seda")

        SecondaryWindow(image_data, "/opt").wait_window()
