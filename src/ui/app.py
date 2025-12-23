import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from src.graph import Graph
from src.node import Node
import random
import time
import networkx as nx

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class App(ctk.CTk):
    def on_drag_start(self, event):
        # Tıklanan yerdeki objeyi bul
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        # Eğer bir node ise (tag olarak node_id verdiğimizi varsayalım)
        # Not: draw_graph içinde create_oval yaparken tags=f"node_{node_id}" eklemelisiniz.
        # Basit mantıkla en yakın node'u bulalım:
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
            # Pozisyonu güncelle
            self.node_positions[nid] = (event.x, event.y)
            # Sadece o an tekrar çiz (Performans için optimize edilebilir ama şimdilik draw_graph yeter)
            self.draw_graph()

    def on_drag_release(self, event):
        self.drag_data["node_id"] = None
    def __init__(self):
        super().__init__()
        self.drag_data = {"x": 0, "y": 0, "item": None, "node_id": None}
      
        self.title("Social Graph Analysis")
        self.geometry("1200x800")
        
        self.graph = Graph()
        self.node_positions = {}
        self.node_radius = 20
        
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)    

        self.setup_ui()
        self.status_label.configure(text="System Ready. Waiting for data...")
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_release)

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1) 

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

        self.create_sidebar_label("ALGORITHMS", row=10)
        self.create_sidebar_btn("Run BFS", self.run_bfs_ui, row=11)
        self.create_sidebar_btn("Run DFS", self.run_dfs_ui, row=12)
        self.create_sidebar_btn("Dijkstra (Shortest)", self.run_dijkstra_ui, row=13)
        self.create_sidebar_btn("A* Search", self.run_astar_ui, row=14)
        
        self.create_sidebar_label("ANALYSIS", row=15)
        self.create_sidebar_btn("Top 5 Influencers", self.show_top_nodes, row=16, color="orange")
        self.create_sidebar_btn("Welsh-Powell Color", self.run_coloring_ui, row=17, color="orange")
        self.create_sidebar_btn("Reset View", self.reset_view, row=18, color="red")

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
    def draw_graph(self, highlight_nodes=None, color_map=None, path_edges=None):
        self.canvas.delete("all")

        # --- 1. KENARLAR (EDGES) ---
        for key, edge in self.graph.edges.items():
            if edge.a in self.node_positions and edge.b in self.node_positions:
                x1, y1 = self.node_positions[edge.a]
                x2, y2 = self.node_positions[edge.b]
                
                # -- Görsel İyileştirme (Visual Polish) --
                # Varsayılan değerler
                color = "#95a5a6" # Orta Gri
                width = 2
                
                # Maliyet (Weight) düşükse -> Mesafe kısa -> Bağlantı GÜÇLÜ (Kalın ve Koyu)
                # Maliyet yüksekse -> Mesafe uzun -> Bağlantı ZAYIF (İnce ve Açık)
                try:
                    w = edge.weight
                    # Kalınlık Ayarı (Ters Orantı)
                    if w < 2.0: width = 4      # Çok sıkı dost
                    elif w < 5.0: width = 3    # Yakın
                    elif w < 10.0: width = 2   # Normal
                    else: width = 1            # Uzak/Zayıf

                    # Renk Ayarı (Grayscale - Koyudan Açığa)
                    # w=1 -> 50 (Koyu), w=20 -> 200 (Açık)
                    gray_val = int(max(50, min(220, 50 + (w * 8))))
                    color = f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}"
                except:
                    pass # Hata olursa varsayılanlar kalır

                # -- Yol Vurgusu (Path Highlight) --
                # Eğer bir algoritma çalıştıysa ve bu kenar yolun parçasıysa
                if path_edges and tuple(sorted((edge.a, edge.b))) in path_edges:
                    color = "#e74c3c" # Kırmızı
                    width = 4
                
                # Kenarı Çiz
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, smooth=True)
                
                # Ağırlık Etiketi (Küçük yuvarlak içinde)
                mx, my = (x1+x2)/2, (y1+y2)/2
                self.canvas.create_oval(mx-9, my-9, mx+9, my+9, fill="white", outline="#bdc3c7")
                self.canvas.create_text(mx, my, text=f"{edge.weight:.1f}", font=("Arial", 7), fill="black")

        # --- 2. DÜĞÜMLER (NODES) ---
        for node_id, pos in self.node_positions.items():
            x, y = pos
            r = self.node_radius
            
            fill_color = "#3498db" # Varsayılan Mavi
            outline_color = "white"
            
            # Renklendirme Önceliği: Algoritma Renkleri > Vurgu > Varsayılan
            if color_map and node_id in color_map:
                # Pastel Renk Paleti (Daha modern)
                palette = ["#e57373", "#81c784", "#64b5f6", "#fff176", "#ffb74d", "#ba68c8", "#90a4ae", "#4db6ac"]
                fill_color = palette[color_map[node_id] % len(palette)]
            elif highlight_nodes and node_id in highlight_nodes:
                fill_color = "#f1c40f" # Parlak Sarı (Seçili)

            # Gölge Efekti (Hafif gri, sağ-alt)
            self.canvas.create_oval(x-r+3, y-r+3, x+r+3, y+r+3, fill="#bdc3c7", outline="")
            
            # Düğüm Şekli
            # 'tags' parametresi çok önemli: Sürükle-Bırak yaparken hangi node'a tıklandığını anlamamızı sağlar.
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline=outline_color, width=2, tags=f"node_{node_id}")
            
            # ID Yazısı
            self.canvas.create_text(x, y, text=str(node_id), font=("Arial", 10, "bold"), fill="white", tags=f"node_{node_id}")
            
            # İsim Etiketi (Düğümün altında)
            if node_id in self.graph.nodes:
                node_name = self.graph.nodes[node_id].name
                # İsim çok uzunsa kırp
                display_name = node_name[:12] + "..." if len(node_name) > 12 else node_name
                self.canvas.create_text(x, y+r+15, text=display_name, font=("Arial", 9, "bold"), fill="#2c3e50")

   

    
    def add_node_dialog(self):
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

   # --- YARDIMCI TABLO FONKSİYONU (Bunu App sınıfı içine ekle) ---
    def show_results_table(self, title, columns, data):
        """Sonuçları yeni bir pencerede tablo olarak gösterir."""
        top = ctk.CTkToplevel(self)
        top.title(title)
        top.geometry("600x400")
        top.transient(self) # Ana pencereye bağlı kalsın
        
        # Tablo Stili
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2c3e50", foreground="white", fieldbackground="#2c3e50", rowheight=25)
        style.configure("Treeview.Heading", background="#34495e", foreground="white", font=('Arial', 10, 'bold'))
        
        # Treeview (Tablo) Oluşturma
        tree = ttk.Treeview(top, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
            
        for item in data:
            tree.insert("", "end", values=item)
            
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(top, orientation="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    # --- GÜNCELLENMİŞ ALGORİTMA FONKSİYONLARI ---

    def run_bfs_ui(self):
        start = simpledialog.askinteger("BFS", "Start Node ID:")
        if start:
            try:
                t0 = time.perf_counter()
                res = self.graph.run_bfs(start) # res = visited set
                t1 = time.perf_counter()
                
                # 1. Görselleştirme
                self.draw_graph(highlight_nodes=res)
                self.status_label.configure(text=f"BFS Done in {(t1-t0)*1000:.2f}ms. Visited: {len(res)}")
                
                # 2. Tablo Verisi Hazırlama
                table_data = []
                for node_id in res:
                    # Node bilgilerini al
                    name = self.graph.nodes[node_id].name if node_id in self.graph.nodes else "Unknown"
                    table_data.append((node_id, name, "Ziyaret Edildi"))
                
                # ID'ye göre sırala
                table_data.sort(key=lambda x: x[0])
                
                # Tabloyu Göster
                self.show_results_table(
                    title=f"BFS Sonuçları (Başlangıç: {start})",
                    columns=["Node ID", "İsim", "Durum"],
                    data=table_data
                )
            except Exception as e: messagebox.showerror("Error", str(e))

    def run_dfs_ui(self):
        start = simpledialog.askinteger("DFS", "Start Node ID:")
        if start:
            try:
                t0 = time.perf_counter()
                res = self.graph.run_dfs(start)
                t1 = time.perf_counter()
                
                self.draw_graph(highlight_nodes=res)
                self.status_label.configure(text=f"DFS Done in {(t1-t0)*1000:.2f}ms. Visited: {len(res)}")
                
                # Tablo Verisi
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
        s = simpledialog.askinteger("Dijkstra", "Start ID:")
        e = simpledialog.askinteger("Dijkstra", "End ID:")
        if s and e:
            try:
                t0 = time.perf_counter()
                dist, path = self.graph.run_dijkstra(s, e)
                t1 = time.perf_counter()
                
                # Görselleştirme
                edges = [(tuple(sorted((path[i], path[i+1])))) for i in range(len(path)-1)] if len(path) > 1 else []
                self.draw_graph(highlight_nodes=set(path), path_edges=edges)
                self.status_label.configure(text=f"Dijkstra Cost: {dist:.2f} | Time: {(t1-t0)*1000:.2f}ms")

                # Tablo Verisi (Adım Adım Yol)
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
        s = simpledialog.askinteger("A*", "Start ID:")
        e = simpledialog.askinteger("A*", "End ID:")
        if s and e:
            try:
                t0 = time.perf_counter()
                dist, path = self.graph.run_astar(s, e)
                t1 = time.perf_counter()
                
                edges = [(tuple(sorted((path[i], path[i+1])))) for i in range(len(path)-1)] if len(path) > 1 else []
                self.draw_graph(highlight_nodes=set(path), path_edges=edges)
                self.status_label.configure(text=f"A* Cost: {dist:.2f} | Time: {(t1-t0)*1000:.2f}ms")

                # Tablo Verisi
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
            
            self.draw_graph(color_map=colors)
            self.status_label.configure(text=f"Coloring Done in {(t1-t0)*1000:.2f}ms")
            
            # Tablo Verisi
            table_data = []
            for node_id, color_code in colors.items():
                name = self.graph.nodes[node_id].name
                table_data.append((node_id, name, f"Renk {color_code}"))
            
            table_data.sort(key=lambda x: x[0])
            
            self.show_results_table(
                title="Welsh-Powell Renklendirme Tablosu",
                columns=["Node ID", "İsim", "Atanan Renk"],
                data=table_data
            )
        except Exception as e: messagebox.showerror("Error", str(e))
    def run_coloring_ui(self):
        try:
            t0 = time.perf_counter()
            colors = self.graph.color_graph()
            self.draw_graph(color_map=colors)
            t1 = time.perf_counter()
            self.status_label.configure(text=f"Coloring Done in {(t1-t0)*1000:.2f}ms")
        except Exception as e: messagebox.showerror("Error", str(e))
    def show_top_nodes(self):
        try:
            # Komşu sayısına göre sırala
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
    
  

    def reset_view(self):
        self.draw_graph()
        self.status_label.configure(text="View Reset.")

    def add_edge_dialog(self): 
         a = simpledialog.askinteger("Link", "Source ID:")
         b = simpledialog.askinteger("Link", "Target ID:")
         if a and b:
             try:
                 self.graph.add_edge(a, b)
                 self.draw_graph()
                 self.status_label.configure(text=f"Linked: {a}-{b}")
             except Exception as e: messagebox.showerror("Error", str(e))
    
    def remove_edge_dialog(self): 
         a = simpledialog.askinteger("Unlink", "Source ID:")
         b = simpledialog.askinteger("Unlink", "Target ID:")
         if a and b:
             try:
                 self.graph.remove_edge(a, b)
                 self.draw_graph()
                 self.status_label.configure(text=f"Unlinked: {a}-{b}")
             except Exception as e: messagebox.showerror("Error", str(e))

    def remove_node_dialog(self):
         nid = simpledialog.askinteger("Remove", "Node ID:")
         if nid:
             try:
                 self.graph.remove_node(nid)
                 if nid in self.node_positions: del self.node_positions[nid]
                 self.draw_graph()
                 self.status_label.configure(text=f"Node Removed: {nid}")
             except Exception as e: messagebox.showerror("Error", str(e))
    
    def update_node_dialog(self):
        nid = simpledialog.askinteger("Update", "Node ID:")
        if nid and nid in self.graph.nodes:
             messagebox.showinfo("Info", "Update dialog açılacak (Eski kodu ekle)")
        
    def on_canvas_click(self, event):
        for nid, pos in self.node_positions.items():
            if (event.x - pos[0])**2 + (event.y - pos[1])**2 <= self.node_radius**2:
                n = self.graph.nodes[nid]
                info = f"👤 {n.name}\nID: {n.id}\nAct: {n.aktiflik}\nConn: {n.baglanti_sayisi}"
                messagebox.showinfo("Profile", info)
                return
    import networkx as nx  # En tepeye ekleyin

# Mevcut graph yapınızı geçici bir NetworkX grafına çevirip pozisyon hesaplatın
def calculate_layout(self):
    G_nx = nx.Graph()
    for nid, node in self.graph.nodes.items():
        G_nx.add_node(nid)
    for key, edge in self.graph.edges.items():
        G_nx.add_edge(edge.a, edge.b, weight=edge.weight)

    # Spring Layout: Düğümleri fizik kurallarına göre dağıtır
    # k parametresi: Düğümler arası ideal mesafe (Artırın ki ferah olsun)
    # scale: Canvas boyutuna göre ölçekleme
    pos = nx.spring_layout(G_nx, k=0.5, iterations=50, seed=42)
    
    # NetworkX 0-1 arası koordinat verir, bunu Canvas boyutuna (800x600) genişletmeliyiz
    canvas_width = 800
    canvas_height = 600
    padding = 50
    
    new_positions = {}
    for nid, (x, y) in pos.items():
        # -1 ile 1 arasını canvas genişliğine uyarla
        screen_x = (x + 1) / 2 * (canvas_width - 2*padding) + padding
        screen_y = (y + 1) / 2 * (canvas_height - 2*padding) + padding
        new_positions[nid] = (screen_x, screen_y)
        
    self.node_positions = new_positions
    self.draw_graph()

if __name__ == "__main__":
    app = App()
    app.mainloop()