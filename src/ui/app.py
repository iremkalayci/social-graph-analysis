import tkinter as tk
from src.graph import Graph
from tkinter import messagebox
from src.node import Node


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Social Graph Analysis")

        self.graph = Graph()

        self.setup_ui()

    def setup_ui(self):
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y) 
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.node_positions = {}
        self.node_radius = 20
                         
    

        btn_add_node = tk.Button(control_frame, text="Add Node", command=self.add_node)
        btn_add_node.pack(fill=tk.X, pady=5)

        btn_add_edge = tk.Button(control_frame, text="Add Edge", command=self.add_edge)
        btn_add_edge.pack(fill=tk.X, pady=5)

        btn_bfs = tk.Button(control_frame, text="Run BFS", command=self.run_bfs)
        btn_bfs.pack(fill=tk.X, pady=5)

        btn_dfs = tk.Button(control_frame, text="Run DFS", command=self.run_dfs)
        btn_dfs.pack(fill=tk.X, pady=5)

    def add_node(self):
        win=tk.Toplevel(self.root)
        win.title("add node")
        labels=["ID", "Name", "Activity", "Interaction", "Connection Count"]
        entries = []
        for i, text in enumerate(labels):
            tk.Label(win, text=text).grid(row=i, column=0, padx=5, pady=5)
            e = tk.Entry(win)
            e.grid(row=i, column=1, padx=5, pady=5)
            entries.append(e)
        def submit():
            try:
                node=Node(
                    int(entries[0].get()),
                    entries[1].get(),
                    float(entries[2].get()),
                    float(entries[3].get()),
                    int(entries[4].get())
                )
                self.graph.add_node(node)
                x = 50 + (len(self.node_positions) * 80) % 500
                y = 50 + ((len(self.node_positions) * 80) // 500) * 100
                self.node_positions[node.id] = (x, y)
                self.canvas.create_oval(
                    x - self.node_radius, y - self.node_radius,
                    x + self.node_radius, y + self.node_radius,
                    fill="lightblue"
                )
                self.canvas.create_text(x, y, text=str(node.id))
                messagebox.showinfo("Success", "Node added successfully")
                win.destroy()
            except Exception as e:
                  messagebox.showerror("Error", str(e))
        tk.Button(win, text="Add", command=submit).grid(row=len(labels), columnspan=2, pady=10)

    
        

    def add_edge(self):
        win = tk.Toplevel(self.root)
        win.title("Add Edge")
        tk.Label(win, text="From Node ID").grid(row=0, column=0)
        tk.Label(win, text="To Node ID").grid(row=1, column=0)
        e1 = tk.Entry(win)
        e2 = tk.Entry(win)
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        def submit():
            try:
                a=int(e1.get())
                b=int(e2.get())
                self.graph.add_edge(a, b)
                x1, y1 = self.node_positions[a]
                x2, y2 = self.node_positions[b]
                self.canvas.create_line(x1, y1, x2, y2, width=2)
                win.destroy()
            except Exception as err:
                messagebox.showerror("Error", str(err))
        tk.Button(win, text="Add Edge", command=submit).grid(
        row=2, column=0, columnspan=2, pady=10
    )
    
                
    
       
        

    def run_bfs(self):
        print("BFS calistirildi")

    def run_dfs(self):
        print("DFS calistirildi")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
