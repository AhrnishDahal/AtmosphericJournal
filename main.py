import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Querybox
from tkinter import filedialog, Canvas, font as tkfont
import json
import os
import requests
from datetime import datetime
import random

class AtmosphericJournal:
    def __init__(self, root):
        self.root = root
        self.root.title("Atmospheric Journal - Meta Context Edition")
        self.root.geometry("1600x950")
        
        self.weather_api_key = "key-here" 
        self.current_city = "London"
        
        # Weather Cache
        self.live_temp = "--"
        self.live_condition = "Clear" 
        self.live_humidity = "--"
        
        
        # DYNAMIC ATMOSPHERE MAPPING
        # ------------------------------------------------------------------
        self.atmosphere_map = {
            "Clear": {"bg": "#ffffff", "fg": "#1c1e21", "accent": "#1877f2", "header": ["#1877f2", "#00c6ff"]},
            "Clouds": {"bg": "#f0f2f5", "fg": "#1c1e21", "accent": "#4b4f56", "header": ["#4b4f56", "#8d949e"]},
            "Rain": {"bg": "#1a1a2e", "fg": "#e4e6eb", "accent": "#00d2ff", "header": ["#003366", "#00d2ff"]},
            "Drizzle": {"bg": "#e7f3ff", "fg": "#1c1e21", "accent": "#1877f2", "header": ["#74b9ff", "#a29bfe"]},
            "Thunderstorm": {"bg": "#101010", "fg": "#ffffff", "accent": "#a29bfe", "header": ["#2d3436", "#6c5ce7"]},
            "Snow": {"bg": "#fcfcfc", "fg": "#2d3436", "accent": "#0984e3", "header": ["#74b9ff", "#ffffff"]},
            "Mist": {"bg": "#f5f6f7", "fg": "#1c1e21", "accent": "#636e72", "header": ["#b2bec3", "#dfe6e9"]},
            "Fog": {"bg": "#f5f6f7", "fg": "#1c1e21", "accent": "#636e72", "header": ["#b2bec3", "#dfe6e9"]}
        }

       
        # STATES
        # ------------------------------------------------------------------
        self.entries = []
        self.current_font_size = 15
        self.current_font_family = "Segoe UI"
        self.history_visible = True
        
        self.quotes = [
            "Every moment is a fresh beginning.",
            "Believe you can and you're halfway there.",
            "Your story matters. Write it down.",
            "The best time for new beginnings is now.",
            "Small progress is still progress.",
            "Create the life you imagine."
        ]
        self.current_quote = random.choice(self.quotes)
        self.quote_index = 0
        self.typing_forward = True
        self.quote_text_id = None

        self.load_entries()
        self.setup_ui()
        
        # ------------------------------------------------------------------
        # SAFETY INITIALIZATION SEQUENCE
        # ------------------------------------------------------------------
        # Force the window to calculate sizes before we try to draw context
        self.root.update_idletasks()
        self.root.update()
        
        # Now trigger the atmosphere safely
        self.apply_contextual_atmosphere()
        self.animate_quote()

    
    # CONTEXTUAL ENGINE METHODS
    # ------------------------------------------------------------------
    def get_live_weather(self, city):
        if self.weather_api_key == "YOUR_OPENWEATHER_API_KEY":
            return "22°C", "Clear", "45%"
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get("cod") == 200:
                t = f"{round(data['main']['temp'])}°C"
                c = data['weather'][0]['main'] 
                h = f"{data['main']['humidity']}%"
                return t, c, h
            return "N/A", "Clear", "--"
        except:
            return "Offline", "Clear", "--"

    def apply_contextual_atmosphere(self):
        """Orchestrates the global UI shift based on environment"""
        self.live_temp, self.live_condition, self.live_humidity = self.get_live_weather(self.current_city)
        
        style = self.atmosphere_map.get(self.live_condition, self.atmosphere_map["Clear"])
        
        # Update Editor Colors
        self.text_area.config(
            bg=style["bg"], 
            fg=style["fg"], 
            insertbackground=style["fg"],
            selectbackground=style["accent"]
        )
        
        # Update Weather Readout
        self.weather_label.config(
            text=f"{self.current_city}: {self.live_temp} | {self.live_condition}",
            foreground=style["accent"]
        )
        
        # Refresh all canvas drawings with current geometry
        self.draw_header_gradient(None)
        self.draw_title_card(None)
        self.draw_toolbar_card(None)
        self.draw_editor_bg(None)
        self.draw_history_bg(None)

    def change_city_dialog(self):
        new_city = Querybox.get_string(prompt="Enter City Name:", title="Update Atmosphere", initialvalue=self.current_city)
        if new_city:
            self.current_city = new_city.strip().title()
            self.apply_contextual_atmosphere()

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------
    def setup_ui(self):
        self.main_container = tb.Frame(self.root, bootstyle=LIGHT)
        self.main_container.pack(fill=BOTH, expand=YES)

        # 1. HEADER (Gradient Canvas)
        self.header = tb.Frame(self.main_container, height=140)
        self.header.pack(fill=X, side=TOP)
        self.header.pack_propagate(False)
        self.header_canvas = Canvas(self.header, height=140, highlightthickness=0)
        self.header_canvas.pack(fill=BOTH, expand=YES)
        self.header_canvas.bind("<Configure>", self.draw_header_gradient)

        # 2. MAIN LAYOUT
        self.content_frame = tb.Frame(self.main_container, bootstyle=LIGHT)
        self.content_frame.pack(fill=BOTH, expand=YES, padx=30, pady=30)

        self.editor_container = tb.Frame(self.content_frame, bootstyle=LIGHT)
        self.editor_container.pack(side=LEFT, fill=BOTH, expand=YES)
        self.history_frame = tb.Frame(self.content_frame, width=450, bootstyle=LIGHT)
        self.history_frame.pack(side=RIGHT, fill=BOTH, padx=(30, 0))
        self.history_frame.pack_propagate(False)

        # 3. EDITOR WIDGETS
        # Title Card
        title_card = tb.Frame(self.editor_container, bootstyle=LIGHT)
        title_card.pack(fill=X, pady=(0, 20))
        self.title_canvas = Canvas(title_card, height=80, bg="#f7f9fc", highlightthickness=0)
        self.title_canvas.pack(fill=BOTH, expand=YES)
        self.title_canvas.bind("<Configure>", self.draw_title_card)
        self.title_var = tb.StringVar(value="Untitled Entry")
        self.title_entry = tb.Entry(title_card, textvariable=self.title_var, font=("Segoe UI", 16, "bold"), bootstyle=PRIMARY)
        self.title_entry.place(relx=0.03, rely=0.25, relwidth=0.94, relheight=0.5)

        # Toolbar
        toolbar_card = tb.Frame(self.editor_container, bootstyle=LIGHT)
        toolbar_card.pack(fill=X, pady=(0, 20))
        self.toolbar_canvas = Canvas(toolbar_card, height=90, bg="#f7f9fc", highlightthickness=0)
        self.toolbar_canvas.pack(fill=BOTH, expand=YES)
        self.toolbar_canvas.bind("<Configure>", self.draw_toolbar_card)

        self.tool_frame = tb.Frame(toolbar_card, bootstyle=LIGHT)
        self.tool_frame.place(relx=0.03, rely=0.15, relwidth=0.94, relheight=0.7)
        
        tb.Button(self.tool_frame, text="Typography", bootstyle="outline-primary", command=self.show_font_menu).pack(side=LEFT, padx=5)
        tb.Button(self.tool_frame, text="B", bootstyle="outline-primary", command=self.toggle_bold, width=4).pack(side=LEFT, padx=5)
        
        weather_info_f = tb.Frame(self.tool_frame, bootstyle=LIGHT)
        weather_info_f.pack(side=RIGHT, padx=10)
        weather_inner = tb.Frame(weather_info_f, bootstyle=LIGHT)
        weather_inner.pack(side=TOP, anchor=E)
        self.weather_label = tb.Label(weather_inner, text="Syncing Context...", font=("Segoe UI", 10, "bold"))
        self.weather_label.pack(side=LEFT)
        tb.Button(weather_inner, text="📍", bootstyle="link", command=self.change_city_dialog).pack(side=LEFT, padx=(5,0))
        self.char_count_label = tb.Label(weather_info_f, text="0 words", font=("Segoe UI", 9), foreground="#65676b")
        self.char_count_label.pack(side=TOP, anchor=E,pady=(0,2))

        # Text Editor
        editor_card = tb.Frame(self.editor_container, bootstyle=LIGHT)
        editor_card.pack(fill=BOTH, expand=YES)
        self.editor_bg_canvas = Canvas(editor_card, bg="#f7f9fc", highlightthickness=0)
        self.editor_bg_canvas.pack(fill=BOTH, expand=YES)
        self.editor_bg_canvas.bind("<Configure>", self.draw_editor_bg)

        self.text_frame = tb.Frame(editor_card)
        self.text_frame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.75)
        self.text_scroll = tb.Scrollbar(self.text_frame, bootstyle="primary-round")
        self.text_scroll.pack(side=RIGHT, fill=Y)
        self.text_area = tb.Text(self.text_frame, font=(self.current_font_family, self.current_font_size), wrap=WORD, undo=True, padx=25, pady=25, borderwidth=0, highlightthickness=0, yscrollcommand=self.text_scroll.set)
        self.text_area.pack(side=LEFT, fill=BOTH, expand=YES)
        self.text_scroll.config(command=self.text_area.yview)
        self.text_area.bind('<KeyRelease>', self.update_char_count)

        # Footer
        action_bar = tb.Frame(self.editor_container, bootstyle=LIGHT)
        action_bar.pack(fill=X, pady=(20, 0))
        tb.Button(action_bar, text="New Entry", bootstyle=SECONDARY, command=self.new_entry, width=15).pack(side=LEFT, ipady=10)
        self.save_btn = tb.Button(action_bar, text="Save Atmosphere", bootstyle=PRIMARY, command=self.save_entry, width=25)
        self.save_btn.pack(side=RIGHT, ipady=10)

        # 4. LIBRARY
        self.hist_bg_canvas = Canvas(self.history_frame, bg="#f7f9fc", highlightthickness=0)
        self.hist_bg_canvas.pack(fill=BOTH, expand=YES)
        self.hist_bg_canvas.bind("<Configure>", self.draw_history_bg)
        self.hist_content = tb.Frame(self.history_frame, bootstyle=LIGHT)
        self.hist_content.place(relx=0.05, rely=0.02, relwidth=0.9, relheight=0.96)
        tb.Label(self.hist_content, text="Library", font=("Segoe UI", 22, "bold")).pack(anchor=W, pady=(10, 5))
        
        search_frame = tb.Frame(self.hist_content)
        search_frame.pack(fill=X, pady=(0, 20))
        self.search_var = tb.StringVar()
        self.search_var.trace('w', self.filter_entries)
        tb.Entry(search_frame, textvariable=self.search_var, bootstyle=PRIMARY).pack(fill=X, pady=(0, 10))
        self.sort_var = tb.StringVar(value="Date (Newest)")
        tb.Combobox(search_frame, textvariable=self.sort_var, values=["Date (Newest)", "Date (Oldest)", "Title (A-Z)"], state="readonly").pack(fill=X)

        entries_list_container = tb.Frame(self.hist_content)
        entries_list_container.pack(fill=BOTH, expand=YES)
        self.history_list_canvas = Canvas(entries_list_container, bg="#ffffff", highlightthickness=0)
        self.list_scroll = tb.Scrollbar(entries_list_container, orient=VERTICAL, command=self.history_list_canvas.yview)
        self.history_list_frame = tb.Frame(self.history_list_canvas, bootstyle=LIGHT)
        self.history_list_frame.bind("<Configure>", lambda e: self.history_list_canvas.configure(scrollregion=self.history_list_canvas.bbox("all")))
        self.history_list_canvas.create_window((0, 0), window=self.history_list_frame, anchor="nw")
        self.history_list_canvas.configure(yscrollcommand=self.list_scroll.set)
        self.history_list_canvas.pack(side=LEFT, fill=BOTH, expand=YES); self.list_scroll.pack(side=RIGHT, fill=Y)

        self.display_entries()

    
    # SAFE RENDERING METHODS (NoneType Protected)
    # ------------------------------------------------------------------
    def draw_header_gradient(self, event):
        w = event.width if event else self.header_canvas.winfo_width()
        h = event.height if event else self.header_canvas.winfo_height()
        if w < 20: w = 1600
        if h < 20: h = 140
        
        style = self.atmosphere_map.get(self.live_condition, self.atmosphere_map["Clear"])
        self.header_canvas.delete("header_ui")
        c1, c2 = style["header"][0], style["header"][1]
        for i in range(h):
            ratio = i / h
            r = int(int(c1[1:3], 16) + (int(c2[1:3], 16) - int(c1[1:3], 16)) * ratio)
            g = int(int(c1[3:5], 16) + (int(c2[3:5], 16) - int(c1[3:5], 16)) * ratio)
            b = int(int(c1[5:7], 16) + (int(c2[5:7], 16) - int(c1[5:7], 16)) * ratio)
            self.header_canvas.create_line(0, i, w, i, fill=f"#{r:02x}{g:02x}{b:02x}", tags="header_ui")
        
        self.header_canvas.create_text(50, h/2 - 10, text="Atmospheric Journal", font=("Segoe UI", 34, "bold"), fill="#ffffff", anchor=W, tags="header_ui")
        self.header_canvas.create_text(50, h/2 + 30, text=f"Environmental Snapshot: {self.live_condition} in {self.current_city}", font=("Segoe UI", 12), fill="#ffffff", anchor=W, tags="header_ui")
        
        qx, qy, qw, qh = w - 470, h/2 - 35, 420, 70
        self.create_rounded_rect(self.header_canvas, qx, qy, qx+qw, qy+qh, radius=15, fill="#ffffff", outline="", tags="header_ui")
        self.quote_text_id = self.header_canvas.create_text(qx + qw/2, qy + qh/2, text="", font=("Segoe UI", 11, "italic"), fill="#1c1e21", width=qw-40, tags="header_ui")

    def draw_title_card(self, event):
        w = event.width if event else self.title_canvas.winfo_width()
        h = event.height if event else self.title_canvas.winfo_height()
        if w < 20: w = 1000
        self.title_canvas.delete("all")
        self.create_rounded_rect(self.title_canvas, 5, 5, w-5, h-5, radius=15, fill="#ffffff", outline="#e0e4e8", width=1)

    def draw_toolbar_card(self, event):
        w = event.width if event else self.toolbar_canvas.winfo_width()
        h = event.height if event else self.toolbar_canvas.winfo_height()
        if w < 20: w = 1000
        self.toolbar_canvas.delete("all")
        self.create_rounded_rect(self.toolbar_canvas, 5, 5, w-5, h-5, radius=15, fill="#ffffff", outline="#e0e4e8", width=1)

    def draw_editor_bg(self, event):
        w = event.width if event else self.editor_bg_canvas.winfo_width()
        h = event.height if event else self.editor_bg_canvas.winfo_height()
        if w < 20: w = 1000
        if h < 20: h = 600
        style = self.atmosphere_map.get(self.live_condition, self.atmosphere_map["Clear"])
        self.editor_bg_canvas.delete("all")
        self.create_rounded_rect(self.editor_bg_canvas, 5, 5, w-5, h-5, radius=25, fill=style["bg"], outline="#e0e4e8", width=1)
        self.editor_bg_canvas.create_text(w/2, 40, text=datetime.now().strftime("%A, %B %d, %Y"), font=("Segoe UI", 12, "bold"), fill=style["accent"])

    def draw_history_bg(self, event):
        w = event.width if event else self.hist_bg_canvas.winfo_width()
        h = event.height if event else self.hist_bg_canvas.winfo_height()
        if w < 20: w = 450
        if h < 20: h = 800
        style = self.atmosphere_map.get(self.live_condition, self.atmosphere_map["Clear"])
        self.hist_bg_canvas.delete("all")
        self.create_rounded_rect(self.hist_bg_canvas, 5, 5, w-5, h-5, radius=25, fill="#ffffff", outline=style["accent"], width=2)

    def create_rounded_rect(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    
    # LOGIC & DATA
    # ------------------------------------------------------------------
    def animate_quote(self):
        if not self.quote_text_id: return
        if self.typing_forward:
            if self.quote_index < len(self.current_quote):
                disp = self.current_quote[:self.quote_index + 1]
                self.header_canvas.itemconfig(self.quote_text_id, text=f"\"{disp}\"")
                self.quote_index += 1; self.root.after(80, self.animate_quote)
            else: self.root.after(3000, self.start_erasing)
        else:
            if self.quote_index > 0:
                disp = self.current_quote[:self.quote_index - 1]
                self.header_canvas.itemconfig(self.quote_text_id, text=f"\"{disp}\"")
                self.quote_index -= 1; self.root.after(50, self.animate_quote)
            else: self.typing_forward = True; self.current_quote = random.choice(self.quotes); self.root.after(500, self.animate_quote)

    def start_erasing(self): self.typing_forward = False; self.animate_quote()

    def update_char_count(self, event=None):
        content = self.text_area.get("1.0", END).strip()
        words = len(content.split()) if content else 0
        self.char_count_label.config(text=f"{words} words | {len(content)} chars")

    def show_font_menu(self):
        menu = tb.Toplevel(self.root); menu.title("Typography"); menu.geometry("300x400")
        for f in ["Segoe UI", "Georgia", "Arial"]:
            tb.Button(menu, text=f, bootstyle="outline-primary", command=lambda fn=f: self.update_font(fn, menu)).pack(fill=X, padx=20, pady=5)

    def update_font(self, n, w): self.current_font_family = n; self.text_area.config(font=(n, self.current_font_size)); w.destroy()
    
    def toggle_bold(self):
        try:
            cur = self.text_area.tag_names(SEL_FIRST)
            if "bold" in cur: self.text_area.tag_remove("bold", SEL_FIRST, SEL_LAST)
            else: self.text_area.tag_add("bold", SEL_FIRST, SEL_LAST)
            self.text_area.tag_configure("bold", font=(self.current_font_family, self.current_font_size, "bold"))
        except: pass

    def new_entry(self): self.text_area.delete("1.0", END); self.title_var.set("Untitled Entry"); self.update_char_count()

    def save_entry(self):
        content = self.text_area.get("1.0", END).strip()
        if not content: return
        entry = {"title": self.title_var.get(), "date": datetime.now().isoformat(), "content": content, "city": self.current_city, "weather": self.live_condition, "temp": self.live_temp}
        self.entries.insert(0, entry); self.save_to_json(); self.display_entries(); self.new_entry()

    def display_entries(self, data=None):
        for w in self.history_list_frame.winfo_children(): w.destroy()
        source = data if data is not None else self.entries
        for e in source:
            card = tb.Frame(self.history_list_frame, bootstyle=SECONDARY, padding=1); card.pack(fill=X, padx=10)
            inner = tb.Frame(card, bootstyle=LIGHT, padding=15); inner.pack(fill=X)
            tb.Label(inner, text=e['title'], font=("Segoe UI", 12, "bold")).pack(anchor=W)
            badge = f"{e.get('date', '')[:10]} | {e.get('weather', 'Clear')}"
            tb.Label(inner, text=badge, font=("Segoe UI", 9), foreground="#65676b").pack(anchor=W)
            tb.Button(inner, text="Open", bootstyle="link", command=lambda obj=e: self.load_entry(obj)).pack(side=LEFT)

    def load_entry(self, e):
        self.title_var.set(e['title']); self.text_area.delete("1.0", END); self.text_area.insert("1.0", e['content'])
        self.live_condition = e.get('weather', 'Clear')
        self.apply_contextual_atmosphere()

    def filter_entries(self, *args):
        q = self.search_var.get().lower()
        res = [e for e in self.entries if q in e['title'].lower()]
        self.display_entries(res)

    def save_to_json(self):
        with open("context_journal_final.json", "w") as f: json.dump(self.entries, f, indent=4)

    def load_entries(self):
        if os.path.exists("context_journal_final.json"):
            with open("context_journal_final.json", "r") as f: self.entries = json.load(f)

if __name__ == "__main__":
    app_window = tb.Window(themename="cosmo")
    app = AtmosphericJournal(app_window)
    app_window.mainloop()
