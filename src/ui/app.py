import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from src.graph import Graph
from src.node import Node
import random
import time
import networkx as nx
# --- EKRAN KALİTESİNİ ARTIRAN KOD BLOĞU (ESKİSİNİ SİLİP BUNU YAPIŞTIRIN) ---
import ctypes
try:
    # Windows 10/11 için en yüksek netlik modu (Per Monitor DPI V2)
    ctypes.windll.shcore.SetProcessDpiAwareness(2) 
except Exception:
    try:
        # Windows 8.1 ve eski sürümler için yedek netlik modu
        ctypes.windll.user32.SetProcessDPIAware()
    except: 
        pass # Windows dışı sistemler için geç
# -------------------------------------------------------------------------

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class App(ctk.CTk):
    def on_drag_start(self, event):
      
        found_items = self.canvas.find_closest(event.x, event.y)
        
       
        if not found_items:
            return

 
        closest_node = None
        min_dist = self.node_radius + 5
        
        for nid, (nx, ny) in self.node_positions.items():
            dist = ((nx - event.x)**2 + (ny - event.y)**2)**0.5
            if dist < min_dist:
                closest_node = nid
                break
        
        if closest_node:
            self.drag_data["node_id"] = closest_node
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drag_motion(self, event):
        if self.drag_data["node_id"]:
            nid = self.drag_data["node_id"]
            self.node_positions[nid] = (event.x, event.y)
            self.draw_graph()

    def on_drag_release(self, event):
        self.drag_data["node_id"] = None
    def __init__(self):
        super().__init__()
        self.drag_data = {"x": 0, "y": 0, "item": None, "node_id": None}
        self.selected_edge_key = None
        self.selected_node_id = None
        self.last_click_pos = None  
      
        self.title("Social Graph Analysis")
        self.geometry("1200x800")
        
        self.graph = Graph()
        self.node_positions = {}
        self.node_radius = 20
        
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)    

        self.setup_ui()
        self.create_context_menu()  
        
        self.status_label.configure(text="System Ready. Waiting for data...")
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_release)
        self.canvas.bind("<Button-3>", self.on_right_click) 
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Configure>", lambda event: self.draw_graph())
        
        # 2. Açılışta ızgarayı hemen göster
        # Küçük bir gecikme (100ms) ekliyoruz ki pencere tam yüklensin, sonra çizsin.
        self.after(100, self.draw_graph)


    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(20, weight=1)

        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="Social Graph Analysis", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.create_sidebar_label("DATA MANAGEMENT", row=1)
        self.create_sidebar_btn("Add Node (+)", self.add_node_dialog, row=2)
        self.create_sidebar_btn("Update/Edit Node", self.update_node_dialog, row=3)
        self.create_sidebar_btn("Remove Node (-)", self.remove_node_dialog, row=4)
        self.create_sidebar_btn("Create Link (Edge)", self.add_edge_dialog, row=5)
        self.create_sidebar_btn("Remove Link", self.remove_edge_dialog, row=6)
        
        self.create_sidebar_label("FILE IO", row=7)
        self.create_sidebar_btn("Load CSV Data", self.load_csv, row=8, color="green")
        self.create_sidebar_btn("Save to CSV", self.save_csv, row=9, color="green")
        self.create_sidebar_btn("Export HD Image", self.save_hd_image, row=10, color="green")

        self.create_sidebar_label("ALGORITHMS", row=11)
        self.create_sidebar_btn("Run BFS", self.run_bfs_ui, row=12)
        self.create_sidebar_btn("Run DFS", self.run_dfs_ui, row=13)
        self.create_sidebar_btn("Dijkstra Search", self.run_dijkstra_ui, row=14)
        self.create_sidebar_btn("A* Search", self.run_astar_ui, row=15)
        
        self.create_sidebar_label("ANALYSIS", row=16)
        self.create_sidebar_btn("Top 5 Influencers", self.show_top_nodes, row=17, color="orange")
        self.create_sidebar_btn("Welsh-Powell Color", self.run_coloring_ui, row=18, color="orange")
        self.create_sidebar_btn("Reset View", self.reset_view, row=19, color="red")
        self.create_sidebar_btn("Clear All Data", self.clear_all_nodes, row=20, color="red")
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.canvas_frame = ctk.CTkFrame(self.right_frame, fg_color="#ecf0f1") 
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#ecf0f1", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.status_frame = ctk.CTkFrame(self.right_frame, height=40, corner_radius=10)
        self.status_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="System Ready", font=("Consolas", 12))
        self.status_label.pack(side="left", padx=20)
    
    def show_results_table(self, title, columns, data):
      
        top = ctk.CTkToplevel(self)
        top.title(title)
        top.geometry("600x400")
        
        
        top.transient(self) 
        top.grab_set()

       
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#2c3e50", 
                        foreground="white", 
                        fieldbackground="#2c3e50", 
                        rowheight=25)
        style.configure("Treeview.Heading", 
                        background="#34495e", 
                        foreground="white", 
                        font=('Arial', 10, 'bold'))

 
        tree = ttk.Treeview(top, columns=columns, show="headings", selectmode="browse")
        
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)

      
        for item in data:
            tree.insert("", "end", values=item)

        
        scrollbar = ctk.CTkScrollbar(top, orientation="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)




    def create_sidebar_label(self, text, row):
        lbl = ctk.CTkLabel(self.sidebar, text=text, anchor="w", text_color="#bdc3c7", font=("Arial", 10, "bold"))
        lbl.grid(row=row, column=0, padx=20, pady=(10, 0), sticky="ew")

    def create_sidebar_btn(self, text, command, row, color="standard"):
        fg_color = None
        hover_color = None
        if color == "green":
            fg_color = "#27ae60"
            hover_color = "#2ecc71"
        elif color == "red":
            fg_color = "#c0392b"
            hover_color = "#e74c3c"
        elif color == "orange":
            fg_color = "#d35400"
            hover_color = "#e67e22"

        btn = ctk.CTkButton(self.sidebar, text=text, command=command, fg_color=fg_color, hover_color=hover_color)
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")

    def draw_graph(self, highlight_nodes=None, color_map=None, path_edges=None, custom_palette=None):
        self.canvas.delete("all")
        
        self.draw_grid()
        # Etiketleri (Labels) en üstte tutmak için bir liste
        labels_to_draw = []

        # --- KENAR ÇİZİMİ ---
        for key, edge in self.graph.edges.items():
            if edge.a in self.node_positions and edge.b in self.node_positions:
                x1, y1 = self.node_positions[edge.a]
                x2, y2 = self.node_positions[edge.b]
                
                # Varsayılan stil (İnce ve Gri)
                edge_color = "#bdc3c7"  # Açık gri (Daha az dikkat çeksin)
                width = 1.0  # Varsayılan çok ince
                
                # Ağırlığa göre kalınlık ayarı (Ters orantı: Küçük ağırlık = Yakın Mesafe = Kalın Çizgi)
                try:
                    w = edge.weight
                    if w < 2.0: width = 3.0      # Çok yakın (Kalın)
                    elif w < 5.0: width = 2.0    # Orta
                    elif w < 10.0: width = 1.5   # Uzak
                    else: width = 1.0            # Çok uzak (İnce)
                    
                    # Renk koyuluğu (Yakınlar daha koyu)
                    # 0.0 -> Koyu Gri, 20.0 -> Açık Gri
                    gray_level = int(min(200, max(50, w * 10)))
                    edge_color = f"#{gray_level:02x}{gray_level:02x}{gray_level:02x}"
                except: pass 

                # Eğer bir yol (Path) çiziliyorsa o çizgiyi belirginleştir
                if path_edges and tuple(sorted((edge.a, edge.b))) in path_edges:
                    edge_color = "#e74c3c" # Kırmızı
                    width = 4.0 # Yol daha kalın olsun
                
                # Çizgiyi Çiz (capstyle=tk.ROUND köşeleri yumuşatır)
                self.canvas.create_line(x1, y1, x2, y2, 
                                      fill=edge_color, 
                                      width=width, 
                                      capstyle=tk.ROUND, smooth=True)

                # Ağırlık Yazısını Hazırla (En son çizeceğiz ki çizginin üstünde kalsın)
                mx, my = (x1+x2)/2, (y1+y2)/2
                labels_to_draw.append((mx, my, f"{edge.weight:.2f}"))

        # --- AĞIRLIK YAZILARI (Çizgilerin Üstüne) ---
        for mx, my, text in labels_to_draw:
            # Arkaya Beyaz Kutu (Okunabilirlik için)
            # Yazı boyutuna göre dinamik kutu: x-12, y-8
            self.canvas.create_rectangle(mx-14, my-8, mx+14, my+8, fill="white", outline="#bdc3c7", width=1)
            # Yazı (Siyah ve Net)
            self.canvas.create_text(mx, my, text=text, font=("Arial", 9, "bold"), fill="black")

        # --- DÜĞÜM ÇİZİMİ ---
        for node_id, pos in self.node_positions.items():
            x, y = pos
            r = self.node_radius
            
            fill_color = "#3498db" 
            outline_color = "black" # DEĞİŞİKLİK 1: Kenar Rengi Siyah (Eskiden white idi)
            
            # Renklendirme veya Vurgulama Kontrolü
            if color_map and node_id in color_map:
                if custom_palette:
                    palette = custom_palette
                else:
                    palette = ["#e57373", "#81c784", "#64b5f6", "#fff176", "#ffb74d", "#ba68c8", "#90a4ae", "#4db6ac"]
                fill_color = palette[color_map[node_id] % len(palette)]
            elif highlight_nodes and node_id in highlight_nodes:
                fill_color = "#f1c40f" 

            # Düğüm Gölgesi (Hafif derinlik hissi için arkada gri bir yuvarlak)
            self.canvas.create_oval(x-r+2, y-r+2, x+r+2, y+r+2, fill="#95a5a6", outline="")
            
            # Düğümün Kendisi (Siyah kenarlı ve kalın)
            # DEĞİŞİKLİK 2: width=3 yapıldı (Hafif kalınlaştırıldı)
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline=outline_color, width=3, tags=f"node_{node_id}")
            
            # Düğüm ID (İçinde - Beyaz renk siyah konturda iyi durur)
            self.canvas.create_text(x, y, text=str(node_id), font=("Arial", 10, "bold"), fill="white", tags=f"node_{node_id}")
            
            # Düğüm İsmi (Altında)
            if node_id in self.graph.nodes:
                node_name = self.graph.nodes[node_id].name
                display_name = node_name[:12] + ".." if len(node_name) > 12 else node_name
                self.canvas.create_text(x, y+r+15, text=display_name, font=("Arial", 9, "bold"), fill="#2c3e50")
        
        # Etiketleri en üste taşı
        self.canvas.tag_raise("label_bg")

    
    def add_node_dialog(self, pos=None):
        win = tk.Toplevel(self)
        win.title("Add Node")
        fields = ["ID", "Name", "Activity (0-1)", "Interaction", "Connection Count"]
        entries = []
        for i, f in enumerate(fields):
            tk.Label(win, text=f).grid(row=i, column=0, padx=10, pady=5)
            e = tk.Entry(win)
            e.grid(row=i, column=1, padx=10, pady=5)
            entries.append(e)

        def submit():
            try:
                vals = [e.get() for e in entries]
                node = Node(int(vals[0]), vals[1], float(vals[2]), float(vals[3]), int(vals[4]))
                self.graph.add_node(node)
                
                # Eğer pos parametresi geldiyse oraya, gelmediyse rastgele bir yere koy
                if pos:
                    self.node_positions[node.id] = pos
                else:
                    self.node_positions[node.id] = (random.randint(50, 800), random.randint(50, 600))
                
                self.draw_graph()
                self.status_label.configure(text=f"Node Added: {node.name}")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(win, text="SAVE", command=submit).grid(row=len(fields), columnspan=2, pady=10)


    def load_csv(self):
        from tkinter import filedialog
        from src.csv_loader import CSVLoader
        f = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if f:
            try:
                self.graph = Graph()
                self.node_positions = {}
                nodes, positions = CSVLoader.load_nodes(f)
                for n in nodes:
                    self.graph.add_node(n)
                    if positions.get(n.id):
                        self.node_positions[n.id] = positions[n.id]
                    else:
                        self.node_positions[n.id] = (random.randint(100, 900), random.randint(50, 600))
                for n in nodes:
                    for nid in n.neighbors:
                        if nid in self.graph.nodes:
                            try: self.graph.add_edge(n.id, nid)
                            except: pass
                self.draw_graph()
                self.status_label.configure(text=f"CSV Loaded: {len(nodes)} nodes.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def save_csv(self):
        from tkinter import filedialog
        import csv
        f = filedialog.asksaveasfilename(defaultextension=".csv")
        if f:
            try:
                with open(f, 'w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow(["DugumId", "Name", "Ozellik_I", "Ozellik_II", "Ozellik_III", "Komsular", "Pos_X", "Pos_Y"])
                    for n in self.graph.nodes.values():
                        komsular = ",".join(map(str, n.neighbors))
                        x, y = self.node_positions.get(n.id, (0, 0))
                        writer.writerow([n.id, n.name, n.aktiflik, n.etkilesim, n.baglanti_sayisi, f"{komsular}", x, y])
                self.status_label.configure(text="Data Saved Successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def draw_grid(self):
        """Arka plana sade teknik çizim ızgarası ekler."""
        # Canvas boyutlarını al
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Pencere henüz tam yüklenmediyse varsayılan genişliği kullan
        if w < 50: w = 2000
        if h < 50: h = 2000
        
        step = 50 # Karelerin boyutu
        
        # Dikey Çizgiler (X Ekseni)
        for i in range(0, w, step):
            # 100'ün katları biraz daha koyu olsun (Ana çizgiler)
            if i % 100 == 0:
                color = "#bdc3c7" # Koyu Gri
            else:
                color = "#e5e8e8" # Çok Açık Gri
                
            self.canvas.create_line(i, 0, i, h, fill=color, width=1)

        # Yatay Çizgiler (Y Ekseni)
        for i in range(0, h, step):
            if i % 100 == 0:
                color = "#bdc3c7"
            else:
                color = "#e5e8e8"
                
            self.canvas.create_line(0, i, w, i, fill=color, width=1)

    def show_results_table(self, title, columns, data):
        """Sonuçları yeni bir pencerede tablo olarak gösterir."""
        top = ctk.CTkToplevel(self)
        top.title(title)
        top.geometry("600x400")
        top.transient(self) 
        
     
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50", rowheight=25)
        style.configure("Treeview.Heading", background="#34495e", foreground="white", font=('Arial', 10, 'bold'))
        
    
        tree = ttk.Treeview(top, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
            
        for item in data:
            tree.insert("", "end", values=item)
            
  
        scrollbar = ctk.CTkScrollbar(top, orientation="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)



    def run_bfs_ui(self):
        start = simpledialog.askinteger("BFS", "Start Node ID:", parent=self)
        if start:
            try:
                t0 = time.perf_counter()
                res = self.graph.run_bfs(start) 
                t1 = time.perf_counter()
                
          
                self.draw_graph(highlight_nodes=res)
                self.status_label.configure(text=f"BFS Done in {(t1-t0)*1000:.2f}ms. Visited: {len(res)}")
                
           
                table_data = []
                for node_id in res:
               
                    name = self.graph.nodes[node_id].name if node_id in self.graph.nodes else "Unknown"
                    table_data.append((node_id, name, "Ziyaret Edildi"))
                
          
                table_data.sort(key=lambda x: x[0])
                
           
                self.show_results_table(
                    title=f"BFS Sonuçları (Başlangıç: {start})",
                    columns=["Node ID", "İsim", "Durum"],
                    data=table_data
                )
            except Exception as e: messagebox.showerror("Error", str(e))

    def run_dfs_ui(self):
        start = simpledialog.askinteger("DFS", "Start Node ID:", parent=self)
        if start:
            try:
                t0 = time.perf_counter()
                res = self.graph.run_dfs(start)
                t1 = time.perf_counter()
                
                self.draw_graph(highlight_nodes=res)
                self.status_label.configure(text=f"DFS Done in {(t1-t0)*1000:.2f}ms. Visited: {len(res)}")
                
 
                table_data = []
                for node_id in res:
                    name = self.graph.nodes[node_id].name if node_id in self.graph.nodes else "Unknown"
                    table_data.append((node_id, name, "Ziyaret Edildi"))
                
                table_data.sort(key=lambda x: x[0])
                
                self.show_results_table(
                    title=f"DFS Sonuçları (Başlangıç: {start})",
                    columns=["Node ID", "İsim", "Durum"],
                    data=table_data
                )
            except Exception as e: messagebox.showerror("Error", str(e))

    def run_dijkstra_ui(self):
        s = simpledialog.askinteger("Dijkstra", "Start ID:", parent=self)
        if s is None: 
            return
        e = simpledialog.askinteger("Dijkstra", "End ID:", parent=self)
        if s and e:
            try:
                t0 = time.perf_counter()
                dist, path = self.graph.run_dijkstra(s, e)
                t1 = time.perf_counter()
                
 
                edges = [(tuple(sorted((path[i], path[i+1])))) for i in range(len(path)-1)] if len(path) > 1 else []
                self.draw_graph(highlight_nodes=set(path), path_edges=edges)
                self.status_label.configure(text=f"Dijkstra Cost: {dist:.2f} | Time: {(t1-t0)*1000:.2f}ms")

      
                table_data = []
                if path:
                    for i, node_id in enumerate(path):
                        name = self.graph.nodes[node_id].name
                        table_data.append((i+1, node_id, name))
                else:
                    table_data.append(("-", "-", "Yol Bulunamadı"))

                self.show_results_table(
                    title=f"En Kısa Yol (Dijkstra) - Maliyet: {dist:.2f}",
                    columns=["Adım", "Node ID", "İsim"],
                    data=table_data
                )
            except Exception as err: messagebox.showerror("Error", str(err))

    def run_astar_ui(self):
        s = simpledialog.askinteger("A*", "Start ID:", parent=self)
        
        if s is None: 
            return

        e = simpledialog.askinteger("A*", "End ID:", parent=self)
        if s and e:
            try:
                t0 = time.perf_counter()
                dist, path = self.graph.run_astar(s, e)
                t1 = time.perf_counter()
                
                edges = [(tuple(sorted((path[i], path[i+1])))) for i in range(len(path)-1)] if len(path) > 1 else []
                self.draw_graph(highlight_nodes=set(path), path_edges=edges)
                self.status_label.configure(text=f"A* Cost: {dist:.2f} | Time: {(t1-t0)*1000:.2f}ms")


                table_data = []
                if path:
                    for i, node_id in enumerate(path):
                        name = self.graph.nodes[node_id].name
                        table_data.append((i+1, node_id, name))
                else:
                    table_data.append(("-", "-", "Yol Bulunamadı"))

                self.show_results_table(
                    title=f"En Kısa Yol (A*) - Maliyet: {dist:.2f}",
                    columns=["Adım", "Node ID", "İsim"],
                    data=table_data
                )
            except Exception as err: messagebox.showerror("Error", str(err))

    def run_coloring_ui(self):
        try:
            t0 = time.perf_counter()
            colors = self.graph.color_graph()
            t1 = time.perf_counter()
            
            # Geniş bir renk havuzu tanımla
            palette = [
                "#e57373", "#81c784", "#64b5f6", "#fff176", "#ffb74d", 
                "#ba68c8", "#90a4ae", "#4db6ac", "#f06292", "#4dd0e1",
                "#7986cb", "#a1887f", "#ff8a65", "#dce775", "#afb42b"
            ]
            
            random.shuffle(palette)
            
            self.draw_graph(color_map=colors, custom_palette=palette)
            
            self.status_label.configure(text=f"Coloring Done in {(t1-t0)*1000:.2f}ms")

            table_data = []
            for node_id, color_code in colors.items():
                name = self.graph.nodes[node_id].name if node_id in self.graph.nodes else "Unknown"
                
                assigned_color = palette[color_code % len(palette)]
                
                table_data.append((node_id, name, f"Grup {color_code} ({assigned_color})"))
            
            table_data.sort(key=lambda x: x[0])
            
            self.show_results_table(
                title="Welsh-Powell Renklendirme Tablosu",
                columns=["Node ID", "İsim", "Atanan Renk Grubu"],
                data=table_data
            )
        except Exception as e: 
            messagebox.showerror("Error", str(e), parent=self)
    def show_top_nodes(self):
        try:
   
            nodes = sorted(self.graph.nodes.values(), key=lambda x: len(x.neighbors), reverse=True)[:5]
            
            table_data = []
            for i, n in enumerate(nodes, 1):
                table_data.append((i, n.id, n.name, len(n.neighbors)))
            
            self.show_results_table(
                title="Top 5 En Etkili Kullanıcı",
                columns=["Sıra", "ID", "İsim", "Bağlantı Sayısı"],
                data=table_data
            )
        except: pass
    
  
    def create_context_menu(self):
        """Sağ tık menülerini oluşturur."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Düğüm Ekle", command=self.add_node_context)
        self.context_menu.add_command(label="Bağlantı (Edge) Oluştur", command=self.add_edge_dialog)
        
        self.edge_menu = tk.Menu(self, tearoff=0)
        self.edge_menu.add_command(label="Bu Bağlantıyı Sil", command=self.delete_edge_context)

        self.node_menu = tk.Menu(self, tearoff=0)
        self.node_menu.add_command(label="Bu Düğümü Sil", command=self.delete_node_context)
        self.node_menu.add_command(label="Düzenle", command=lambda: self.update_node_dialog(passed_nid=self.selected_node_id))

    def on_right_click(self, event):
        """Sağ tıklama olayını yönetir: Node, Edge veya Boşluk tespiti."""
        click_x, click_y = event.x, event.y
        
        # 1. Önce Düğüm (Node) kontrolü (Öncelik düğümlerde)
        for nid, (nx, ny) in self.node_positions.items():
            dist = ((nx - click_x)**2 + (ny - click_y)**2)**0.5
            if dist < self.node_radius:
                # Tıklanan düğümü kaydet ve menüyü aç
                self.selected_node_id = nid
                try:
                    self.node_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.node_menu.grab_release()
                return

        # 2. Sonra Kenar (Edge) kontrolü
        closest_edge = None
        min_dist = 10.0 # Tıklama hassasiyeti (piksel)

        for key, edge in self.graph.edges.items():
            if edge.a in self.node_positions and edge.b in self.node_positions:
                x1, y1 = self.node_positions[edge.a]
                x2, y2 = self.node_positions[edge.b]
                
                # Noktanın çizgiye olan en kısa uzaklığını hesapla
                d = self.point_to_line_dist(click_x, click_y, x1, y1, x2, y2)
                
                if d < min_dist:
                    min_dist = d
                    closest_edge = key
        
        # Eğer bir kenar bulunduysa menüyü aç
        if closest_edge:
            self.selected_edge_key = closest_edge
            try:
                self.edge_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.edge_menu.grab_release()
            return

        # 3. Hiçbiri değilse Boş Alan menüsünü aç
        self.last_click_pos = (click_x, click_y)
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # --- Yardımcı Matematik Fonksiyonu ---
    def point_to_line_dist(self, px, py, x1, y1, x2, y2):
        """Bir noktanın (px,py) bir doğru parçasına (x1,y1 - x2,y2) en kısa uzaklığı."""
        # Vektör hesaplamaları
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1

        dot = A * C + B * D
        len_sq = C * C + D * D
        param = -1
        
        if len_sq != 0:
            param = dot / len_sq

        if param < 0:
            xx, yy = x1, y1
        elif param > 1:
            xx, yy = x2, y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D

        dx = px - xx
        dy = py - yy
        return (dx * dx + dy * dy) ** 0.5

    def add_node_context(self):
        """Sağ tıklanan pozisyonu kullanarak düğüm ekleme penceresini açar."""
        if self.last_click_pos:
            self.add_node_dialog(pos=self.last_click_pos)
    def reset_view(self):
        self.draw_graph()
        self.status_label.configure(text="View Reset.")

    def add_edge_dialog(self): 
         a = simpledialog.askinteger("Link", "Source ID:", parent=self)
         if a is None: 
            return
         b = simpledialog.askinteger("Link", "Target ID:", parent=self)
         if a and b:
             try:
                 self.graph.add_edge(a, b)
                 self.draw_graph()
                 self.status_label.configure(text=f"Linked: {a}-{b}")
             except Exception as e: messagebox.showerror("Error", str(e))
    
    def remove_edge_dialog(self): 
         a = simpledialog.askinteger("Unlink", "Source ID:", parent=self)
         if a is None: 
            return
         b = simpledialog.askinteger("Unlink", "Target ID:", parent=self)
         if a and b:
             try:
                 self.graph.remove_edge(a, b)
                 self.draw_graph()
                 self.status_label.configure(text=f"Unlinked: {a}-{b}")
             except Exception as e: messagebox.showerror("Error", str(e))

    def save_hd_image(self):
        """Mevcut grafiği Matplotlib kullanarak yüksek kalitede kaydeder."""
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
            
            # 1. Yeni bir figür oluştur (Yüksek çözünürlük: dpi=300)
            plt.figure(figsize=(12, 8), dpi=300)
            
            # 2. NetworkX grafiği oluştur
            G = nx.Graph()
            for nid, node in self.graph.nodes.items():
                G.add_node(nid)
            for key, edge in self.graph.edges.items():
                G.add_edge(edge.a, edge.b, weight=edge.weight)
            
            # 3. Pozisyonları Tkinter'dan alıp Matplotlib formatına çevir
            # Tkinter'da (0,0) sol üsttür, Matplotlib'de sol alttır. Y eksenini ters çeviriyoruz.
            height = self.canvas.winfo_height()
            pos = {nid: (x, height - y) for nid, (x, y) in self.node_positions.items()}
            
            # 4. Çizim İşlemi (Profesyonel Görünüm)
            # Düğümler
            nx.draw_networkx_nodes(G, pos, node_size=500, node_color="#3498db", edgecolors="black")
            # Etiketler (ID)
            nx.draw_networkx_labels(G, pos, font_color="white", font_size=10, font_weight="bold")
            # Kenarlar
            nx.draw_networkx_edges(G, pos, edge_color="#95a5a6", width=2, alpha=0.7)
            # Kenar Ağırlıkları
            edge_labels = {(e[0], e[1]): f"{e[2]['weight']:.2f}" for e in G.edges(data=True)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
            
            plt.axis("off") # Eksenleri gizle
            
            # 5. Dosyayı Kaydet
            filename = "Proje_Grafigi_HD.png"
            plt.savefig(filename, bbox_inches="tight")
            plt.close() # Hafızayı temizle
            
            messagebox.showinfo("Başarılı", f"Grafik yüksek kalitede kaydedildi:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Görüntü kaydedilemedi: {str(e)}")

    def remove_node_dialog(self):
         nid = simpledialog.askinteger("Remove", "Node ID:", parent=self)
         if nid:
             try:
                 self.graph.remove_node(nid)
                 if nid in self.node_positions: del self.node_positions[nid]
                 self.draw_graph()
                 self.status_label.configure(text=f"Node Removed: {nid}")
             except Exception as e: messagebox.showerror("Error", str(e))
    def clear_all_nodes(self):
        if messagebox.askyesno("Dikkat", "Tüm düğümler ve bağlantılar kalıcı olarak silinecek.\nDevam etmek istiyor musunuz?", parent=self):
            self.graph = Graph()
            self.node_positions = {}
            
            self.draw_graph()
            
            self.status_label.configure(text="System cleared. Ready for new data.")
    def delete_edge_context(self):
        if self.selected_edge_key:
            u, v = self.selected_edge_key
            # Onay iste (İsteğe bağlı, kaldırmak istersen if bloğunu silip direkt silme yapabilirsin)
            if messagebox.askyesno("Bağlantıyı Sil", f"{u} ve {v} arasındaki bağlantı silinsin mi?", parent=self):
                try:
                    self.graph.remove_edge(u, v)
                    self.draw_graph()
                    self.status_label.configure(text=f"Bağlantı silindi: {u}-{v}")
                except Exception as e:
                    messagebox.showerror("Hata", str(e), parent=self)
            
            self.selected_edge_key = None
    def update_node_dialog(self, passed_nid=None):
            if passed_nid is not None:
                nid = passed_nid
            else:
                nid = simpledialog.askinteger("Update", "Node ID:", parent=self)
            
            if nid is None: 
                return 
                
            if nid not in self.graph.nodes:
                messagebox.showerror("Error", f"Node {nid} bulunamadı!", parent=self)
                return

            node = self.graph.nodes[nid]
            
            win = tk.Toplevel(self)
            win.title(f"Update Node {nid}")
            
            fields = ["Name", "Activity (0-1)", "Interaction", "Connection Count"]
            current_vals = [node.name, str(node.aktiflik), str(node.etkilesim), str(node.baglanti_sayisi)]
            entries = []

            for i, field in enumerate(fields):
                tk.Label(win, text=field).grid(row=i, column=0, padx=10, pady=5)
                e = tk.Entry(win)
                e.insert(0, current_vals[i])
                e.grid(row=i, column=1, padx=10, pady=5)
                entries.append(e)

            def submit():
                try:
                    vals = [e.get() for e in entries]
                    
                    self.graph.update_node(nid, vals[0], float(vals[1]), float(vals[2]), int(vals[3]))
                    
                    self.draw_graph()
                    self.status_label.configure(text=f"Node {nid} updated successfully.")
                    win.destroy()
                except ValueError:
                    messagebox.showerror("Hata", "Lütfen sayısal alanlara geçerli sayılar giriniz.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            tk.Button(win, text="UPDATE", command=submit, bg="#f1c40f", fg="black").grid(row=len(fields), columnspan=2, pady=10)

    def delete_node_context(self):
        if self.selected_node_id is not None:
            nid = self.selected_node_id
            if messagebox.askyesno("Düğümü Sil", f"Düğüm {nid} ve tüm bağlantıları silinsin mi?", parent=self):
                try:
                    self.graph.remove_node(nid)
                    if nid in self.node_positions: 
                        del self.node_positions[nid]
                    
                    self.draw_graph()
                    self.status_label.configure(text=f"Node removed: {nid}")
                except Exception as e:
                    messagebox.showerror("Hata", str(e), parent=self)
            
            self.selected_node_id = None

    def on_double_click(self, event):
        for nid, (nx, ny) in self.node_positions.items():
            dist = ((nx - event.x)**2 + (ny - event.y)**2)**0.5
            
            if dist < self.node_radius:
                self.update_node_dialog(passed_nid=nid)
                return
            
    def on_canvas_click(self, event):
        for nid, pos in self.node_positions.items():
            if (event.x - pos[0])**2 + (event.y - pos[1])**2 <= self.node_radius**2:
                n = self.graph.nodes[nid]
                info = f"👤 {n.name}\nID: {n.id}\nAct: {n.aktiflik}\nConn: {n.baglanti_sayisi}"
                messagebox.showinfo("Profile", info)
                return
    import networkx as nx  

def calculate_layout(self):
    G_nx = nx.Graph()
    for nid, node in self.graph.nodes.items():
        G_nx.add_node(nid)
    for key, edge in self.graph.edges.items():
        G_nx.add_edge(edge.a, edge.b, weight=edge.weight)


    pos = nx.spring_layout(G_nx, k=0.5, iterations=50, seed=42)
    
   
    canvas_width = 800
    canvas_height = 600
    padding = 50
    
    new_positions = {}
    for nid, (x, y) in pos.items():
     
        screen_x = (x + 1) / 2 * (canvas_width - 2*padding) + padding
        screen_y = (y + 1) / 2 * (canvas_height - 2*padding) + padding
        new_positions[nid] = (screen_x, screen_y)
        
    self.node_positions = new_positions
    self.draw_graph()

if __name__ == "__main__":
    app = App()
    app.mainloop()