from __future__ import annotations

import tkinter as tk

import customtkinter as ctk


class GlassCard(ctk.CTkFrame):
    def __init__(self, master, title: str, subtitle: str | None = None, **kwargs):
        super().__init__(
            master,
            corner_radius=20,
            fg_color="#0e141d",
            border_width=1,
            border_color="#203241",
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            header,
            text=title,
            font=("Consolas", 17, "bold"),
            text_color="#e7fff0",
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                header,
                text=subtitle,
                font=("Segoe UI", 11),
                text_color="#77cfe1",
            )
            self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))


class MetricCard(ctk.CTkFrame):
    def __init__(self, master, label: str, value: str, accent: str = "#6dff95", **kwargs):
        super().__init__(
            master,
            corner_radius=16,
            fg_color="#0a1118",
            border_width=1,
            border_color="#203241",
            **kwargs,
        )
        self.accent = accent
        self.grid_columnconfigure(0, weight=1)

        self.label_widget = ctk.CTkLabel(
            self,
            text=label,
            font=("Segoe UI", 11),
            text_color="#8bb0c2",
        )
        self.label_widget.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 0))

        self.value_widget = ctk.CTkLabel(
            self,
            text=value,
            font=("Consolas", 18, "bold"),
            text_color=accent,
        )
        self.value_widget.grid(row=1, column=0, sticky="w", padx=14, pady=(4, 12))

    def set_value(self, value: str, color: str | None = None) -> None:
        self.value_widget.configure(text=value)
        if color:
            self.value_widget.configure(text_color=color)
        else:
            self.value_widget.configure(text_color=self.accent)


class CheckRow(ctk.CTkFrame):
    def __init__(self, master, label: str, **kwargs):
        super().__init__(
            master,
            corner_radius=12,
            fg_color="#091017",
            border_width=1,
            border_color="#172531",
            **kwargs,
        )
        self.dot = ctk.CTkLabel(
            self,
            text="●",
            font=("Segoe UI", 14, "bold"),
            text_color="#ff6b81",
        )
        self.dot.grid(row=0, column=0, padx=(12, 8), pady=10, sticky="w")

        self.label_widget = ctk.CTkLabel(
            self,
            text=label,
            font=("Segoe UI", 12),
            text_color="#d8eef2",
        )
        self.label_widget.grid(row=0, column=1, padx=(0, 12), pady=10, sticky="w")

        self.grid_columnconfigure(1, weight=1)

    def set_status(self, passed: bool) -> None:
        if passed:
            self.dot.configure(text_color="#62ff9d")
            self.label_widget.configure(text_color="#e9fff0")
        else:
            self.dot.configure(text_color="#ff6b81")
            self.label_widget.configure(text_color="#9db1bc")

    def set_neutral(self) -> None:
        self.dot.configure(text_color="#5e7f8c")
        self.label_widget.configure(text_color="#9db1bc")


class ActionButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        defaults = {
            "corner_radius": 14,
            "fg_color": "#0e2b24",
            "hover_color": "#123c31",
            "border_width": 1,
            "border_color": "#2b6f61",
            "text_color": "#dffff0",
            "font": ("Segoe UI", 12, "bold"),
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)


class AnimatedProgress(ctk.CTkFrame):
    def __init__(self, master, height: int = 18, **kwargs):
        super().__init__(
            master,
            corner_radius=999,
            fg_color="#071019",
            border_width=1,
            border_color="#18313f",
            height=height,
            **kwargs,
        )
        self.grid_propagate(False)
        self.canvas = tk.Canvas(
            self,
            height=height - 2,
            highlightthickness=0,
            bg="#071019",
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True, padx=1, pady=1)
        self.value = 0.0
        self.target = 0.0
        self.after_id = None
        self._color = "#63ff9f"
        self.bind("<Configure>", self._redraw)
        self.canvas.bind("<Configure>", self._redraw)

    def set_color(self, color: str) -> None:
        self._color = color
        self._redraw()

    def set_value(self, target: float) -> None:
        self.target = max(0.0, min(1.0, target))
        if self.after_id:
            self.after_cancel(self.after_id)
        self._animate()

    def _animate(self) -> None:
        delta = self.target - self.value
        if abs(delta) < 0.01:
            self.value = self.target
            self._redraw()
            return
        self.value += delta * 0.18
        self._redraw()
        self.after_id = self.after(16, self._animate)

    def _redraw(self, event=None) -> None:
        self.canvas.delete("all")
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        fill_width = max(8, int(width * self.value))
        self.canvas.create_rectangle(
            0,
            0,
            fill_width,
            height,
            outline="",
            fill=self._color,
        )
        self.canvas.create_text(
            max(fill_width - 8, 18),
            height // 2,
            text=f"{int(self.value * 100)}%",
            fill="#03100a",
            font=("Consolas", 10, "bold"),
            anchor="e",
        )


class TerminalLog(ctk.CTkTextbox):
    LEVELS = {
        "INFO": ("[INFO]", "#7fd9ff"),
        "WARNING": ("[WARNING]", "#ffd36d"),
        "SECURE": ("[SECURE]", "#6cff9a"),
        "SCAN": ("[SCAN]", "#78f0d0"),
    }

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=14,
            fg_color="#05090d",
            border_width=1,
            border_color="#18313f",
            text_color="#d4f8e4",
            wrap="word",
            **kwargs,
        )
        self._textbox.configure(
            bg="#05090d",
            fg="#d4f8e4",
            insertbackground="#77ffad",
            font=("Consolas", 10),
            relief="flat",
            highlightthickness=0,
            padx=10,
            pady=10,
        )
        for level, (_, color) in self.LEVELS.items():
            self._textbox.tag_config(level, foreground=color)
        self.configure(state="disabled")

    def write(self, level: str, message: str) -> None:
        level = level.upper()
        prefix, _ = self.LEVELS.get(level, ("[INFO]", "#7fd9ff"))
        self.configure(state="normal")
        self._textbox.insert("end", f"{prefix} {message}\n", level if level in self.LEVELS else "INFO")
        self._textbox.see("end")
        self.configure(state="disabled")
