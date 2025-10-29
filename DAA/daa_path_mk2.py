import tkinter as tk
from tkinter import messagebox
import heapq
import time
import networkx as nx
import matplotlib.pyplot as plt

# ---------------- Algorithms ---------------- #

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]

    while pq:
        current_distance, current_node = heapq.heappop(pq)
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    return distances


def bellman_ford(graph, vertices, start):
    distance = {node: float('inf') for node in graph}
    distance[start] = 0

    for _ in range(vertices - 1):
        for u in graph:
            for v, w in graph[u]:
                if distance[u] + w < distance[v]:
                    distance[v] = distance[u] + w

    for u in graph:
        for v, w in graph[u]:
            if distance[u] + w < distance[v]:
                messagebox.showerror("Error", "Graph contains a negative weight cycle!")
                return None
    return distance


# ---------------- GUI ---------------- #

class GraphGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Shortest Path Visualizer")
        self.root.geometry("720x580")
        self.root.configure(bg="#0b132b")

        self.graph = {}

        # ---- Title ---- #
        tk.Label(root, text="Shortest Path Visualizer", font=("Poppins", 22, "bold"),
                 fg="#6fffe9", bg="#0b132b").pack(pady=15)

        subtitle = tk.Label(root, text="Visualize Dijkstra & Bellman-Ford Algorithms",
                            font=("Poppins", 11), fg="#c0c0c0", bg="#0b132b")
        subtitle.pack(pady=(0, 20))

        # ---- Input Frame ---- #
        input_frame = tk.Frame(root, bg="#1c2541", bd=2, relief="groove")
        input_frame.pack(pady=10, padx=20)

        labels = ["From:", "To:", "Weight:"]
        entries = []
        for i, text in enumerate(labels):
            tk.Label(input_frame, text=text, font=("Poppins", 11), fg="white", bg="#1c2541").grid(row=0, column=i * 2, padx=5, pady=10)
            entry = tk.Entry(input_frame, width=6, font=("Poppins", 11), bg="#3a506b", fg="white", bd=0, justify="center")
            entry.grid(row=0, column=i * 2 + 1, padx=5)
            entries.append(entry)

        self.entry_from, self.entry_to, self.entry_weight = entries

        self.create_button(input_frame, "Add Edge", "#06d6a0", self.add_edge, 6, 0, 20)

        # ---- Start Node ---- #
        tk.Label(root, text="Start Vertex:", font=("Poppins", 12), fg="#ffffff", bg="#0b132b").pack(pady=(15, 2))
        self.entry_start = tk.Entry(root, width=8, font=("Poppins", 12), bg="#3a506b", fg="white", bd=0, justify="center")
        self.entry_start.pack()

        # ---- Buttons ---- #
        button_frame = tk.Frame(root, bg="#0b132b")
        button_frame.pack(pady=15)

        self.create_button(button_frame, "Run Dijkstra", "#48cae4", self.run_dijkstra, 0, 0)
        self.create_button(button_frame, "Run Bellman-Ford", "#ffd166", self.run_bellman, 0, 1)
        self.create_button(button_frame, "Show Graph", "#ef476f", self.show_graph, 0, 2)

        # ---- Output ---- #
        self.output_text = tk.Text(root, height=10, width=75, wrap="word",
                                   font=("Consolas", 11), bg="#1c2541", fg="#ffffff",
                                   bd=0, relief="flat", padx=10, pady=10)
        self.output_text.pack(pady=20)

        # Add scrollbar
        scroll = tk.Scrollbar(self.output_text, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    # ---- Helper for Buttons ---- #
    def create_button(self, frame, text, color, command, row, col, padx=8):
        btn = tk.Button(frame, text=text, command=command, font=("Poppins", 11, "bold"),
                        bg=color, fg="black", activebackground=color,
                        activeforeground="black", relief="flat", width=15, bd=0)
        btn.grid(row=row, column=col, padx=padx, pady=10)
        # Hover effect
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg="white"))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

    # ---- Functionalities ---- #
    def add_edge(self):
        u = self.entry_from.get().upper()
        v = self.entry_to.get().upper()
        try:
            w = int(self.entry_weight.get())
        except:
            messagebox.showerror("Invalid Input", "Weight must be an integer!")
            return

        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []

        self.graph[u].append((v, w))
        self.output_text.insert(tk.END, f"✅ Added Edge: {u} → {v} (Weight {w})\n")
        self.entry_from.delete(0, tk.END)
        self.entry_to.delete(0, tk.END)
        self.entry_weight.delete(0, tk.END)

    def run_dijkstra(self):
        start = self.entry_start.get().upper()
        if start not in self.graph:
            messagebox.showerror("Error", "Start vertex not found in graph!")
            return
        start_time = time.time()
        result = dijkstra(self.graph, start)
        end_time = time.time()
        self.output_text.insert(tk.END, f"\n💠 Dijkstra Result from {start}: {result}\n")
        self.output_text.insert(tk.END, f"⏱ Execution Time: {end_time - start_time:.6f} sec\n")

    def run_bellman(self):
        start = self.entry_start.get().upper()
        if start not in self.graph:
            messagebox.showerror("Error", "Start vertex not found in graph!")
            return
        start_time = time.time()
        result = bellman_ford(self.graph, len(self.graph), start)
        end_time = time.time()
        if result is not None:
            self.output_text.insert(tk.END, f"\n🔶 Bellman-Ford Result from {start}: {result}\n")
            self.output_text.insert(tk.END, f"⏱ Execution Time: {end_time - start_time:.6f} sec\n")

    def show_graph(self):
        if not self.graph:
            messagebox.showerror("Error", "No graph data available!")
            return
        G = nx.DiGraph()
        for u in self.graph:
            for v, w in self.graph[u]:
                G.add_edge(u, v, weight=w)

        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(8, 5))
        nx.draw(G, pos, with_labels=True, node_color="#48cae4", node_size=2500,
                font_size=12, font_weight="bold", edgecolors="#03045e", arrows=True)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
        plt.title("Graph Visualization", fontsize=14, fontweight="bold")
        plt.show()


# ---------------- Run the App ---------------- #
root = tk.Tk()
app = GraphGUI(root)
root.mainloop()
