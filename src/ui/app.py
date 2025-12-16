import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from src.graph import Graph
from src.node import Node
import random
import time

COLOR_SIDEBAR = "#2c3e50"
COLOR_CANVAS = "#ecf0f1"
COLOR_BTN_BG = "#34495e"
COLOR_BTN_FG = "white"
COLOR_ACCENT = "#e67e22"
COLOR_NODE_DEFAULT = "#3498db"
COLOR_NODE_HIGHLIGHT = "#f1c40f"
COLOR_EDGE = "#95a5a6"
FONT_HEADER = ("Helvetica", 12, "bold")
FONT_NORMAL = ("Helvetica", 10)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Social Graph Analysis v2.0")
        self.root.geometry("1100x700")
        
        self.graph = Graph()
        self.node_positions = {}
        self.node_radius = 25

        self.setup_layout()
        
        self.status_var.set("System ready. Please add nodes or load a CSV file.")

    def setup_layout(self):
        self.sidebar = tk.Frame(self.root, width=280, bg=COLOR_SIDEBAR)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        lbl_title = tk.Label(self.sidebar, text="SNA TOOLKIT", bg=COLOR_SIDEBAR, fg="white", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=20)

        self.create_menu_group("DATA OPERATIONS", [
            ("Add Node (+)", self.add_node_dialog),
            ("Update Node (Edit)", self.update_node_dialog),
            ("Remove Node (-)", self.remove_node_dialog),
            ("Add Edge (Link)", self.add_edge_dialog),
            ("Remove Edge (Unlink)", self.remove_edge_dialog),
            ("Load CSV", self.load_csv),
            ("Save CSV", self.save_csv)
        ])

        self.create_menu_group("ALGORITHMS", [
            ("Run BFS", self.run_bfs_ui),
            ("Run DFS", self.run_dfs_ui),
            ("Run Dijkstra (Shortest Path)", self.run_dijkstra_ui),
            ("Run A* (A-Star)", self.run_astar_ui)
        ])

        self.create_menu_group("ANALYSIS & VIEW", [
            ("Top 5 Nodes (Centrality)", self.show_top_nodes),
            ("Color Graph (Welsh-Powell)", self.run_coloring_ui),
            ("Clear Canvas", self.reset_view)
        ])

        self.main_area = tk.Frame(self.root, bg=COLOR_CANVAS)
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_area, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.main_area, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#dfe6e9", font=("Arial", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu_group(self, title, buttons):
        frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR)
        frame.pack(fill=tk.X, padx=15, pady=10)

        lbl = tk.Label(frame, text=title, bg=COLOR_SIDEBAR, fg="#bdc3c7", font=("Arial", 8, "bold"), anchor="w")
        lbl.pack(fill=tk.X)

        for text, command in buttons:
            btn = tk.Button(frame, text=text, command=command, 
                            bg=COLOR_BTN_BG, fg=COLOR_BTN_FG, 
                            activebackground=COLOR_ACCENT, activeforeground="white",
                            bd=0, font=FONT_NORMAL, height=1, cursor="hand2", anchor="w", padx=10)
            btn.pack(fill=tk.X, pady=2)

    def draw_graph(self, highlight_nodes=None, color_map=None, path_edges=None):
        self.canvas.delete("all")

        for key, edge in self.graph.edges.items():
            if edge.a in self.node_positions and edge.b in self.node_positions:
                x1, y1 = self.node_positions[edge.a]
                x2, y2 = self.node_positions[edge.b]
                
                color = COLOR_EDGE
                width = 2
                
                if path_edges and tuple(sorted((edge.a, edge.b))) in path_edges:
                    color = "#e74c3c"
                    width = 4
                
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, smooth=True)
                
                mx, my = (x1+x2)/2, (y1+y2)/2
                self.canvas.create_rectangle(mx-10, my-8, mx+10, my+8, fill="white", outline=COLOR_EDGE)
                self.canvas.create_text(mx, my, text=f"{edge.weight:.1f}", font=("Arial", 8), fill="#2c3e50")

        for node_id, pos in self.node_positions.items():
            x, y = pos
            r = self.node_radius
            
            fill_color = COLOR_NODE_DEFAULT
            
            if color_map and node_id in color_map:
                palette = ["#e74c3c", "#2ecc71", "#9b59b6", "#f1c40f", "#1abc9c", "#34495e", "#e67e22"]
                fill_color = palette[color_map[node_id] % len(palette)]
            elif highlight_nodes and node_id in highlight_nodes:
                fill_color = COLOR_NODE_HIGHLIGHT

            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline="white", width=2)
            
            self.canvas.create_text(x, y, text=str(node_id), font=("Arial", 10, "bold"), fill="white")
            
            node_name = self.graph.nodes[node_id].name
            self.canvas.create_text(x, y+r+10, text=node_name[:10], font=("Arial", 8), fill="#7f8c8d")

    def add_node_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Node")
        win.configure(bg=COLOR_CANVAS)
        
        fields = ["ID", "Name", "Activity (0-1)", "Interaction", "Connection Count"]
        entries = []
        for i, f in enumerate(fields):
            tk.Label(win, text=f, bg=COLOR_CANVAS).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            e = tk.Entry(win)
            e.grid(row=i, column=1, padx=10, pady=5)
            entries.append(e)

        def submit():
            try:
                vals = [e.get() for e in entries]
                node = Node(int(vals[0]), vals[1], float(vals[2]), float(vals[3]), int(vals[4]))
                self.graph.add_node(node)
                self.node_positions[node.id] = (random.randint(50, 700), random.randint(50, 500))
                self.draw_graph()
                self.status_var.set(f"Node added: {node.name}")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(win, text="SAVE", command=submit, bg=COLOR_BTN_BG, fg="white").grid(row=len(fields), columnspan=2, pady=15)

    def add_edge_dialog(self):
        a = simpledialog.askinteger("Add Edge", "Source Node ID:")
        b = simpledialog.askinteger("Add Edge", "Target Node ID:")
        if a and b:
            try:
                self.graph.add_edge(a, b)
                self.draw_graph()
                self.status_var.set(f"Edge created: {a} <--> {b}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def update_node_dialog(self):
        nid = simpledialog.askinteger("Update Node", "Node ID to update:")
        if nid:
            if nid not in self.graph.nodes:
                messagebox.showerror("Error", "Node not found!")
                return
            
            current_node = self.graph.nodes[nid]
            
            win = tk.Toplevel(self.root)
            win.title(f"Update Node {nid}")
            win.configure(bg=COLOR_CANVAS)
            
            fields = ["Name", "Activity", "Interaction", "Connection Count"]
            defaults = [current_node.name, current_node.aktiflik, current_node.etkilesim, current_node.baglanti_sayisi]
            entries = []
            
            for i, f in enumerate(fields):
                tk.Label(win, text=f, bg=COLOR_CANVAS).grid(row=i, column=0, padx=10, pady=5, sticky="e")
                e = tk.Entry(win)
                e.insert(0, str(defaults[i]))
                e.grid(row=i, column=1, padx=10, pady=5)
                entries.append(e)

            def submit():
                try:
                    vals = [e.get() for e in entries]
                    self.graph.update_node(nid, vals[0], float(vals[1]), float(vals[2]), int(vals[3]))
                    self.draw_graph()
                    self.status_var.set(f"Node {nid} updated.")
                    win.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            tk.Button(win, text="UPDATE", command=submit, bg=COLOR_BTN_BG, fg="white").grid(row=len(fields), columnspan=2, pady=15)

    def remove_node_dialog(self):
        nid = simpledialog.askinteger("Remove Node", "Node ID to remove:")
        if nid:
            try:
                self.graph.remove_node(nid)
                if nid in self.node_positions:
                    del self.node_positions[nid]
                
                self.draw_graph()
                self.status_var.set(f"Node {nid} removed.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def remove_edge_dialog(self):
        a = simpledialog.askinteger("Remove Edge", "Source Node ID:")
        b = simpledialog.askinteger("Remove Edge", "Target Node ID:")
        if a and b:
            try:
                self.graph.remove_edge(a, b)
                self.draw_graph()
                self.status_var.set(f"Edge removed: {a} <--> {b}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def run_bfs_ui(self):
        start = simpledialog.askinteger("BFS", "Start Node ID:")
        if start:
            try:
                t0 = time.perf_counter()
                res = self.graph.run_bfs(start)
                self.draw_graph(highlight_nodes=res)
                t1 = time.perf_counter()
                duration_ms = (t1 - t0) * 1000
                self.status_var.set(f"BFS Completed in {duration_ms:.4f} ms. Visited: {len(res)} nodes.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def run_dfs_ui(self):
        start = simpledialog.askinteger("DFS", "Start Node ID:")
        if start:
            try:
                t0 = time.perf_counter()
                res = self.graph.run_dfs(start)
                self.draw_graph(highlight_nodes=res)
                t1 = time.perf_counter()
                duration_ms = (t1 - t0) * 1000
                self.status_var.set(f"DFS Completed in {duration_ms:.4f} ms. Visited: {len(res)} nodes.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def run_dijkstra_ui(self):
        s = simpledialog.askinteger("Dijkstra", "Start Node ID:")
        e = simpledialog.askinteger("Dijkstra", "End Node ID:")
        if s and e:
            try:
                t0 = time.perf_counter()
                dist, path = self.graph.run_dijkstra(s, e)
                edges = []
                if len(path) > 1:
                    edges = [tuple(sorted((path[i], path[i+1]))) for i in range(len(path)-1)]
                self.draw_graph(highlight_nodes=set(path), path_edges=edges)
                t1 = time.perf_counter()
                duration_ms = (t1 - t0) * 1000
                self.status_var.set(f"Shortest Path: {dist:.2f} | Time: {duration_ms:.4f} ms")
            except Exception as err:
                messagebox.showerror("Error", str(err))

    def run_astar_ui(self):
        s = simpledialog.askinteger("A*", "Start Node ID:")
        e = simpledialog.askinteger("A*", "End Node ID:")
        if s and e:
            try:
                t0 = time.perf_counter()
                dist, path = self.graph.run_astar(s, e)
                edges = []
                if len(path) > 1:
                    edges = [tuple(sorted((path[i], path[i+1]))) for i in range(len(path)-1)]
                self.draw_graph(highlight_nodes=set(path), path_edges=edges)
                t1 = time.perf_counter()
                duration_ms = (t1 - t0) * 1000
                self.status_var.set(f"A* Result Cost: {dist:.2f} | Time: {duration_ms:.4f} ms")
            except Exception as err:
                messagebox.showerror("Error", str(err))

    def run_coloring_ui(self):
        try:
            t0 = time.perf_counter()
            colors = self.graph.color_graph()
            self.draw_graph(color_map=colors)
            t1 = time.perf_counter()
            duration_ms = (t1 - t0) * 1000
            self.status_var.set(f"Graph colored using Welsh-Powell in {duration_ms:.4f} ms.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_top_nodes(self):
        try:
            nodes = sorted(self.graph.nodes.values(), key=lambda x: len(x.neighbors), reverse=True)[:5]
            msg = "TOP 5 NODES (CENTRALITY)\n" + "-"*30 + "\n"
            for i, n in enumerate(nodes, 1):
                msg += f"{i}. {n.name} (ID: {n.id}) -> {len(n.neighbors)} Connections\n"
            messagebox.showinfo("Analysis Report", msg)
        except:
            pass

    def save_csv(self):
        from tkinter import filedialog
        import csv
        
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if f:
            try:
                with open(f, 'w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow(["DugumId", "Name", "Ozellik_I", "Ozellik_II", "Ozellik_III", "Komsular", "Pos_X", "Pos_Y"])
                    
                    for n in self.graph.nodes.values():
                        komsular = ",".join(map(str, n.neighbors))
                        x, y = self.node_positions.get(n.id, (0, 0))
                        
                        writer.writerow([
                            n.id, 
                            n.name, 
                            n.aktiflik, 
                            n.etkilesim, 
                            n.baglanti_sayisi, 
                            f"{komsular}",
                            x, 
                            y
                        ])
                self.status_var.set("Data saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_csv(self):
        from tkinter import filedialog
        from src.csv_loader import CSVLoader
        import random
        
        f = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
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
                self.status_var.set(f"CSV Loaded: {len(nodes)} nodes restored.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def reset_view(self):
        self.draw_graph()
        self.status_var.set("View reset.")

    def on_canvas_click(self, event):
        for nid, pos in self.node_positions.items():
            if (event.x - pos[0])**2 + (event.y - pos[1])**2 <= self.node_radius**2:
                n = self.graph.nodes[nid]
                info = f"👤 Name: {n.name}\n🆔 ID: {n.id}\n📊 Activity: {n.aktiflik}\n💬 Interaction: {n.etkilesim}\n🔗 Connections: {n.baglanti_sayisi}"
                messagebox.showinfo("Node Profile", info)
                return

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app = App(root)
    root.mainloop()