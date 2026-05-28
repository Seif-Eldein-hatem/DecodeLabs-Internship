from __future__ import annotations

import math
import random
import string
import tkinter as tk

import customtkinter as ctk

from core.checker import analyze_password
from core.generator import generate_password
from core.hashing import sha256_hash
from ui.components import ActionButton, AnimatedProgress, CheckRow, GlassCard, MetricCard, TerminalLog
from utils.helpers import ensure_assets


class SecurePassAnalyzerApp(ctk.CTk):
    MATRIX_CHARS = string.ascii_letters + string.digits + "!@#$%^&*+-=/\\|"
    ANALYSIS_DEBOUNCE_MS = 550
    MATRIX_FRAME_MS = 180
    TYPING_FRAME_MS = 200

    def __init__(self):
        ensure_assets()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        super().__init__()

        self.title("SecurePass Analyzer")
        self.geometry("1540x930")
        self.minsize(1280, 820)
        self.configure(fg_color="#05080d")

        self._analysis_after = None
        self._copy_feedback_after = None
        self._typing_job = None
        self._matrix_job = None
        self._loading_job = None
        self._loading_step = 0
        self._matrix_columns = []
        self._matrix_chars = []
        self._scan_message_index = 0

        self._build_background()
        self._build_layout()
        self._set_idle_state()
        self._show_loading_overlay()
        self._start_matrix()
        self._start_typing_animation()

    def _build_background(self):
        self.matrix_canvas = tk.Canvas(self, bg="#05080d", highlightthickness=0, bd=0)
        self.matrix_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._handle_resize)

    def _build_layout(self):
        self.shell = ctk.CTkFrame(self, fg_color="#071019", corner_radius=0)
        self.shell.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.shell.grid_columnconfigure(0, weight=1)
        self.shell.grid_rowconfigure(0, weight=1)

        self.content = ctk.CTkScrollableFrame(
            self.shell,
            fg_color="#071019",
            corner_radius=26,
            border_width=1,
            border_color="#13212d",
        )
        self.content.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)
        self.content.grid_columnconfigure(0, weight=0, minsize=295)
        self.content.grid_columnconfigure(1, weight=1, minsize=760)
        self.content.grid_columnconfigure(2, weight=0, minsize=390)

        self._build_left_panel()
        self._build_center_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        left = ctk.CTkFrame(
            self.content,
            fg_color="#0b111a",
            corner_radius=22,
            border_width=1,
            border_color="#1a2a38",
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(18, 10), pady=18)
        left.configure(width=295)
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)

        logo_wrap = ctk.CTkFrame(left, fg_color="#08121a", corner_radius=20, border_width=1, border_color="#1b3c2d")
        logo_wrap.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 12))
        logo_wrap.grid_columnconfigure(0, weight=1)

        self.logo = ctk.CTkLabel(
            logo_wrap,
            text="SECUREPASS",
            font=("Consolas", 24, "bold"),
            text_color="#66ff99",
        )
        self.logo.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 0))

        self.brand = ctk.CTkLabel(
            logo_wrap,
            text="ANALYZER",
            font=("Consolas", 24, "bold"),
            text_color="#7ce7ff",
        )
        self.brand.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 4))

        self.tagline = ctk.CTkLabel(
            logo_wrap,
            text="Initializing security engine...",
            font=("Segoe UI", 11),
            text_color="#9dc9d8",
        )
        self.tagline.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 14))

        status_card = GlassCard(left, "System Status", "Live cyber defense indicators")
        status_card.grid(row=1, column=0, sticky="ew", padx=18, pady=12)
        status_card.grid_columnconfigure(0, weight=1)

        self.system_status = self._status_pill(status_card, "Engine Armed", "#6cff9a")
        self.system_status.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.real_time_status_card = self._status_pill(status_card, "Real-time Scan", "#78f0d0")
        self.real_time_status_card.grid(row=2, column=0, sticky="ew", padx=16, pady=10)
        self.real_time_status = self.real_time_status_card.status_label
        self.hash_status = self._status_pill(status_card, "SHA-256 Ready", "#7fd9ff")
        self.hash_status.grid(row=3, column=0, sticky="ew", padx=16, pady=(10, 16))

        features = GlassCard(left, "Feature Matrix", "Portfolio-grade security tooling")
        features.grid(row=2, column=0, sticky="nsew", padx=18, pady=12)
        features.grid_columnconfigure(0, weight=1)

        for index, text in enumerate(
            [
                "Live password scoring",
                "Crack-time estimation",
                "Common password detection",
                "Generator and copy tools",
                "Terminal activity logs",
            ]
        ):
            item = ctk.CTkLabel(
                features,
                text=f"▸ {text}",
                font=("Segoe UI", 12),
                text_color="#d7eef1",
                anchor="w",
            )
            item.grid(row=index + 1, column=0, sticky="ew", padx=16, pady=(0, 8))

        note = ctk.CTkLabel(
            left,
            text="Cybersecurity desktop UX built by Seif Eldein.",
            font=("Segoe UI", 11),
            text_color="#7da1b3",
            wraplength=250,
            justify="left",
        )
        note.grid(row=3, column=0, sticky="ew", padx=22, pady=(12, 18))

        left.grid_rowconfigure(2, weight=1)

    def _build_center_panel(self):
        center = ctk.CTkFrame(
            self.content,
            fg_color="#081019",
            corner_radius=22,
            border_width=1,
            border_color="#1a2a38",
        )
        center.grid(row=0, column=1, sticky="nsew", padx=10, pady=18)
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(4, weight=1)

        header = ctk.CTkFrame(center, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(20, 8))
        header.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(
            header,
            text="SecurePass Analyzer",
            font=("Consolas", 28, "bold"),
            text_color="#ecfff4",
        )
        self.header_title.grid(row=0, column=0, sticky="w")

        self.header_subtitle = ctk.CTkLabel(
            header,
            text="Advanced password threat intelligence and strength scoring",
            font=("Segoe UI", 12),
            text_color="#76d3e6",
        )
        self.header_subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        input_card = GlassCard(center, "Live Analyzer", "Type a password to trigger instant security telemetry")
        input_card.grid(row=1, column=0, sticky="ew", padx=18, pady=10)
        input_card.grid_columnconfigure(0, weight=1)
        input_card.grid_columnconfigure(1, weight=0)
        input_card.grid_columnconfigure(2, weight=0)

        self.password_var = tk.StringVar()
        self.password_var.trace_add("write", self._schedule_analysis)

        self.password_entry = ctk.CTkEntry(
            input_card,
            textvariable=self.password_var,
            height=46,
            width=520,
            corner_radius=14,
            fg_color="#071019",
            border_width=1,
            border_color="#1d3341",
            text_color="#f1fff4",
            placeholder_text="Enter a password to scan...",
            font=("Segoe UI", 13),
            show="*",
        )
        self.password_entry.grid(row=1, column=0, sticky="ew", padx=(18, 10), pady=(2, 10))

        self.show_password = False
        self.toggle_button = ActionButton(
            input_card,
            text="Show",
            width=96,
            height=46,
            command=self._toggle_password_visibility,
        )
        self.toggle_button.grid(row=1, column=1, sticky="e", padx=(0, 18), pady=(2, 10))

        self.copy_input_button = ActionButton(
            input_card,
            text="Copy",
            width=96,
            height=46,
            command=self._copy_input_password,
        )
        self.copy_input_button.grid(row=1, column=2, sticky="e", padx=(0, 18), pady=(2, 10))

        self.scan_state = ctk.CTkLabel(
            input_card,
            text="Scanning idle",
            font=("Consolas", 11),
            text_color="#7fd9ff",
        )
        self.scan_state.grid(row=2, column=0, columnspan=3, sticky="w", padx=18, pady=(0, 12))

        meter_card = GlassCard(center, "Security Meter", "Animated classification and confidence level")
        meter_card.grid(row=2, column=0, sticky="ew", padx=18, pady=10)
        meter_card.grid_columnconfigure(0, weight=1)

        self.meter_label = ctk.CTkLabel(
            meter_card,
            text="Weak",
            font=("Consolas", 18, "bold"),
            text_color="#ff6b81",
        )
        self.meter_label.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 8))

        self.progress = AnimatedProgress(meter_card, height=18)
        self.progress.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))

        self.score_badge = ctk.CTkLabel(
            meter_card,
            text="Score: 0/100",
            font=("Segoe UI", 12),
            text_color="#93bacb",
        )
        self.score_badge.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 16))

        checks_card = GlassCard(center, "Security Validation", "Core checks and policy flags")
        checks_card.grid(row=3, column=0, sticky="ew", padx=18, pady=10)
        checks_card.grid_columnconfigure(0, weight=1)

        self.check_rows: list[CheckRow] = []
        for idx, label in enumerate(
            [
                "Length >= 12",
                "Uppercase letters",
                "Lowercase letters",
                "Numbers",
                "Symbols",
                "No repeated characters",
                "No sequential patterns",
                "Not a common password",
            ]
        ):
            row = CheckRow(checks_card, label)
            row.grid(row=idx + 1, column=0, sticky="ew", padx=16, pady=5)
            self.check_rows.append(row)

        self.suggestions_card = GlassCard(center, "Security Suggestions", "Guidance to harden the password")
        self.suggestions_card.grid(row=4, column=0, sticky="nsew", padx=18, pady=10)
        self.suggestions_card.grid_columnconfigure(0, weight=1)
        self.suggestions_text = ctk.CTkLabel(
            self.suggestions_card,
            text="Enter a password to receive live recommendations.",
            font=("Segoe UI", 12),
            text_color="#d7eef1",
            wraplength=820,
            justify="left",
        )
        self.suggestions_text.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))

        generator = GlassCard(center, "Password Generator", "Create strong credentials and copy them instantly")
        generator.grid(row=5, column=0, sticky="ew", padx=18, pady=(10, 18))
        generator.grid_columnconfigure(0, weight=1)
        generator.grid_columnconfigure(1, weight=0)

        self.generator_length = tk.IntVar(value=18)
        self.include_symbols = tk.BooleanVar(value=True)

        length_label = ctk.CTkLabel(
            generator,
            text="Length",
            font=("Segoe UI", 12),
            text_color="#9dc9d8",
        )
        length_label.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 4))

        self.length_value = ctk.CTkLabel(
            generator,
            text="18",
            font=("Consolas", 14, "bold"),
            text_color="#6cff9a",
        )
        self.length_value.grid(row=1, column=1, sticky="e", padx=18, pady=(0, 4))

        self.length_slider = ctk.CTkSlider(
            generator,
            from_=8,
            to=32,
            number_of_steps=24,
            command=self._update_generator_length,
            progress_color="#6cff9a",
            button_color="#6cff9a",
            button_hover_color="#7ce7ff",
        )
        self.length_slider.set(18)
        self.length_slider.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10))

        self.symbol_switch = ctk.CTkSwitch(
            generator,
            text="Include symbols",
            variable=self.include_symbols,
            progress_color="#6cff9a",
            button_color="#6cff9a",
            button_hover_color="#7ce7ff",
            font=("Segoe UI", 12),
        )
        self.symbol_switch.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 10))

        self.generated_password_var = tk.StringVar(value="")
        self.generated_password = ctk.CTkEntry(
            generator,
            textvariable=self.generated_password_var,
            height=42,
            width=520,
            corner_radius=14,
            fg_color="#071019",
            border_width=1,
            border_color="#1d3341",
            text_color="#f1fff4",
            font=("Consolas", 12),
        )
        self.generated_password.grid(row=4, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10))

        gen_buttons = ctk.CTkFrame(generator, fg_color="transparent")
        gen_buttons.grid(row=5, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 16))
        gen_buttons.grid_columnconfigure(0, weight=1)
        gen_buttons.grid_columnconfigure(1, weight=1)

        self.generate_button = ActionButton(gen_buttons, text="Generate Secure Password", command=self._generate_password)
        self.generate_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.copy_generated_button = ActionButton(gen_buttons, text="Copy", command=self._copy_generated_password)
        self.copy_generated_button.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _build_right_panel(self):
        right = ctk.CTkFrame(
            self.content,
            fg_color="#0b111a",
            corner_radius=22,
            border_width=1,
            border_color="#1a2a38",
        )
        right.grid(row=0, column=2, sticky="nsew", padx=(10, 18), pady=18)
        right.configure(width=390)
        right.grid_propagate(False)
        right.grid_columnconfigure(0, weight=1)

        analytics = GlassCard(right, "Analytics Panel", "Live telemetry and forensic outputs")
        analytics.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        analytics.grid_columnconfigure(0, weight=1)
        analytics.grid_columnconfigure(1, weight=1)

        self.score_card = MetricCard(analytics, "Security Score", "0", accent="#6cff9a")
        self.score_card.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=(0, 8))
        self.entropy_card = MetricCard(analytics, "Entropy", "0.00 bits", accent="#7fd9ff")
        self.entropy_card.grid(row=1, column=1, sticky="ew", padx=(8, 16), pady=(0, 8))
        self.threat_card = MetricCard(analytics, "Threat Level", "Minimal", accent="#ffd36d")
        self.threat_card.grid(row=2, column=0, sticky="ew", padx=(16, 8), pady=(0, 16))
        self.complexity_card = MetricCard(analytics, "Complexity", "Low", accent="#78f0d0")
        self.complexity_card.grid(row=2, column=1, sticky="ew", padx=(8, 16), pady=(0, 16))

        crack = GlassCard(right, "Crack Time Estimate", "Brute force resistance indicator")
        crack.grid(row=1, column=0, sticky="ew", padx=18, pady=10)
        crack.grid_columnconfigure(0, weight=1)

        self.crack_time_label = ctk.CTkLabel(
            crack,
            text="—",
            font=("Consolas", 22, "bold"),
            text_color="#6cff9a",
        )
        self.crack_time_label.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 6))

        self.crack_detail = ctk.CTkLabel(
            crack,
            text="Estimate updates in real time as you type.",
            font=("Segoe UI", 11),
            text_color="#8fb6c8",
            wraplength=300,
            justify="left",
        )
        self.crack_detail.grid(row=2, column=0, sticky="w", padx=18, pady=(0, 16))

        hash_card = GlassCard(right, "SHA-256 Hash Preview", "One-way hashing demo of the current password")
        hash_card.grid(row=2, column=0, sticky="ew", padx=18, pady=10)
        hash_card.grid_columnconfigure(0, weight=1)

        self.hash_preview = ctk.CTkTextbox(
            hash_card,
            height=110,
            width=340,
            corner_radius=14,
            fg_color="#05090d",
            border_width=1,
            border_color="#18313f",
            text_color="#d4f8e4",
            font=("Consolas", 10),
        )
        self.hash_preview.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.hash_preview.insert("0.0", "SHA-256 output will appear here.")
        self.hash_preview.configure(state="disabled")

        self.copy_hash_button = ActionButton(hash_card, text="Copy Hash", command=self._copy_hash)
        self.copy_hash_button.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 16))

        logs_card = GlassCard(right, "Activity Logs", "Terminal-style scan output")
        logs_card.grid(row=3, column=0, sticky="nsew", padx=18, pady=(10, 18))
        logs_card.grid_columnconfigure(0, weight=1)
        logs_card.grid_rowconfigure(1, weight=1)

        self.logs = TerminalLog(logs_card, height=250)
        self.logs.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))

        self.logs.write("INFO", "SecurePass Analyzer session started.")
        self.logs.write("SCAN", "Waiting for password input.")

    def _status_pill(self, master, text: str, accent: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            master,
            corner_radius=14,
            fg_color="#0a1118",
            border_width=1,
            border_color="#18313f",
        )
        frame.grid_columnconfigure(1, weight=1)

        dot = ctk.CTkLabel(frame, text="●", font=("Segoe UI", 14, "bold"), text_color=accent)
        dot.grid(row=0, column=0, padx=(12, 8), pady=10, sticky="w")

        label = ctk.CTkLabel(frame, text=text, font=("Segoe UI", 12), text_color="#d9eff1")
        label.grid(row=0, column=1, padx=(0, 12), pady=10, sticky="w")
        frame.status_label = label
        return frame

    def _show_loading_overlay(self):
        self.loading_overlay = ctk.CTkFrame(self, fg_color="#020507", corner_radius=0)
        self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        card = ctk.CTkFrame(
            self.loading_overlay,
            width=420,
            height=180,
            corner_radius=24,
            fg_color="#0b111a",
            border_width=1,
            border_color="#1f3a2f",
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            card,
            text="Booting SecurePass Analyzer",
            font=("Consolas", 18, "bold"),
            text_color="#6cff9a",
        )
        label.grid(row=0, column=0, padx=18, pady=(22, 8))

        sub = ctk.CTkLabel(
            card,
            text="Loading cyber defense modules...",
            font=("Segoe UI", 11),
            text_color="#8fb6c8",
        )
        sub.grid(row=1, column=0, padx=18, pady=(0, 10))

        self.loading_progress = AnimatedProgress(card, height=16)
        self.loading_progress.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        self.loading_progress.set_color("#6cff9a")
        self._loading_step = 0
        self._advance_loading()

    def _advance_loading(self):
        self._loading_step += 1
        self.loading_progress.set_value(min(self._loading_step / 24, 1.0))
        if self._loading_step < 24:
            self.after(30, self._advance_loading)
        else:
            self.after(150, self.loading_overlay.destroy)

    def _start_matrix(self):
        width = max(self.winfo_width(), 1200)
        self._matrix_columns = []
        if width <= 0:
            width = 1200
        step = 34
        count = max(1, width // step)
        for index in range(count):
            self._matrix_columns.append({
                "x": index * step,
                "y": random.randint(-600, 0),
                "speed": random.randint(3, 8),
                "char": random.choice(self.MATRIX_CHARS),
            })
        self._matrix_tick()

    def _matrix_tick(self):
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)
        self.matrix_canvas.delete("all")

        if not self._matrix_columns or len(self._matrix_columns) < max(1, width // 34) - 1:
            self._start_matrix()
            return

        for column in self._matrix_columns:
            x = column["x"]
            y = column["y"]
            char = column["char"]
            speed = column["speed"]
            self.matrix_canvas.create_text(x, y, text=char, fill="#6cff9a", font=("Consolas", 11, "bold"))

            column["y"] = y + speed
            if column["y"] > height + 30:
                column["y"] = random.randint(-250, -20)
                column["speed"] = random.randint(3, 8)
            if random.random() < 0.08:
                column["char"] = random.choice(self.MATRIX_CHARS)

        self._matrix_job = self.after(self.MATRIX_FRAME_MS, self._matrix_tick)

    def _handle_resize(self, event=None):
        if not event:
            return
        self.matrix_canvas.configure(width=event.width, height=event.height)

    def _start_typing_animation(self):
        phrases = [
            "Live password threat detection",
            "Entropy analysis and security scoring",
            "Modern cyber defense dashboard",
        ]
        phrase = phrases[self._scan_message_index % len(phrases)]
        visible = min((self._typing_job or 0) % (len(phrase) + 6), len(phrase))
        if visible == 0:
            self.tagline.configure(text="Initializing security engine...")
        else:
            self.tagline.configure(text=phrase[:visible] + ("_" if visible < len(phrase) else ""))
        self._typing_job = (self._typing_job or 0) + 1
        if self._typing_job % (len(phrase) + 10) == 0:
            self._scan_message_index += 1
        self.after(self.TYPING_FRAME_MS, self._start_typing_animation)

    def _toggle_password_visibility(self):
        self.show_password = not self.show_password
        self.password_entry.configure(show="" if self.show_password else "*")
        self.toggle_button.configure(text="Hide" if self.show_password else "Show")

    def _update_generator_length(self, value):
        rounded = int(round(float(value)))
        self.generator_length.set(rounded)
        self.length_value.configure(text=str(rounded))

    def _generate_password(self):
        password = generate_password(
            length=self.generator_length.get(),
            include_lowercase=True,
            include_uppercase=True,
            include_digits=True,
            include_symbols=self.include_symbols.get(),
        )
        self.generated_password_var.set(password)
        self.logs.write("SECURE", "Strong password generated.")

    def _copy_generated_password(self):
        password = self.generated_password_var.get()
        if not password:
            self.logs.write("WARNING", "No generated password available to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(password)
        self.logs.write("INFO", "Generated password copied to clipboard.")

    def _copy_hash(self):
        hash_text = self._hash_value if hasattr(self, "_hash_value") else ""
        if not hash_text:
            self.logs.write("WARNING", "No hash available to copy.")
            self._flash_copy_feedback("Copy Hash")
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(hash_text)
            self.update_idletasks()
            self.logs.write("INFO", "SHA-256 hash copied to clipboard.")
            self._flash_copy_feedback("Copied!")
        except tk.TclError as exc:
            self.logs.write("WARNING", f"Clipboard copy failed: {exc}")
            self._flash_copy_feedback("Copy Hash")

    def _copy_input_password(self):
        password = self.password_var.get()
        if not password:
            self.logs.write("WARNING", "No password entered to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(password)
        self.logs.write("INFO", "Current password copied to clipboard.")

    def _schedule_analysis(self, *_):
        if self._analysis_after:
            self.after_cancel(self._analysis_after)
        self.scan_state.configure(text="Scanning live input...")
        self._analysis_after = self.after(self.ANALYSIS_DEBOUNCE_MS, self._run_analysis)

    def _run_analysis(self):
        password = self.password_var.get()
        if not password:
            self._set_idle_state()
            return
        analysis = analyze_password(password)
        self._apply_analysis(analysis)

    def _apply_analysis(self, analysis):
        score_ratio = analysis.score / 100
        color_map = {
            "Weak": "#ff6b81",
            "Medium": "#ffd36d",
            "Strong": "#7ce7ff",
            "Very Strong": "#6cff9a",
        }
        label_color = color_map.get(analysis.strength, "#6cff9a")

        self.meter_label.configure(text=analysis.strength, text_color=label_color)
        self.progress.set_color(label_color)
        self.progress.set_value(score_ratio)
        self.score_badge.configure(text=f"Score: {analysis.score}/100")
        self.score_card.set_value(str(analysis.score), color=label_color)
        self.entropy_card.set_value(f"{analysis.entropy:.2f} bits", color="#7fd9ff")
        self.threat_card.set_value(analysis.threat_level, color=self._threat_color(analysis.threat_level))
        self.complexity_card.set_value(analysis.complexity_rating, color=self._complexity_color(analysis.complexity_rating))
        self.crack_time_label.configure(text=analysis.crack_time)
        self.crack_detail.configure(text=f"Estimated brute-force resistance at 1 billion guesses per second.")

        for row, (label, passed) in zip(self.check_rows, analysis.checks.items()):
            row.set_status(passed)

        if analysis.suggestions:
            self.suggestions_text.configure(text="\n".join(f"- {item}" for item in analysis.suggestions))
        else:
            self.suggestions_text.configure(text="No further improvements required.")

        self._hash_value = sha256_hash(analysis.password) if analysis.password else ""
        self._update_hash_preview(self._hash_value)
        self._update_logs(analysis)
        self.scan_state.configure(text=f"Scan complete | {analysis.strength} classification")
        self._update_real_time_indicator(analysis)

    def _set_idle_state(self):
        for row in getattr(self, "check_rows", []):
            row.set_neutral()
        self.meter_label.configure(text="Idle", text_color="#7fd9ff")
        self.progress.set_color("#7fd9ff")
        self.progress.set_value(0.0)
        self.score_badge.configure(text="Score: 0/100")
        self.score_card.set_value("0", color="#7fd9ff")
        self.entropy_card.set_value("0.00 bits", color="#7fd9ff")
        self.threat_card.set_value("Minimal", color="#6cff9a")
        self.complexity_card.set_value("Low", color="#78f0d0")
        self.crack_time_label.configure(text="—")
        self.crack_detail.configure(text="Enter a password to calculate brute-force resistance.")
        self.suggestions_text.configure(text="Enter a password to receive live recommendations.")
        self._hash_value = ""
        self._update_hash_preview("")
        self.scan_state.configure(text="Scanning idle")
        self.real_time_status.configure(text="Real-time Scan Idle")

    def _update_hash_preview(self, hash_value: str):
        self.hash_preview.configure(state="normal")
        self.hash_preview.delete("1.0", "end")
        self.hash_preview.insert("1.0", hash_value if hash_value else "SHA-256 output will appear here.")
        self.hash_preview.configure(state="disabled")

    def _update_logs(self, analysis):
        self.logs.write("INFO", "Password scanned.")
        if analysis.common_password:
            self.logs.write("WARNING", "Common password detected.")
        if analysis.repeated_chars:
            self.logs.write("WARNING", "Repeated character pattern flagged.")
        if analysis.sequential_chars:
            self.logs.write("WARNING", "Sequential pattern detected.")
        if analysis.score >= 85:
            self.logs.write("SECURE", "Very strong password confirmed.")
        elif analysis.score >= 60:
            self.logs.write("SECURE", "Strong password confirmed.")
        else:
            self.logs.write("WARNING", "Weak or moderate password detected.")

    def _update_real_time_indicator(self, analysis):
        if analysis.score >= 85:
            self.real_time_status.configure(text="Real-time Scan Active")
        elif analysis.score >= 60:
            self.real_time_status.configure(text="Real-time Scan Calibrated")
        else:
            self.real_time_status.configure(text="Real-time Scan Alert")

    def _flash_copy_feedback(self, message: str):
        self.copy_hash_button.configure(text=message)
        if self._copy_feedback_after:
            self.after_cancel(self._copy_feedback_after)
        self._copy_feedback_after = self.after(1400, lambda: self.copy_hash_button.configure(text="Copy Hash"))

    def _threat_color(self, threat: str) -> str:
        mapping = {
            "Critical": "#ff6b81",
            "Elevated": "#ffd36d",
            "Guarded": "#7ce7ff",
            "Minimal": "#6cff9a",
        }
        return mapping.get(threat, "#7ce7ff")

    def _complexity_color(self, complexity: str) -> str:
        mapping = {
            "Low": "#ff6b81",
            "Moderate": "#ffd36d",
            "High": "#7ce7ff",
            "Elite": "#6cff9a",
        }
        return mapping.get(complexity, "#7ce7ff")
