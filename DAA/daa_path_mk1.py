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

    # Relax edges |V|-1 times
    for _ in range(vertices - 1):
        for u in graph:
            for v, w in graph[u]:
                if distance[u] + w < distance[v]:
                    distance[v] = distance[u] + w

    # Check for negative cycles
    for u in graph:
        for v, w in graph[u]:
            if distance[u] + w < distance[v]:
                messagebox.showerror("Error", "Graph contains a negative weight cycle!")
                return None

    return distance


# ---------------- GUI Code ---------------- #

class GraphGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Shortest Path Visualizer - Dijkstra & Bellman-Ford")
        self.root.geometry("650x500")
        self.graph = {}

        # Title Label
        tk.Label(root, text="Shortest Path Finder", font=("Arial", 18, "bold"), fg="darkblue").pack(pady=10)

        # Frame for Inputs
        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Label(frame, text="From:").grid(row=0, column=0)
        self.entry_from = tk.Entry(frame, width=5)
        self.entry_from.grid(row=0, column=1)

        tk.Label(frame, text="To:").grid(row=0, column=2)
        self.entry_to = tk.Entry(frame, width=5)
        self.entry_to.grid(row=0, column=3)

        tk.Label(frame, text="Weight:").grid(row=0, column=4)
        self.entry_weight = tk.Entry(frame, width=5)
        self.entry_weight.grid(row=0, column=5)

        tk.Button(frame, text="Add Edge", command=self.add_edge, bg="lightgreen").grid(row=0, column=6, padx=10)

        # Start Node
        tk.Label(root, text="Start Vertex:").pack()
        self.entry_start = tk.Entry(root, width=10)
        self.entry_start.pack()

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Run Dijkstra", command=self.run_dijkstra, bg="lightblue", width=15).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Run Bellman-Ford", command=self.run_bellman, bg="lightyellow", width=15).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Show Graph", command=self.show_graph, bg="lightpink", width=15).grid(row=0, column=2, padx=5)

        # Output Box
        self.output_text = tk.Text(root, height=10, width=70, wrap="word")
        self.output_text.pack(pady=10)

    # Add Edge Function
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
        self.output_text.insert(tk.END, f"Added Edge: {u} -> {v} (Weight {w})\n")
        self.entry_from.delete(0, tk.END)
        self.entry_to.delete(0, tk.END)
        self.entry_weight.delete(0, tk.END)

    # Run Dijkstra
    def run_dijkstra(self):
        start = self.entry_start.get().upper()
        if start not in self.graph:
            messagebox.showerror("Error", "Start vertex not found in graph!")
            return
        start_time = time.time()
        result = dijkstra(self.graph, start)
        end_time = time.time()
        self.output_text.insert(tk.END, f"\nDijkstra Result from {start}: {result}\n")
        self.output_text.insert(tk.END, f"Execution Time: {end_time - start_time:.6f} seconds\n")

    # Run Bellman-Ford
    def run_bellman(self):
        start = self.entry_start.get().upper()
        if start not in self.graph:
            messagebox.showerror("Error", "Start vertex not found in graph!")
            return
        start_time = time.time()
        result = bellman_ford(self.graph, len(self.graph), start)
        end_time = time.time()
        if result is not None:
            self.output_text.insert(tk.END, f"\nBellman-Ford Result from {start}: {result}\n")
            self.output_text.insert(tk.END, f"Execution Time: {end_time - start_time:.6f} seconds\n")

    # Show Graph
    def show_graph(self):
        if not self.graph:
            messagebox.showerror("Error", "No graph data available!")
            return
        G = nx.DiGraph()
        for u in self.graph:
            for v, w in self.graph[u]:
                G.add_edge(u, v, weight=w)

        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2500, font_size=12, arrows=True)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.title("Graph Visualization")
        plt.show()


# Run the App
root = tk.Tk()
app = GraphGUI(root)
root.mainloop()
