from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import tkinter as tk
from tkinter import ttk


def _try_import_real_customtkinter():
    current_dir = Path(__file__).resolve().parent
    original_path = list(sys.path)
    placeholder = sys.modules.get(__name__)

    try:
        sys.modules.pop(__name__, None)
        filtered_path = []
        for entry in original_path:
            resolved = Path(entry or os.getcwd()).resolve()
            if resolved != current_dir:
                filtered_path.append(entry)
        sys.path = filtered_path
        return importlib.import_module("customtkinter")
    except Exception:
        return None
    finally:
        sys.path = original_path
        if placeholder is not None and __name__ not in sys.modules:
            sys.modules[__name__] = placeholder


_REAL_CUSTOMTKINTER = _try_import_real_customtkinter()


def _normalize_color(master, value, fallback="#05080d"):
    if value in (None, "", "transparent"):
        return getattr(master, "_fg_color", fallback)
    return value


def set_appearance_mode(_mode: str) -> None:
    return None


def set_default_color_theme(_theme: str) -> None:
    return None


class CTk(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fg_color = "#05080d"
        self.configure(bg=self._fg_color)

    def configure(self, cnf=None, **kwargs):
        cnf = dict(cnf or {})
        cnf.update(kwargs)
        if "fg_color" in cnf:
            cnf["bg"] = _normalize_color(self.master, cnf.pop("fg_color"), getattr(self, "_fg_color", "#05080d"))
        if "bg_color" in cnf:
            cnf["bg"] = cnf.pop("bg_color")
        return super().configure(cnf)

    config = configure


class CTkFrame(tk.Frame):
    def __init__(
        self,
        master=None,
        fg_color: str = "#0b111a",
        corner_radius: int = 0,
        border_width: int = 0,
        border_color: str = "#000000",
        **kwargs,
    ):
        fg_color = _normalize_color(master, fg_color)
        super().__init__(
            master,
            bg=fg_color,
            highlightbackground=border_color,
            highlightcolor=border_color,
            highlightthickness=border_width,
            bd=0,
            **kwargs,
        )
        self._fg_color = fg_color

    def configure(self, cnf=None, **kwargs):
        cnf = dict(cnf or {})
        cnf.update(kwargs)
        if "fg_color" in cnf:
            color = _normalize_color(self.master, cnf.pop("fg_color"), getattr(self, "_fg_color", "#05080d"))
            self._fg_color = color
            cnf["bg"] = color
        if "border_color" in cnf:
            cnf["highlightbackground"] = cnf.pop("border_color")
            cnf["highlightcolor"] = cnf["highlightbackground"]
        if "border_width" in cnf:
            cnf["highlightthickness"] = cnf.pop("border_width")
        return super().configure(cnf)

    config = configure


class CTkLabel(tk.Label):
    def __init__(self, master=None, text: str = "", text_color: str = "#ffffff", **kwargs):
        self._text_color = text_color
        self._fg_color = _normalize_color(master, kwargs.pop("fg_color", getattr(master, "_fg_color", "#05080d")))
        super().__init__(master, text=text, fg=text_color, bg=self._fg_color, bd=0, **kwargs)

    def configure(self, cnf=None, **kwargs):
        cnf = dict(cnf or {})
        cnf.update(kwargs)
        if "text_color" in cnf:
            self._text_color = cnf.pop("text_color")
            cnf["fg"] = self._text_color
        if "fg_color" in cnf:
            self._fg_color = _normalize_color(self.master, cnf.pop("fg_color"), self._fg_color)
            cnf["bg"] = self._fg_color
        return super().configure(cnf)

    config = configure


class CTkButton(tk.Button):
    def __init__(
        self,
        master=None,
        text: str = "",
        command=None,
        fg_color: str = "#173326",
        hover_color: str = "#214538",
        text_color: str = "#ffffff",
        border_width: int = 0,
        border_color: str = "#000000",
        corner_radius: int = 0,
        **kwargs,
    ):
        fg_color = _normalize_color(master, fg_color)
        super().__init__(
            master,
            text=text,
            command=command,
            bg=fg_color,
            fg=text_color,
            activebackground=hover_color,
            activeforeground=text_color,
            bd=border_width,
            highlightthickness=0,
            relief="flat",
            **kwargs,
        )

    def configure(self, cnf=None, **kwargs):
        cnf = dict(cnf or {})
        cnf.update(kwargs)
        if "text_color" in cnf:
            cnf["fg"] = cnf.pop("text_color")
            cnf["activeforeground"] = cnf["fg"]
        if "fg_color" in cnf:
            color = _normalize_color(self.master, cnf.pop("fg_color"), getattr(self.master, "_fg_color", "#05080d"))
            cnf["bg"] = color
        if "hover_color" in cnf:
            cnf["activebackground"] = cnf.pop("hover_color")
        return super().configure(cnf)

    config = configure


class CTkEntry(tk.Entry):
    def __init__(
        self,
        master=None,
        textvariable=None,
        placeholder_text: str | None = None,
        show: str = "",
        fg_color: str = "#081019",
        text_color: str = "#ffffff",
        **kwargs,
    ):
        fg_color = _normalize_color(master, fg_color)
        super().__init__(
            master,
            textvariable=textvariable,
            show=show,
            bg=fg_color,
            fg=text_color,
            insertbackground=text_color,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#1d3341",
            highlightcolor="#6cff9a",
            **kwargs,
        )
        self._placeholder_text = placeholder_text

    def configure(self, cnf=None, **kwargs):
        cnf = dict(cnf or {})
        cnf.update(kwargs)
        if "fg_color" in cnf:
            cnf["bg"] = _normalize_color(self.master, cnf.pop("fg_color"), getattr(self.master, "_fg_color", "#05080d"))
        if "text_color" in cnf:
            cnf["fg"] = cnf.pop("text_color")
            cnf["insertbackground"] = cnf["fg"]
        return super().configure(cnf)

    config = configure


class CTkSlider(tk.Scale):
    def __init__(
        self,
        master=None,
        from_: int = 0,
        to: int = 100,
        number_of_steps: int | None = None,
        command=None,
        progress_color: str = "#6cff9a",
        button_color: str = "#6cff9a",
        button_hover_color: str = "#7ce7ff",
        **kwargs,
    ):
        resolution = 1
        if number_of_steps and number_of_steps > 0:
            resolution = max(1, int(abs(to - from_) / number_of_steps))
        self._command = command
        bg_color = _normalize_color(master, getattr(master, "_fg_color", "#05080d"))
        super().__init__(
            master,
            from_=from_,
            to=to,
            orient="horizontal",
            resolution=resolution,
            showvalue=False,
            troughcolor="#0a1118",
            bg=bg_color,
            fg=progress_color,
            highlightthickness=0,
            bd=0,
            command=self._on_change,
            **kwargs,
        )
        self._value = from_

    def configure(self, cnf=None, **kwargs):
        cnf = dict(cnf or {})
        cnf.update(kwargs)
        if "progress_color" in cnf:
            cnf["fg"] = cnf.pop("progress_color")
        return super().configure(cnf)

    config = configure

    def _on_change(self, value):
        self._value = float(value)
        if self._command:
            self._command(value)

    def set(self, value):
        self._value = float(value)
        super().set(value)
        if self._command:
            self._command(value)


class CTkSwitch(tk.Checkbutton):
    def __init__(
        self,
        master=None,
        text: str = "",
        variable=None,
        progress_color: str = "#6cff9a",
        button_color: str = "#6cff9a",
        button_hover_color: str = "#7ce7ff",
        font=None,
        **kwargs,
    ):
        bg_color = _normalize_color(master, getattr(master, "_fg_color", "#05080d"))
        super().__init__(
            master,
            text=text,
            variable=variable,
            bg=bg_color,
            fg="#d7eef1",
            activebackground=bg_color,
            activeforeground="#ffffff",
            selectcolor="#0a1118",
            bd=0,
            highlightthickness=0,
            font=font,
            **kwargs,
        )

    def configure(self, cnf=None, **kwargs):
        cnf = dict(cnf or {})
        cnf.update(kwargs)
        if "text_color" in cnf:
            cnf["fg"] = cnf.pop("text_color")
        if "fg_color" in cnf:
            cnf["bg"] = _normalize_color(self.master, cnf.pop("fg_color"), getattr(self.master, "_fg_color", "#05080d"))
            cnf["activebackground"] = cnf["bg"]
        return super().configure(cnf)

    config = configure


class CTkTextbox(tk.Frame):
    def __init__(
        self,
        master=None,
        height: int = 120,
        corner_radius: int = 0,
        fg_color: str = "#05090d",
        border_width: int = 0,
        border_color: str = "#000000",
        text_color: str = "#ffffff",
        wrap: str = "word",
        font=None,
        **kwargs,
    ):
        fg_color = _normalize_color(master, fg_color)
        super().__init__(
            master,
            bg=fg_color,
            highlightbackground=border_color,
            highlightcolor=border_color,
            highlightthickness=border_width,
            bd=0,
            **kwargs,
        )
        self._textbox = tk.Text(
            self,
            height=height,
            wrap=wrap,
            bg=fg_color,
            fg=text_color,
            insertbackground=text_color,
            relief="flat",
            bd=0,
            font=font,
            highlightthickness=0,
        )
        self._textbox.pack(fill="both", expand=True)

    def insert(self, *args, **kwargs):
        return self._textbox.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._textbox.delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self._textbox.get(*args, **kwargs)

    def configure(self, **kwargs):
        if "text_color" in kwargs:
            kwargs["fg"] = kwargs.pop("text_color")
        if "fg_color" in kwargs:
            color = _normalize_color(self.master, kwargs.pop("fg_color"), getattr(self.master, "_fg_color", "#05080d"))
            super().configure(bg=color)
            self._textbox.configure(bg=color)
        if "border_color" in kwargs:
            color = kwargs.pop("border_color")
            super().configure(highlightbackground=color, highlightcolor=color)
        if "border_width" in kwargs:
            width = kwargs.pop("border_width")
            super().configure(highlightthickness=width)
        self._textbox.configure(**kwargs)

    config = configure

    def see(self, *args, **kwargs):
        return self._textbox.see(*args, **kwargs)

    def tag_configure(self, *args, **kwargs):
        return self._textbox.tag_configure(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._textbox, name)


class CTkProgressBar(tk.Frame):
    pass


class CTkScrollableFrame(CTkFrame):
    pass


if _REAL_CUSTOMTKINTER is not None:
    for name in [
        "CTk",
        "CTkFrame",
        "CTkLabel",
        "CTkButton",
        "CTkEntry",
        "CTkSlider",
        "CTkSwitch",
        "CTkTextbox",
        "CTkProgressBar",
        "CTkScrollableFrame",
        "set_appearance_mode",
        "set_default_color_theme",
    ]:
        if hasattr(_REAL_CUSTOMTKINTER, name):
            globals()[name] = getattr(_REAL_CUSTOMTKINTER, name)
