"""
EFM (Edit Folder Manager) - Version 6.0
Modern Windows Desktop Application
Built with CustomTkinter
"""

import os
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

try:
    from . import core as efm_core
except ImportError:
    try:
        from src.efm import core as efm_core
    except ImportError:
        import core as efm_core

# Set default appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Theme Colors
ACCENT_COLOR = "#0ea5e9"       # Sky blue
ACCENT_HOVER = "#0284c7"
BG_DARK = "#0f172a"            # Slate 900
CARD_BG = "#1e293b"            # Slate 800
CARD_BORDER = "#334155"        # Slate 700
TEXT_MUTED = "#94a3b8"         # Slate 400
CLIENT_COLOR = "#38bdf8"       # Light blue
PERSONAL_COLOR = "#a855f7"     # Purple
SUCCESS_COLOR = "#22c55e"      # Green


class EFMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load configurations
        self.config = efm_core.load_config()
        self.base_dir = self.config.get("base_dir") or efm_core.get_default_base_dir()
        ctk.set_appearance_mode(self.config.get("appearance_mode", "dark"))

        # Window Setup
        self.title("EFM 6.0 - Edit Folder Manager")
        self.geometry("1100x720")
        self.minsize(920, 620)

        # Set Window Icon if exists
        self.icon_path = efm_core.get_resource_path("efm_icon.ico")
        if self.icon_path.exists():
            try:
                self.iconbitmap(str(self.icon_path))
            except Exception:
                pass

        # State Variables
        self.current_view = "dashboard"
        self.ongoing_projects = []
        self.selected_move_project = None

        # Build UI Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_content_area()

        # Load initial data
        self.refresh_projects_data()
        self.show_view("dashboard")

    # -------------------------------------------------------------------------
    # Layout: Sidebar & Content Area
    # -------------------------------------------------------------------------
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # Logo / Title
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(24, 20), sticky="ew")

        # Load icon for header if available
        png_icon_path = efm_core.get_resource_path("efm_icon.png")
        if png_icon_path.exists():
            try:
                pil_img = Image.open(png_icon_path).resize((38, 38), Image.Resampling.LANCZOS)
                self.logo_ctk_img = ctk.CTkImage(pil_img, size=(38, 38))
                icon_lbl = ctk.CTkLabel(logo_frame, image=self.logo_ctk_img, text="")
                icon_lbl.pack(side="left", padx=(0, 10))
            except Exception:
                pass

        title_lbl = ctk.CTkLabel(
            logo_frame, 
            text="EFM 6.0", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_lbl.pack(side="left")

        subtitle_lbl = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Edit Folder Manager", 
            font=ctk.CTkFont(size=11), 
            text_color=TEXT_MUTED
        )
        subtitle_lbl.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "🏠  Home / Dashboard"),
            ("projects", "📁  Active Projects"),
            ("new_project", "➕  New Project"),
            ("move_project", "📦  Move Project"),
            ("file_sorter", "🗂️  File Sorter"),
            ("settings", "⚙️  Settings")
        ]

        for idx, (view_id, label_text) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=label_text,
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold"),
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray25"),
                command=lambda v=view_id: self.show_view(v)
            )
            btn.grid(row=idx, column=0, padx=14, pady=4, sticky="ew")
            self.nav_buttons[view_id] = btn

        # Bottom info in sidebar
        bottom_box = ctk.CTkFrame(self.sidebar_frame, fg_color=("gray85", "#1e293b"), corner_radius=10)
        bottom_box.grid(row=8, column=0, padx=14, pady=16, sticky="ew")

        base_info_lbl = ctk.CTkLabel(
            bottom_box, 
            text="Base Directory:", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED
        )
        base_info_lbl.pack(anchor="w", padx=10, pady=(8, 2))

        # Show truncated base dir
        dir_name = os.path.basename(self.base_dir) or self.base_dir
        self.sidebar_base_lbl = ctk.CTkLabel(
            bottom_box, 
            text=f"📁 {dir_name}", 
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.sidebar_base_lbl.pack(anchor="w", padx=10, pady=(0, 4))

        open_root_btn = ctk.CTkButton(
            bottom_box,
            text="Open Folder",
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color=("gray70", "#334155"),
            hover_color=("gray60", "#475569"),
            command=lambda: efm_core.open_folder(self.base_dir)
        )
        open_root_btn.pack(fill="x", padx=10, pady=(2, 8))

    def create_content_area(self):
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Dictionary of frames for each view
        self.views = {
            "dashboard": self.build_dashboard_view(),
            "projects": self.build_projects_view(),
            "new_project": self.build_new_project_view(),
            "move_project": self.build_move_project_view(),
            "file_sorter": self.build_file_sorter_view(),
            "settings": self.build_settings_view()
        }

    def show_view(self, view_name):
        self.current_view = view_name

        # Highlight active navigation button
        for v_id, btn in self.nav_buttons.items():
            if v_id == view_name:
                btn.configure(
                    fg_color=(ACCENT_COLOR, ACCENT_COLOR),
                    text_color="#ffffff"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray10", "gray90")
                )

        # Hide all view frames and display the chosen one
        for v_id, frame in self.views.items():
            if v_id == view_name:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()

        # Specific page update triggers
        if view_name == "dashboard":
            self.update_dashboard_stats()
        elif view_name == "projects":
            self.refresh_projects_list_ui()
        elif view_name == "move_project":
            self.update_move_project_dropdown()

    def refresh_projects_data(self):
        """Fetches active ongoing projects from disk."""
        self.ongoing_projects = efm_core.list_ongoing_projects(self.base_dir)

    # -------------------------------------------------------------------------
    # VIEW 1: Dashboard (Matches After Effects Render1.png Vision)
    # -------------------------------------------------------------------------
    def build_dashboard_view(self):
        frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        # Hero Banner
        hero_frame = ctk.CTkFrame(frame, fg_color="transparent")
        hero_frame.pack(fill="x", pady=(10, 20))

        welcome_title = ctk.CTkLabel(
            hero_frame,
            text="WELCOME !",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        welcome_title.pack(anchor="center", pady=(10, 4))

        subtitle = ctk.CTkLabel(
            hero_frame,
            text="What do you want to do today?.....",
            font=ctk.CTkFont(size=16),
            text_color=TEXT_MUTED
        )
        subtitle.pack(anchor="center", pady=(0, 25))

        # 3 Main Action Cards (Matching Render1.png mockup)
        cards_container = ctk.CTkFrame(frame, fg_color="transparent")
        cards_container.pack(fill="x", pady=10)
        cards_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        # 1. Open Project Card
        card_open = ctk.CTkFrame(cards_container, corner_radius=18, fg_color=("gray85", "#1e293b"), border_width=1, border_color=CARD_BORDER)
        card_open.grid(row=0, column=0, padx=12, pady=10, sticky="nsew")

        ctk.CTkLabel(card_open, text="📁", font=ctk.CTkFont(size=42)).pack(pady=(28, 8))
        ctk.CTkLabel(card_open, text="Open\nProject", font=ctk.CTkFont(size=22, weight="bold"), justify="center").pack(pady=4)
        
        self.dash_open_count_lbl = ctk.CTkLabel(card_open, text="0 Active Projects", font=ctk.CTkFont(size=13), text_color=TEXT_MUTED)
        self.dash_open_count_lbl.pack(pady=4)

        btn_open = ctk.CTkButton(
            card_open,
            text="Browse Projects",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            corner_radius=10,
            fg_color=("gray70", "#334155"),
            hover_color=("gray60", "#475569"),
            command=lambda: self.show_view("projects")
        )
        btn_open.pack(fill="x", padx=24, pady=(16, 28))

        # 2. New Project Card
        card_new = ctk.CTkFrame(cards_container, corner_radius=18, fg_color=("gray85", "#1e293b"), border_width=1, border_color=CARD_BORDER)
        card_new.grid(row=0, column=1, padx=12, pady=10, sticky="nsew")

        ctk.CTkLabel(card_new, text="✨", font=ctk.CTkFont(size=42)).pack(pady=(28, 8))
        ctk.CTkLabel(card_new, text="New\nProject", font=ctk.CTkFont(size=22, weight="bold"), justify="center").pack(pady=4)
        
        ctk.CTkLabel(card_new, text="Quick Structure Setup", font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(pady=4)

        btn_new = ctk.CTkButton(
            card_new,
            text="Create Project",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            corner_radius=10,
            fg_color=("gray70", "#334155"),
            hover_color=("gray60", "#475569"),
            command=lambda: self.show_view("new_project")
        )
        btn_new.pack(fill="x", padx=24, pady=(16, 28))

        # 3. Move Project Card (Prominent cyan accent matching Render1.png)
        card_move = ctk.CTkFrame(cards_container, corner_radius=18, fg_color=(ACCENT_COLOR, ACCENT_COLOR))
        card_move.grid(row=0, column=2, padx=12, pady=10, sticky="nsew")

        ctk.CTkLabel(card_move, text="📦", font=ctk.CTkFont(size=42)).pack(pady=(28, 8))
        ctk.CTkLabel(card_move, text="Move\nProject", font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff", justify="center").pack(pady=4)
        
        ctk.CTkLabel(card_move, text="Archive & Organize", font=ctk.CTkFont(size=13), text_color="#e0f2fe").pack(pady=4)

        btn_move = ctk.CTkButton(
            card_move,
            text="Move Project",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            corner_radius=10,
            fg_color="#0369a1",
            hover_color="#075985",
            text_color="#ffffff",
            command=lambda: self.show_view("move_project")
        )
        btn_move.pack(fill="x", padx=24, pady=(16, 28))

        # Quick Overview Section
        quick_frame = ctk.CTkFrame(frame, corner_radius=14, fg_color=("gray90", "#1e293b"))
        quick_frame.pack(fill="x", pady=25, padx=12)

        q_title = ctk.CTkLabel(quick_frame, text="Current Workspace Summary", font=ctk.CTkFont(size=16, weight="bold"))
        q_title.pack(anchor="w", padx=20, pady=(16, 10))

        self.dash_stats_lbl = ctk.CTkLabel(
            quick_frame, 
            text="Loading summary...", 
            font=ctk.CTkFont(size=14),
            justify="left",
            text_color=TEXT_MUTED
        )
        self.dash_stats_lbl.pack(anchor="w", padx=20, pady=(0, 16))

        return frame

    def update_dashboard_stats(self):
        self.refresh_projects_data()
        client_count = sum(1 for p in self.ongoing_projects if p["category"] == "Client")
        personal_count = sum(1 for p in self.ongoing_projects if p["category"] == "Personal")
        total = len(self.ongoing_projects)

        self.dash_open_count_lbl.configure(text=f"{total} Active Projects")
        self.dash_stats_lbl.configure(
            text=f"• Active Client Projects:  {client_count}\n"
                 f"• Active Personal Projects: {personal_count}\n"
                 f"• Base Storage: {self.base_dir}"
        )

    # -------------------------------------------------------------------------
    # VIEW 2: Active Projects List
    # -------------------------------------------------------------------------
    def build_projects_view(self):
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        # Header with Search and Filter
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(header_frame, text="Active Ongoing Projects", font=ctk.CTkFont(size=24, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w")

        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray75", "#334155"),
            hover_color=("gray65", "#475569"),
            command=self.refresh_projects_list_ui
        )
        refresh_btn.grid(row=0, column=1, sticky="e")

        # Search Bar & Filter Segmented Button
        bar_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bar_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        bar_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            bar_frame, 
            placeholder_text="🔍 Search ongoing projects by name...",
            height=38,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_projects_list())

        self.filter_segmented = ctk.CTkSegmentedButton(
            bar_frame,
            values=["All", "Client", "Personal"],
            command=lambda v: self.filter_projects_list()
        )
        self.filter_segmented.set("All")
        self.filter_segmented.grid(row=0, column=1, sticky="e")

        # Scrollable Cards List
        self.projects_scroll = ctk.CTkScrollableFrame(frame, corner_radius=12, fg_color=("gray95", "#131d2e"))
        self.projects_scroll.grid(row=2, column=0, sticky="nsew")
        self.projects_scroll.grid_columnconfigure(0, weight=1)

        # Status toast message at bottom
        self.project_status_lbl = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.project_status_lbl.grid(row=3, column=0, sticky="w", pady=(8, 0))

        return frame

    def refresh_projects_list_ui(self):
        self.refresh_projects_data()
        self.filter_projects_list()

    def filter_projects_list(self):
        # Clear existing cards
        for widget in self.projects_scroll.winfo_children():
            widget.destroy()

        search_query = self.search_entry.get().strip().lower() if hasattr(self, 'search_entry') else ""
        selected_filter = self.filter_segmented.get() if hasattr(self, 'filter_segmented') else "All"

        filtered = []
        for p in self.ongoing_projects:
            if selected_filter != "All" and p["category"] != selected_filter:
                continue
            if search_query and search_query not in p["name"].lower():
                continue
            filtered.append(p)

        if not filtered:
            empty_frame = ctk.CTkFrame(self.projects_scroll, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, pady=60)

            ctk.CTkLabel(empty_frame, text="📂", font=ctk.CTkFont(size=48)).pack(pady=(0, 10))
            msg = "No ongoing projects found matching criteria." if search_query or selected_filter != "All" else "No ongoing projects currently found."
            ctk.CTkLabel(empty_frame, text=msg, font=ctk.CTkFont(size=16), text_color=TEXT_MUTED).pack(pady=4)

            create_btn = ctk.CTkButton(
                empty_frame,
                text="Create New Project",
                fg_color=ACCENT_COLOR,
                hover_color=ACCENT_HOVER,
                command=lambda: self.show_view("new_project")
            )
            create_btn.pack(pady=15)
            return

        for project in filtered:
            self.create_project_card(project)

    def create_project_card(self, project):
        card = ctk.CTkFrame(self.projects_scroll, corner_radius=12, fg_color=("gray90", "#1e293b"), border_width=1, border_color=CARD_BORDER)
        card.pack(fill="x", padx=6, pady=6)
        card.grid_columnconfigure(1, weight=1)

        # Icon & Badge Frame
        left_frame = ctk.CTkFrame(card, fg_color="transparent", width=120)
        left_frame.grid(row=0, column=0, padx=16, pady=14, sticky="w")

        is_client = (project["category"] == "Client")
        badge_color = CLIENT_COLOR if is_client else PERSONAL_COLOR
        badge_text = "CLIENT" if is_client else "PERSONAL"

        cat_badge = ctk.CTkLabel(
            left_frame,
            text=f"  {badge_text}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=badge_color,
            text_color="#000000" if is_client else "#ffffff",
            corner_radius=6
        )
        cat_badge.pack(anchor="w", pady=(0, 4))

        date_lbl = ctk.CTkLabel(
            left_frame,
            text=project["date_display"],
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        date_lbl.pack(anchor="w")

        # Project Info Frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=10, pady=14, sticky="ew")

        name_lbl = ctk.CTkLabel(
            info_frame,
            text=project["name"],
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        name_lbl.pack(fill="x", anchor="w")

        path_lbl = ctk.CTkLabel(
            info_frame,
            text=project["path"],
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        path_lbl.pack(fill="x", anchor="w", pady=(2, 0))

        # Actions Frame
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=0, column=2, padx=16, pady=14, sticky="e")

        # Open in Explorer button
        open_btn = ctk.CTkButton(
            actions_frame,
            text="📂 Open",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray75", "#334155"),
            hover_color=("gray65", "#475569"),
            command=lambda p=project: self.handle_open_project(p)
        )
        open_btn.pack(side="left", padx=4)

        # Sort Files button
        sort_btn = ctk.CTkButton(
            actions_frame,
            text="🧹 Sort Files",
            width=90,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray75", "#334155"),
            hover_color=("gray65", "#475569"),
            command=lambda p=project: self.handle_sort_project_files(p)
        )
        sort_btn.pack(side="left", padx=4)

        # Move button
        move_btn = ctk.CTkButton(
            actions_frame,
            text="📦 Move",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=lambda p=project: self.prepare_move_project(p)
        )
        move_btn.pack(side="left", padx=4)

    def handle_open_project(self, project):
        # Check auto-sort config
        if self.config.get("auto_sort_on_open", True):
            summary = efm_core.auto_sort_project(project["path"])
            if summary["total_moved"] > 0:
                self.project_status_lbl.configure(
                    text=f"✓ Sorted {summary['total_moved']} files (Raw: {summary['raw_moved']}, Stock: {summary['stock_moved']})",
                    text_color=SUCCESS_COLOR
                )
            else:
                self.project_status_lbl.configure(text=f"Opened '{project['name']}' in Explorer", text_color=TEXT_MUTED)
        else:
            self.project_status_lbl.configure(text=f"Opened '{project['name']}' in Explorer", text_color=TEXT_MUTED)

        efm_core.open_folder(project["path"])

    def handle_sort_project_files(self, project):
        summary = efm_core.auto_sort_project(project["path"])
        if summary["total_moved"] > 0:
            details_str = ", ".join(summary["details"][:4])
            self.project_status_lbl.configure(
                text=f"✓ Organized {summary['total_moved']} files in '{project['name']}' ({details_str})",
                text_color=SUCCESS_COLOR
            )
            messagebox.showinfo("Files Sorted", f"Organized {summary['total_moved']} files into subfolders!\n\n" + "\n".join(summary["details"][:10]))
        else:
            self.project_status_lbl.configure(text=f"Raw & Stock folders are clean in '{project['name']}' (no files to sort)", text_color=TEXT_MUTED)
            messagebox.showinfo("Files Sorted", "No loose files found in Raw or Stock to sort.")

    def prepare_move_project(self, project):
        self.selected_move_project = project
        self.show_view("move_project")

    # -------------------------------------------------------------------------
    # VIEW 3: Create New Project
    # -------------------------------------------------------------------------
    def build_new_project_view(self):
        frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        # Header
        title_lbl = ctk.CTkLabel(frame, text="Create New Project", font=ctk.CTkFont(size=26, weight="bold"))
        title_lbl.pack(anchor="w", pady=(10, 2))

        sub_lbl = ctk.CTkLabel(
            frame, 
            text="Initializes standardized folders (Exported, Project File, Concept.txt, Raw, Stock, Reference).",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        )
        sub_lbl.pack(anchor="w", pady=(0, 20))

        # Main Card Form
        form_card = ctk.CTkFrame(frame, corner_radius=14, fg_color=("gray90", "#1e293b"), border_width=1, border_color=CARD_BORDER)
        form_card.pack(fill="x", pady=10)
        form_card.grid_columnconfigure(0, weight=1)

        # Project Name Input
        name_title = ctk.CTkLabel(form_card, text="Project Name", font=ctk.CTkFont(size=14, weight="bold"))
        name_title.pack(anchor="w", padx=24, pady=(20, 6))

        self.new_proj_name_entry = ctk.CTkEntry(
            form_card,
            placeholder_text="e.g. Nike Commercial, Travel Vlog Ep 1, Corporate Ad...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.new_proj_name_entry.pack(fill="x", padx=24, pady=(0, 16))
        self.new_proj_name_entry.bind("<KeyRelease>", lambda e: self.update_new_project_preview())

        # Category Selector (Client vs Personal)
        cat_title = ctk.CTkLabel(form_card, text="Project Category", font=ctk.CTkFont(size=14, weight="bold"))
        cat_title.pack(anchor="w", padx=24, pady=(4, 6))

        self.new_proj_cat_var = ctk.StringVar(value="Client")
        cat_segmented = ctk.CTkSegmentedButton(
            form_card,
            values=["Client Project", "Personal Project"],
            variable=self.new_proj_cat_var,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            command=lambda v: self.update_new_project_preview()
        )
        cat_segmented.set("Client Project")
        cat_segmented.pack(fill="x", padx=24, pady=(0, 20))

        # Live Preview Box
        preview_box = ctk.CTkFrame(form_card, corner_radius=10, fg_color=("gray80", "#131d2e"), border_width=1, border_color=CARD_BORDER)
        preview_box.pack(fill="x", padx=24, pady=(0, 20))

        preview_header = ctk.CTkLabel(preview_box, text="📁 Destination Preview", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED)
        preview_header.pack(anchor="w", padx=16, pady=(12, 4))

        self.new_proj_preview_lbl = ctk.CTkLabel(
            preview_box,
            text="",
            font=ctk.CTkFont(size=13, family="Consolas"),
            justify="left",
            anchor="w",
            wraplength=700
        )
        self.new_proj_preview_lbl.pack(fill="x", padx=16, pady=(0, 12))

        # Checkboxes for extra actions
        self.open_explorer_var = ctk.BooleanVar(value=self.config.get("open_explorer_on_create", True))
        open_exp_cb = ctk.CTkCheckBox(
            form_card,
            text="Open folder in File Explorer immediately after creation",
            variable=self.open_explorer_var,
            font=ctk.CTkFont(size=13)
        )
        open_exp_cb.pack(anchor="w", padx=24, pady=(0, 10))

        self.open_concept_var = ctk.BooleanVar(value=self.config.get("open_concept_on_create", False))
        open_concept_cb = ctk.CTkCheckBox(
            form_card,
            text="Open 'Concept.txt' note in default text editor",
            variable=self.open_concept_var,
            font=ctk.CTkFont(size=13)
        )
        open_concept_cb.pack(anchor="w", padx=24, pady=(0, 20))

        # Create Button
        self.create_btn = ctk.CTkButton(
            form_card,
            text="✨  Create Project",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=46,
            corner_radius=10,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.execute_create_project
        )
        self.create_btn.pack(fill="x", padx=24, pady=(0, 24))

        # Status Banner
        self.create_status_lbl = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.create_status_lbl.pack(anchor="w", pady=10)

        self.update_new_project_preview()
        return frame

    def update_new_project_preview(self):
        raw_name = self.new_proj_name_entry.get().strip() if hasattr(self, 'new_proj_name_entry') else ""
        sample_name = raw_name if raw_name else "[ProjectName]"
        sanitized = efm_core.sanitize_folder_name(sample_name)
        date_str = datetime.now().strftime('%Y%m%d')
        folder_name = f"{sanitized}_{date_str}"

        is_client = (self.new_proj_cat_var.get() == "Client Project")
        cat_folder = "Client Project" if is_client else "Personal Project"
        target_path = os.path.join(self.base_dir, cat_folder, "Ongoing Project", folder_name)

        self.new_proj_preview_lbl.configure(text=target_path)

    def execute_create_project(self):
        name = self.new_proj_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Project Name Required", "Please enter a valid project name before creating.")
            return

        is_client = (self.new_proj_cat_var.get() == "Client Project")
        success, message, created_path = efm_core.create_new_project(name, is_client, self.base_dir)

        if success:
            self.create_status_lbl.configure(text=f"✓ {message}", text_color=SUCCESS_COLOR)
            self.new_proj_name_entry.delete(0, tk.END)
            self.update_new_project_preview()
            self.refresh_projects_data()

            # Actions
            if self.open_explorer_var.get():
                efm_core.open_folder(created_path)

            if self.open_concept_var.get():
                concept_file = os.path.join(created_path, "Files", "Concept.txt")
                try:
                    os.startfile(concept_file)
                except Exception:
                    pass

            messagebox.showinfo("Project Created", f"Successfully initialized workspace for:\n{name}\n\nLocation:\n{created_path}")
        else:
            self.create_status_lbl.configure(text=f"✗ {message}", text_color="#ef4444")
            messagebox.showerror("Error Creating Project", message)

    # -------------------------------------------------------------------------
    # VIEW 4: Move / Archive Project
    # -------------------------------------------------------------------------
    def build_move_project_view(self):
        frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        # Header
        title_lbl = ctk.CTkLabel(frame, text="Move / Archive Project", font=ctk.CTkFont(size=26, weight="bold"))
        title_lbl.pack(anchor="w", pady=(10, 2))

        sub_lbl = ctk.CTkLabel(
            frame, 
            text="Move an ongoing project to Finished, Ignored, or Learning storage.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        )
        sub_lbl.pack(anchor="w", pady=(0, 20))

        # Main Card Form
        form_card = ctk.CTkFrame(frame, corner_radius=14, fg_color=("gray90", "#1e293b"), border_width=1, border_color=CARD_BORDER)
        form_card.pack(fill="x", pady=10)
        form_card.grid_columnconfigure(0, weight=1)

        # Step 1: Select Project
        s1_title = ctk.CTkLabel(form_card, text="1. Select Project to Move", font=ctk.CTkFont(size=14, weight="bold"))
        s1_title.pack(anchor="w", padx=24, pady=(20, 6))

        self.move_project_var = ctk.StringVar(value="")
        self.move_project_menu = ctk.CTkOptionMenu(
            form_card,
            variable=self.move_project_var,
            values=["No projects found"],
            height=38,
            font=ctk.CTkFont(size=13),
            command=lambda v: self.on_move_project_selected()
        )
        self.move_project_menu.pack(fill="x", padx=24, pady=(0, 16))

        self.move_proj_detected_badge = ctk.CTkLabel(
            form_card, 
            text="Select an ongoing project above", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_MUTED
        )
        self.move_proj_detected_badge.pack(anchor="w", padx=24, pady=(0, 16))

        # Step 2: Destination Status
        s2_title = ctk.CTkLabel(form_card, text="2. Move Status", font=ctk.CTkFont(size=14, weight="bold"))
        s2_title.pack(anchor="w", padx=24, pady=(6, 6))

        self.move_status_var = ctk.StringVar(value="finished")
        self.move_status_segmented = ctk.CTkSegmentedButton(
            form_card,
            values=["Finished", "Ignored", "Learning"],
            variable=self.move_status_var,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            command=lambda v: self.on_status_changed()
        )
        self.move_status_segmented.set("Finished")
        self.move_status_segmented.pack(fill="x", padx=24, pady=(0, 16))

        # Step 3: Client Subcategory Controls (Dynamic)
        self.client_sub_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        self.client_sub_frame.pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkLabel(self.client_sub_frame, text="3. Client Category", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 6))

        self.client_type_var = ctk.StringVar(value="project")
        self.client_type_segmented = ctk.CTkSegmentedButton(
            self.client_sub_frame,
            values=["Project Based", "Rebound Client"],
            variable=self.client_type_var,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=34,
            command=lambda v: self.on_client_type_changed()
        )
        self.client_type_segmented.set("Project Based")
        self.client_type_segmented.pack(fill="x", pady=(0, 12))

        # Container for Project Based options
        self.proj_based_frame = ctk.CTkFrame(self.client_sub_frame, fg_color="transparent")
        self.proj_based_frame.pack(fill="x")

        ctk.CTkLabel(self.proj_based_frame, text="Project Type:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.project_type_var = ctk.StringVar(value="Video Editing")
        self.project_type_menu = ctk.CTkOptionMenu(
            self.proj_based_frame,
            values=efm_core.PROJECT_TYPES,
            variable=self.project_type_var,
            height=34,
            command=lambda v: self.update_move_preview()
        )
        self.project_type_menu.pack(fill="x", pady=(0, 6))

        # Container for Rebound options
        self.rebound_frame = ctk.CTkFrame(self.client_sub_frame, fg_color="transparent")

        self.rebound_choice_var = ctk.StringVar(value="existing")
        rebound_mode_seg = ctk.CTkSegmentedButton(
            self.rebound_frame,
            values=["Existing Client", "New Rebound Client"],
            variable=self.rebound_choice_var,
            height=32,
            command=lambda v: self.on_rebound_mode_changed()
        )
        rebound_mode_seg.set("Existing Client")
        rebound_mode_seg.pack(fill="x", pady=(0, 8))

        self.rebound_existing_menu = ctk.CTkOptionMenu(
            self.rebound_frame,
            values=["Select Existing Client..."],
            height=34,
            command=lambda v: self.update_move_preview()
        )
        self.rebound_existing_menu.pack(fill="x", pady=(0, 6))

        self.rebound_new_entry = ctk.CTkEntry(
            self.rebound_frame,
            placeholder_text="Enter new Rebound Client folder name...",
            height=34
        )
        self.rebound_new_entry.bind("<KeyRelease>", lambda e: self.update_move_preview())

        # Step 4: Preview Destination Path
        preview_box = ctk.CTkFrame(form_card, corner_radius=10, fg_color=("gray80", "#131d2e"), border_width=1, border_color=CARD_BORDER)
        preview_box.pack(fill="x", padx=24, pady=(10, 20))

        preview_header = ctk.CTkLabel(preview_box, text="🚚 Move Destination Preview", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED)
        preview_header.pack(anchor="w", padx=16, pady=(12, 4))

        self.move_dest_preview_lbl = ctk.CTkLabel(
            preview_box,
            text="",
            font=ctk.CTkFont(size=13, family="Consolas"),
            justify="left",
            anchor="w",
            wraplength=700
        )
        self.move_dest_preview_lbl.pack(fill="x", padx=16, pady=(0, 12))

        # Execute Move Button
        self.move_btn = ctk.CTkButton(
            form_card,
            text="📦  Move Project Now",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=46,
            corner_radius=10,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.execute_move_project
        )
        self.move_btn.pack(fill="x", padx=24, pady=(0, 24))

        return frame

    def update_move_project_dropdown(self):
        self.refresh_projects_data()
        options = [f"[{p['category']}] {p['name']}" for p in self.ongoing_projects]

        if not options:
            self.move_project_menu.configure(values=["No ongoing projects"])
            self.move_project_var.set("No ongoing projects")
            self.move_dest_preview_lbl.configure(text="No projects available to move.")
            return

        self.move_project_menu.configure(values=options)

        # Preselect if coming from card click
        if self.selected_move_project:
            pre_str = f"[{self.selected_move_project['category']}] {self.selected_move_project['name']}"
            if pre_str in options:
                self.move_project_var.set(pre_str)
            else:
                self.move_project_var.set(options[0])
            self.selected_move_project = None
        else:
            if not self.move_project_var.get() or self.move_project_var.get() not in options:
                self.move_project_var.set(options[0])

        self.on_move_project_selected()

    def get_currently_selected_move_project(self):
        selected_text = self.move_project_var.get()
        for p in self.ongoing_projects:
            if f"[{p['category']}] {p['name']}" == selected_text:
                return p
        return None

    def on_move_project_selected(self):
        project = self.get_currently_selected_move_project()
        if not project:
            return

        is_client = (project["category"] == "Client")
        badge_color = CLIENT_COLOR if is_client else PERSONAL_COLOR
        self.move_proj_detected_badge.configure(
            text=f"Type: {project['category']} Project  |  Path: {project['path']}",
            text_color=badge_color
        )

        # Note: 'Learning Project' option removed from Client moving per New Features specification!
        if is_client:
            self.move_status_segmented.configure(values=["Finished", "Ignored"])
            if self.move_status_var.get() == "Learning":
                self.move_status_segmented.set("Finished")
        else:
            self.move_status_segmented.configure(values=["Finished", "Ignored", "Learning"])

        self.on_status_changed()

    def on_status_changed(self):
        project = self.get_currently_selected_move_project()
        if not project:
            return

        is_client = (project["category"] == "Client")
        status = self.move_status_var.get().lower()

        if is_client and status == "finished":
            self.client_sub_frame.pack(fill="x", padx=24, pady=(0, 16))
            self.on_client_type_changed()
        else:
            self.client_sub_frame.pack_forget()

        self.update_move_preview()

    def on_client_type_changed(self):
        client_type = "project" if self.client_type_var.get() == "Project Based" else "rebound"
        if client_type == "project":
            self.rebound_frame.pack_forget()
            self.proj_based_frame.pack(fill="x")
        else:
            self.proj_based_frame.pack_forget()
            self.rebound_frame.pack(fill="x")

            # Update existing rebound dropdown
            rebounds = efm_core.get_existing_rebound_clients(self.base_dir)
            if rebounds:
                self.rebound_existing_menu.configure(values=rebounds)
                self.rebound_existing_menu.set(rebounds[0])
            else:
                self.rebound_existing_menu.configure(values=["(No folders yet)"])
                self.rebound_existing_menu.set("(No folders yet)")
            self.on_rebound_mode_changed()

        self.update_move_preview()

    def on_rebound_mode_changed(self):
        choice = self.rebound_choice_var.get()
        if choice == "Existing Client":
            self.rebound_new_entry.pack_forget()
            self.rebound_existing_menu.pack(fill="x", pady=(0, 6))
        else:
            self.rebound_existing_menu.pack_forget()
            self.rebound_new_entry.pack(fill="x", pady=(0, 6))
        self.update_move_preview()

    def update_move_preview(self):
        project = self.get_currently_selected_move_project()
        if not project:
            self.move_dest_preview_lbl.configure(text="No project selected.")
            return

        is_client = (project["category"] == "Client")
        status = self.move_status_var.get().lower()

        client_type = None
        project_type = None
        rebound_folder = None

        if is_client and status == "finished":
            client_type = "project" if self.client_type_var.get() == "Project Based" else "rebound"
            if client_type == "project":
                project_type = self.project_type_var.get()
            else:
                if self.rebound_choice_var.get() == "Existing Client":
                    rebound_folder = self.rebound_existing_menu.get()
                    if rebound_folder == "(No folders yet)":
                        rebound_folder = None
                else:
                    rebound_folder = self.rebound_new_entry.get().strip()

        valid, dest_dir, error_msg = efm_core.calculate_move_destination(
            project["path"], is_client, status, client_type, project_type, rebound_folder, self.base_dir
        )

        if valid:
            full_dest = os.path.join(dest_dir, project["name"])
            self.move_dest_preview_lbl.configure(
                text=f"Origin:      {project['path']}\nDestination: {full_dest}",
                text_color=("gray10", "gray90")
            )
        else:
            self.move_dest_preview_lbl.configure(
                text=f"⚠️ {error_msg}",
                text_color="#f59e0b"
            )

    def execute_move_project(self):
        project = self.get_currently_selected_move_project()
        if not project:
            messagebox.showwarning("Select Project", "Please select a project to move.")
            return

        is_client = (project["category"] == "Client")
        status = self.move_status_var.get().lower()

        client_type = None
        project_type = None
        rebound_folder = None

        if is_client and status == "finished":
            client_type = "project" if self.client_type_var.get() == "Project Based" else "rebound"
            if client_type == "project":
                project_type = self.project_type_var.get()
            else:
                if self.rebound_choice_var.get() == "Existing Client":
                    rebound_folder = self.rebound_existing_menu.get()
                    if rebound_folder == "(No folders yet)":
                        messagebox.showwarning("Rebound Folder", "No existing rebound client found. Please create a new folder.")
                        return
                else:
                    rebound_folder = self.rebound_new_entry.get().strip()
                    if not rebound_folder:
                        messagebox.showwarning("Rebound Folder", "Please enter a name for the rebound client.")
                        return

        # Confirm before moving
        confirm = messagebox.askyesno(
            "Confirm Project Move",
            f"Are you sure you want to move:\n'{project['name']}'\n\nto status: {status.upper()}?"
        )
        if not confirm:
            return

        success, message, final_path = efm_core.move_project(
            project["path"], is_client, status, client_type, project_type, rebound_folder, self.base_dir
        )

        if success:
            messagebox.showinfo("Project Moved", message)
            efm_core.open_folder(os.path.dirname(final_path))
            self.update_move_project_dropdown()
            self.refresh_projects_list_ui()
            self.update_dashboard_stats()
        else:
            messagebox.showerror("Move Failed", message)

    # -------------------------------------------------------------------------
    # VIEW 5: Dedicated File Sorter Utility
    # -------------------------------------------------------------------------
    def build_file_sorter_view(self):
        frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(frame, text="File Sorter Utility", font=ctk.CTkFont(size=26, weight="bold"))
        title_lbl.pack(anchor="w", pady=(10, 2))

        sub_lbl = ctk.CTkLabel(
            frame, 
            text="Automatically categorizes media and documents into Image, Video, Audio, and Doc subfolders.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        )
        sub_lbl.pack(anchor="w", pady=(0, 20))

        # Main Card
        card = ctk.CTkFrame(frame, corner_radius=14, fg_color=("gray90", "#1e293b"), border_width=1, border_color=CARD_BORDER)
        card.pack(fill="x", pady=10)

        # Folder selection
        f_lbl = ctk.CTkLabel(card, text="Target Folder to Organize", font=ctk.CTkFont(size=14, weight="bold"))
        f_lbl.pack(anchor="w", padx=24, pady=(20, 6))

        sel_frame = ctk.CTkFrame(card, fg_color="transparent")
        sel_frame.pack(fill="x", padx=24, pady=(0, 16))
        sel_frame.grid_columnconfigure(0, weight=1)

        self.sorter_path_entry = ctk.CTkEntry(
            sel_frame,
            placeholder_text="Enter or browse any project folder (e.g., Raw, Stock, or root project folder)...",
            height=38
        )
        self.sorter_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        browse_btn = ctk.CTkButton(
            sel_frame,
            text="📂 Browse...",
            width=100,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray75", "#334155"),
            hover_color=("gray65", "#475569"),
            command=self.browse_sorter_folder
        )
        browse_btn.grid(row=0, column=1)

        # Or pick from ongoing project dropdown
        quick_lbl = ctk.CTkLabel(card, text="Or quick-select an ongoing project:", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        quick_lbl.pack(anchor="w", padx=24, pady=(0, 6))

        self.sorter_proj_var = ctk.StringVar(value="")
        self.sorter_proj_menu = ctk.CTkOptionMenu(
            card,
            variable=self.sorter_proj_var,
            values=["Select project..."],
            height=36,
            command=self.on_sorter_proj_selected
        )
        self.sorter_proj_menu.pack(fill="x", padx=24, pady=(0, 20))

        # File category types summary
        types_box = ctk.CTkFrame(card, corner_radius=8, fg_color=("gray85", "#131d2e"))
        types_box.pack(fill="x", padx=24, pady=(0, 20))

        ctk.CTkLabel(types_box, text="Supported Extensions by Category:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=14, pady=(10, 4))
        for cat, exts in efm_core.FILE_EXTENSIONS.items():
            ext_str = ", ".join(exts)
            ctk.CTkLabel(types_box, text=f"• {cat}: {ext_str}", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=1)
        ctk.CTkLabel(types_box, text="").pack(pady=4)

        # Action Button
        run_sort_btn = ctk.CTkButton(
            card,
            text="🧹  Sort Files Now",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44,
            corner_radius=10,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.execute_sorter
        )
        run_sort_btn.pack(fill="x", padx=24, pady=(0, 24))

        # Output Log Box
        self.sorter_output_box = ctk.CTkTextbox(frame, height=160, font=ctk.CTkFont(family="Consolas", size=12))
        self.sorter_output_box.pack(fill="x", pady=15)
        self.sorter_output_box.insert("0.0", "Sorter ready. Select a folder and click 'Sort Files Now'.\n")

        return frame

    def browse_sorter_folder(self):
        folder = filedialog.askdirectory(initialdir=self.base_dir, title="Select Folder to Sort")
        if folder:
            self.sorter_path_entry.delete(0, tk.END)
            self.sorter_path_entry.insert(0, folder)

    def on_sorter_proj_selected(self, val):
        for p in self.ongoing_projects:
            if f"[{p['category']}] {p['name']}" == val:
                self.sorter_path_entry.delete(0, tk.END)
                self.sorter_path_entry.insert(0, p["path"])
                break

    def execute_sorter(self):
        target = self.sorter_path_entry.get().strip()
        if not target or not os.path.exists(target):
            messagebox.showwarning("Invalid Path", "Please select an existing folder to sort.")
            return

        self.sorter_output_box.delete("0.0", tk.END)
        self.sorter_output_box.insert(tk.END, f"Scanning: {target}\n" + "-"*50 + "\n")

        # Check if project folder with Files/Raw and Files/Stock
        raw_dir = os.path.join(target, "Files", "Raw")
        stock_dir = os.path.join(target, "Files", "Stock")

        if os.path.exists(raw_dir) or os.path.exists(stock_dir):
            summary = efm_core.auto_sort_project(target)
            self.sorter_output_box.insert(tk.END, f"✓ Project scan complete!\nTotal files organized: {summary['total_moved']}\n")
            for detail in summary["details"]:
                self.sorter_output_box.insert(tk.END, f"  • {detail}\n")
        else:
            summary = efm_core.sort_files_into_subfolders(target)
            self.sorter_output_box.insert(tk.END, f"✓ Folder scan complete!\nTotal files organized: {summary['moved_count']}\n")
            for detail in summary["details"]:
                self.sorter_output_box.insert(tk.END, f"  • {detail}\n")

        if summary.get("total_moved", summary.get("moved_count", 0)) == 0:
            self.sorter_output_box.insert(tk.END, "No unsorted files found.\n")

    # -------------------------------------------------------------------------
    # VIEW 6: Settings
    # -------------------------------------------------------------------------
    def build_settings_view(self):
        frame = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(frame, text="Application Settings", font=ctk.CTkFont(size=26, weight="bold"))
        title_lbl.pack(anchor="w", pady=(10, 2))

        sub_lbl = ctk.CTkLabel(
            frame, 
            text="Configure your project workspace directory and interface preferences.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        )
        sub_lbl.pack(anchor="w", pady=(0, 20))

        # Card 1: Directory Setup
        dir_card = ctk.CTkFrame(frame, corner_radius=14, fg_color=("gray90", "#1e293b"), border_width=1, border_color=CARD_BORDER)
        dir_card.pack(fill="x", pady=10)

        ctk.CTkLabel(dir_card, text="Base Projects Storage Directory", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=24, pady=(20, 6))

        sel_frame = ctk.CTkFrame(dir_card, fg_color="transparent")
        sel_frame.pack(fill="x", padx=24, pady=(0, 10))
        sel_frame.grid_columnconfigure(0, weight=1)

        self.settings_dir_entry = ctk.CTkEntry(sel_frame, height=38, font=ctk.CTkFont(size=13))
        self.settings_dir_entry.insert(0, self.base_dir)
        self.settings_dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        browse_btn = ctk.CTkButton(
            sel_frame,
            text="📂 Browse...",
            width=100,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray75", "#334155"),
            hover_color=("gray65", "#475569"),
            command=self.browse_base_directory
        )
        browse_btn.grid(row=0, column=1)

        ensure_struct_btn = ctk.CTkButton(
            dir_card,
            text="Initialize Standard Subdirectories Now",
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=("gray75", "#334155"),
            hover_color=("gray65", "#475569"),
            command=self.initialize_storage_subdirs
        )
        ensure_struct_btn.pack(anchor="w", padx=24, pady=(0, 20))

        # Card 2: Preferences
        pref_card = ctk.CTkFrame(frame, corner_radius=14, fg_color=("gray90", "#1e293b"), border_width=1, border_color=CARD_BORDER)
        pref_card.pack(fill="x", pady=10)

        ctk.CTkLabel(pref_card, text="Appearance & Preferences", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=24, pady=(20, 10))

        theme_lbl = ctk.CTkLabel(pref_card, text="Theme Mode:", font=ctk.CTkFont(size=13))
        theme_lbl.pack(anchor="w", padx=24, pady=(0, 4))

        self.theme_segmented = ctk.CTkSegmentedButton(
            pref_card,
            values=["dark", "light", "system"],
            height=36,
            command=self.change_theme_mode
        )
        self.theme_segmented.set(self.config.get("appearance_mode", "dark"))
        self.theme_segmented.pack(fill="x", padx=24, pady=(0, 16))

        self.pref_auto_sort = ctk.BooleanVar(value=self.config.get("auto_sort_on_open", True))
        sort_cb = ctk.CTkCheckBox(
            pref_card,
            text="Automatically sort files in Raw & Stock when opening projects",
            variable=self.pref_auto_sort,
            font=ctk.CTkFont(size=13),
            command=self.save_settings
        )
        sort_cb.pack(anchor="w", padx=24, pady=(0, 20))

        # Save Button
        save_btn = ctk.CTkButton(
            frame,
            text="💾  Save Settings",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44,
            corner_radius=10,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            command=self.save_settings_from_ui
        )
        save_btn.pack(fill="x", pady=15)

        # About Card
        about_card = ctk.CTkFrame(frame, corner_radius=14, fg_color=("gray90", "#1e293b"), border_width=1, border_color=CARD_BORDER)
        about_card.pack(fill="x", pady=10)

        ctk.CTkLabel(about_card, text="About EFM 6.0", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=24, pady=(16, 4))
        ctk.CTkLabel(
            about_card,
            text="Edit Folder Manager (EFM) - Version 6.0\n"
                 "An open-source workspace automation and media organization tool.\n"
                 "Streamlines project scaffolding, automated media sorting, and client archiving.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", padx=24, pady=(0, 16))

        return frame

    def browse_base_directory(self):
        new_dir = filedialog.askdirectory(initialdir=self.base_dir, title="Select Projects Base Directory")
        if new_dir:
            self.settings_dir_entry.delete(0, tk.END)
            self.settings_dir_entry.insert(0, new_dir)
            self.save_settings_from_ui()

    def initialize_storage_subdirs(self):
        target = self.settings_dir_entry.get().strip()
        if not target:
            messagebox.showwarning("Directory Required", "Please enter a valid directory.")
            return
        efm_core.ensure_directory_structure(target)
        messagebox.showinfo("Success", f"Standard folder structure verified and initialized at:\n{target}")

    def change_theme_mode(self, mode):
        ctk.set_appearance_mode(mode)
        self.config["appearance_mode"] = mode
        efm_core.save_config(self.config)

    def save_settings(self):
        self.config["auto_sort_on_open"] = self.pref_auto_sort.get()
        efm_core.save_config(self.config)

    def save_settings_from_ui(self):
        new_dir = self.settings_dir_entry.get().strip()
        if not new_dir or not os.path.exists(new_dir):
            try:
                os.makedirs(new_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to access or create directory: {e}")
                return

        self.base_dir = new_dir
        self.config["base_dir"] = new_dir
        self.config["auto_sort_on_open"] = self.pref_auto_sort.get()
        self.config["appearance_mode"] = self.theme_segmented.get()

        efm_core.save_config(self.config)

        # Update sidebar
        dir_name = os.path.basename(self.base_dir) or self.base_dir
        self.sidebar_base_lbl.configure(text=f"📁 {dir_name}")

        self.refresh_projects_data()
        self.update_dashboard_stats()
        messagebox.showinfo("Settings Saved", "Your workspace settings have been saved successfully!")


def main():
    app = EFMApp()
    app.mainloop()


if __name__ == "__main__":
    main()
