import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox, simpledialog
from src.graph import Graph
from src.node import Node
import random
import time
import networkx as nx
import ctypes
try:
  
    ctypes.windll.shcore.SetProcessDpiAwareness(2) 
except Exception:
    try:

        ctypes.windll.user32.SetProcessDPIAware()
    except: 
        pass 


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
 
        self.active_color_map = None  
        self.active_palette = None    
 
        self.node_radius = 16
        
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
        
 
        self.after(100, self.draw_graph)


    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(25, weight=1)

        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="Social Graph Analysis", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.create_sidebar_label("DATA MANAGEMENT", row=1)
        self.create_sidebar_btn("Add Node (+)", self.add_node_dialog, row=2)
        self.create_sidebar_btn("Update/Edit Node", self.update_node_dialog, row=3)
        self.create_sidebar_btn("Remove Node (-)", self.remove_node_dialog, row=4)
        self.create_sidebar_btn("Create Edge", self.add_edge_dialog, row=5)
        self.create_sidebar_btn("Remove Link", self.remove_edge_dialog, row=6)
        self.create_sidebar_btn("Random Nodes", self.generate_random_dialog, row=7)

        self.create_sidebar_label("FILE IO", row=8)
        self.create_sidebar_btn("Load CSV Data", self.load_csv, row=9, color="#406b27")
        self.create_sidebar_btn("Save to CSV", self.save_csv, row=10, color="#406b27")
        self.create_sidebar_btn("Export HD Image", self.save_hd_image, row=11, color="#406b27")

        self.create_sidebar_label("ALGORITHMS", row=12)
        self.create_sidebar_btn("Run BFS", self.run_bfs_ui, row=13, color="#8e44ad")
        self.create_sidebar_btn("Run DFS", self.run_dfs_ui, row=14, color="#8e44ad")
        self.create_sidebar_btn("Dijkstra Search", self.run_dijkstra_ui, row=15, color="#8e44ad")
        self.create_sidebar_btn("A* Search", self.run_astar_ui, row=16, color="#8e44ad")
        
        self.create_sidebar_label("ANALYSIS", row=17)
        self.create_sidebar_btn("Ranking List", self.show_full_ranking, row=18, color="#737a32")
        self.create_sidebar_btn("Top 5 Influencers", self.show_top_5_influencers, row=19, color="#737a32")
        self.create_sidebar_btn("Welsh-Powell Color", self.run_coloring_ui, row=20, color="#737a32")
        self.create_sidebar_btn("Find Communities", self.run_connected_components_ui, row=21, color="#737a32")

        self.create_sidebar_label("RESET", row=22)
        self.create_sidebar_btn("Reset View", self.reset_view, row=23, color="#813636")
        self.create_sidebar_btn("Clear All Data", self.clear_all_nodes, row=24, color="#813636")

        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.canvas_frame = ctk.CTkFrame(self.right_frame, fg_color="#ecf0f1") 
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
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

    def create_sidebar_btn(self, text, command, row, color="primary"):
       
        colors = {
            "green": "#2ecc71",
            "red": "#e74c3c",
            "orange": "#e67e22", 
            "gray": "#95a5a6",
            "primary": "#34495e" 
        }
        
     
        if color.startswith("#"):
            fg_color = color
        
            hover_color = color 
        else:
            fg_color = colors.get(color, colors["primary"])
            hover_color = None 
            
        btn = ctk.CTkButton(self.sidebar, text=text, command=command, 
                            fg_color=fg_color, hover_color=hover_color)
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew") 

    def draw_graph(self, highlight_nodes=None, color_map=None, path_edges=None, custom_palette=None):
        self.canvas.delete("all")
        
  
        if color_map is None and self.active_color_map is not None:
            color_map = self.active_color_map
            custom_palette = self.active_palette

        
        self.draw_grid_mpl()
    
        mpl_blue = "#1f77b4"
        mpl_orange = "#ff7f0e"
        mpl_grey = "#7f7f7f"
        mpl_red = "#d62728"
        
        tab10 = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
        ]

      
        labels_to_draw = []

     
        for key, edge in self.graph.edges.items():
            if edge.a in self.node_positions and edge.b in self.node_positions:
                x1, y1 = self.node_positions[edge.a]
                x2, y2 = self.node_positions[edge.b]
                
                width = 1.0  
                color = mpl_grey
                
                if edge.weight < 5.0: width = 2.0
                
                if path_edges and tuple(sorted((edge.a, edge.b))) in path_edges:
                    color = mpl_red
                    width = 2.5
                
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, capstyle=tk.BUTT)

          
                mx, my = (x1+x2)/2, (y1+y2)/2
                labels_to_draw.append((mx, my, f"{edge.weight:.1f}"))

    
        for node_id, pos in self.node_positions.items():
            x, y = pos
            r = 15 
            
            fill_color = mpl_blue
            outline_color = "black"
            
            if color_map and node_id in color_map:
                palette = custom_palette if custom_palette else tab10
                fill_color = palette[color_map[node_id] % len(palette)]
            elif highlight_nodes and node_id in highlight_nodes:
                fill_color = mpl_orange

         
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline=outline_color, width=1, tags=f"node_{node_id}")
            
       
            self.canvas.create_text(x, y, text=str(node_id), font=("Arial", 9, "bold"), fill="white", tags=f"node_{node_id}")
            
          
            if node_id in self.graph.nodes:
                name = self.graph.nodes[node_id].name
                self.canvas.create_text(x+r+5, y-r+5, text=name, anchor="w", font=("Arial", 8), fill="black")

    
        for mx, my, text in labels_to_draw:

            self.canvas.create_rectangle(mx-12, my-7, mx+12, my+7, fill="white", outline="#cccccc", width=1)
            
        
            self.canvas.create_text(mx, my, text=text, font=("Arial", 8, "bold"), fill="black")

    def draw_grid_mpl(self):
        """Matplotlib stili ızgara (dotted lines)."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50: w = 2000
        if h < 50: h = 2000
        
  
        grid_color = "#e6e6e6"
        
        for i in range(0, w, 50):
            self.canvas.create_line(i, 0, i, h, fill=grid_color, dash=(2, 4))
        for i in range(0, h, 50):
            self.canvas.create_line(0, i, w, i, fill=grid_color, dash=(2, 4))

    
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
      
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
   
        if w < 50: w = 2000
        if h < 50: h = 2000
        
        step = 50 
        
     
        for i in range(0, w, step):
           
            if i % 100 == 0:
                color = "#bdc3c7" 
            else:
                color = "#e5e8e8" 
                
            self.canvas.create_line(i, 0, i, h, fill=color, width=1)

    
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
        self.active_color_map = None
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
        self.active_color_map = None
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
        self.active_color_map = None
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
        self.active_color_map = None
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
            
            palette = [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
                "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
            ]
            import random
            random.shuffle(palette)
            
       
            self.active_color_map = colors
            self.active_palette = palette
          
            
            self.draw_graph(color_map=colors, custom_palette=palette)
            self.status_label.configure(text=f"Coloring Done in {(t1-t0)*1000:.2f}ms")

       
            table_data = []
            for node_id, color_code in colors.items():
                name = self.graph.nodes[node_id].name if node_id in self.graph.nodes else "Unknown"
                assigned_color = palette[color_code % len(palette)]
                table_data.append((node_id, name, f"Grup {color_code}"))
            
            table_data.sort(key=lambda x: x[0])
            self.show_results_table(title="Welsh-Powell Renklendirme", columns=["ID", "İsim", "Grup"], data=table_data)
            
        except Exception as e: 
            messagebox.showerror("Error", str(e), parent=self)

    def show_top_nodes(self):
        try:
 
            nodes = sorted(self.graph.nodes.values(), key=lambda x: len(x.neighbors), reverse=True)
            
            table_data = []
            for i, n in enumerate(nodes, 1):
                table_data.append((i, n.id, n.name, len(n.neighbors)))
            
            self.show_results_table(
                title="Popülerlik Sıralaması (Tüm Kullanıcılar)",
                columns=["Sıra", "ID", "İsim", "Bağlantı Sayısı"],
                data=table_data
            )
        except Exception as e:
            messagebox.showerror("Hata", str(e), parent=self)
    
  
    def create_context_menu(self):
        """Sağ tık menülerini oluşturur."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Düğüm Ekle", command=self.add_node_context)
        self.context_menu.add_command(label="Bağlantı (Edge) Oluştur", command=self.add_edge_dialog)
        
        self.edge_menu = tk.Menu(self, tearoff=0)
        self.edge_menu.add_command(label="Bu Bağlantıyı Sil", command=self.delete_edge_context)

        self.node_menu = tk.Menu(self, tearoff=0)
        self.node_menu.add_command(label="Düzenle", command=lambda: self.update_node_dialog(passed_nid=self.selected_node_id))
        self.node_menu.add_command(label="Bağlantı Ekle (+Edge)", command=self.add_edge_from_node_context)
        self.node_menu.add_command(label="Bu Düğümü Sil", command=self.delete_node_context)

    def on_right_click(self, event):
        """Sağ tıklama olayını yönetir: Node, Edge veya Boşluk tespiti."""
        click_x, click_y = event.x, event.y
        
    
        for nid, (nx, ny) in self.node_positions.items():
            dist = ((nx - click_x)**2 + (ny - click_y)**2)**0.5
            if dist < self.node_radius:
              
                self.selected_node_id = nid
                try:
                    self.node_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.node_menu.grab_release()
                return

    
        closest_edge = None
        min_dist = 10.0 

        for key, edge in self.graph.edges.items():
            if edge.a in self.node_positions and edge.b in self.node_positions:
                x1, y1 = self.node_positions[edge.a]
                x2, y2 = self.node_positions[edge.b]
                
           
                d = self.point_to_line_dist(click_x, click_y, x1, y1, x2, y2)
                
                if d < min_dist:
                    min_dist = d
                    closest_edge = key
        
     
        if closest_edge:
            self.selected_edge_key = closest_edge
            try:
                self.edge_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.edge_menu.grab_release()
            return

     
        self.last_click_pos = (click_x, click_y)
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

   
    def point_to_line_dist(self, px, py, x1, y1, x2, y2):
        """Bir noktanın (px,py) bir doğru parçasına (x1,y1 - x2,y2) en kısa uzaklığı."""
      
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
        self.active_color_map = None 
        self.active_palette = None
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
        """Mevcut grafiği yüksek kalitede kaydeder."""
        try:
           
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("PDF Document", "*.pdf"), ("All Files", "*.*")],
                title="Yüksek Kaliteli Grafiği Kaydet",
                initialfile="Proje_Grafigi_HD.png"
            )
            
          
            if not file_path:
                return

            import matplotlib.pyplot as plt
            import networkx as nx
            
            
            plt.figure(figsize=(12, 8), dpi=300)
            
            G = nx.Graph()
            for nid, node in self.graph.nodes.items():
                G.add_node(nid)
            for key, edge in self.graph.edges.items():
                G.add_edge(edge.a, edge.b, weight=edge.weight)
            
            height = self.canvas.winfo_height()
          
            pos = {nid: (x, height - y) for nid, (x, y) in self.node_positions.items()}
            
       
            nx.draw_networkx_nodes(G, pos, node_size=300, node_color="#1f77b4", edgecolors="black", linewidths=1)
            nx.draw_networkx_labels(G, pos, font_color="white", font_size=8, font_weight="bold", font_family="Arial")
            nx.draw_networkx_edges(G, pos, edge_color="#7f7f7f", width=1.0, alpha=0.7)
            
          
            edge_labels = {(e[0], e[1]): f"{e[2]['weight']:.1f}" for e in G.edges(data=True)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6, font_family="Arial")
            
            plt.axis("off")
            
         
            plt.savefig(file_path, bbox_inches="tight")
            plt.close()
            
            messagebox.showinfo("Başarılı", f"Dosya başarıyla kaydedildi:\n{file_path}")
            
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
    
    def generate_random_dialog(self):
        """
        Kullanıcıdan sayı alarak rastgele ancak gerçekçi bir sosyal ağ grafı oluşturur.
        Bazı düğümler izole kalabilir, bazıları popüler olabilir.
        """
        count = simpledialog.askinteger("Rastgele Oluştur", 
                                      "Kaç adet düğüm (Node) oluşturulsun?", 
                                      minvalue=2, maxvalue=500, parent=self)
        if not count:
            return

        self.graph = Graph()
        self.node_positions = {}
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100: w = 1000 
        if h < 100: h = 800
        padding = 50

        try:
            for i in range(1, count + 1):
                name = f"User_{i}"
                
                akt = round(random.random(), 2)         
                etk = round(random.uniform(1, 100), 2)   
                bagl = 0                                 
                
                node = Node(i, name, akt, etk, bagl)
                self.graph.add_node(node)
                
                rx = random.randint(padding, w - padding)
                ry = random.randint(padding, h - padding)
                self.node_positions[i] = (rx, ry)

            node_ids = list(self.graph.nodes.keys())
            
            random.shuffle(node_ids)
            
            for u in node_ids:
                if random.random() < 0.30:
                    continue
                
                num_links = random.choices([1, 2, 3, 4, 5], weights=[0.50, 0.30, 0.15, 0.04, 0.01])[0]
                
                candidates = [n for n in node_ids if n != u]
                if not candidates: continue
                
                targets = random.sample(candidates, min(len(candidates), num_links))
                
                for v in targets:
                    try:
                        self.graph.add_edge(u, v)
                    except: 
                        pass 

            self.draw_graph()
            
            edge_count = len(self.graph.edges)
            self.status_label.configure(text=f"Rastgele Graf Oluşturuldu: {count} Düğüm, {edge_count} Bağlantı")
            
            messagebox.showinfo("Başarılı", f"{count} düğümlü gerçekçi sosyal ağ oluşturuldu.\nBağlantı Sayısı: {edge_count}", parent=self)

        except Exception as e:
            messagebox.showerror("Hata", str(e), parent=self)

    def run_connected_components_ui(self):
        try:
            components = self.graph.connected_components()
            count = len(components)
            
            self.status_label.configure(text=f"Analiz Tamamlandı: {count} adet ayrık topluluk bulundu.")
            
            table_data = []
            
            color_map = {}
            
            for idx, comp in enumerate(components, 1):
                member_names = []
                for node_id in comp:
                    color_map[node_id] = idx 
                    
                    if node_id in self.graph.nodes:
                        member_names.append(self.graph.nodes[node_id].name)
                
                members_str = ", ".join(member_names)
                table_data.append((f"Topluluk {idx}", len(comp), members_str))
            
            self.show_results_table(
                title=f"Bağlı Bileşenler Analizi ({count} Grup)",
                columns=["Grup Adı", "Kişi Sayısı", "Üyeler"],
                data=table_data
            )
            
            palette = [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
                "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
            ]
            
            self.active_color_map = color_map
            self.active_palette = palette
            self.draw_graph(color_map=color_map, custom_palette=palette)
            
            messagebox.showinfo("Analiz Sonucu", f"Toplam {count} adet birbirinden bağımsız topluluk (bağlı bileşen) tespit edildi.\nGrafik bu gruplara göre renklendirildi.")

        except Exception as e:
            messagebox.showerror("Hata", str(e))
    
    def show_full_ranking(self):
        """Tüm kullanıcıları bağlantı sayısına göre sıralar ve tablo olarak gösterir."""
        try:
            nodes = sorted(self.graph.nodes.values(), key=lambda x: len(x.neighbors), reverse=True)
            
            table_data = []
            for i, n in enumerate(nodes, 1):
                table_data.append((i, n.id, n.name, len(n.neighbors)))
            
            self.show_results_table(
                title="Popülerlik Sıralaması (Tüm Kullanıcılar)",
                columns=["Sıra", "ID", "İsim", "Bağlantı Sayısı"],
                data=table_data
            )
        except Exception as e:
            messagebox.showerror("Hata", str(e), parent=self)

    def show_top_5_influencers(self):
        """Sadece en yüksek 5 kullanıcıyı alır, tabloda gösterir ve GRAFİKTE VURGULAR."""
        try:
            all_nodes = sorted(self.graph.nodes.values(), key=lambda x: len(x.neighbors), reverse=True)
            top_5_nodes = all_nodes[:5]
            
            if not top_5_nodes:
                messagebox.showinfo("Bilgi", "Graf boş, analiz yapılacak düğüm yok.")
                return

            top_5_ids = {n.id for n in top_5_nodes}
            self.draw_graph(highlight_nodes=top_5_ids)
            self.status_label.configure(text="En etkili 5 kullanıcı vurgulandı.")
            
            table_data = []
            for i, n in enumerate(top_5_nodes, 1):
                table_data.append((i, n.id, n.name, len(n.neighbors)))
            
            self.show_results_table(
                title="En Etkili 5 Kullanıcı (Top 5)",
                columns=["Sıra", "ID", "İsim", "Bağlantı Sayısı"],
                data=table_data
            )
        except Exception as e:
            messagebox.showerror("Hata", str(e), parent=self)

    def add_edge_from_node_context(self):
        """Sağ tıklanan düğümden başka bir düğüme bağlantı kurar."""
        if self.selected_node_id is not None:
            source_id = self.selected_node_id
            
          
            target_id = simpledialog.askinteger("Bağlantı Ekle", 
                                              f"Kaynak: Node {source_id}\n\nHedef Node ID:", 
                                              parent=self)
            
            if target_id is not None:
              
                if source_id == target_id:
                    messagebox.showwarning("Uyarı", "Kendine bağlantı (Self-loop) oluşturulamaz!", parent=self)
                    return

                try:
                  
                    self.graph.add_edge(source_id, target_id)
                    
                   
                    self.draw_graph()
                    self.status_label.configure(text=f"Linked: {source_id} -> {target_id}")
                    
                except Exception as e:
                    messagebox.showerror("Hata", str(e), parent=self)
                    
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