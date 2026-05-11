"""
Script: Graph Theory with NetworkX
What it does: Creates and analyzes graphs (networks of nodes and edges).
Graphs model relationships: social networks, road maps, web links, flight routes.

Install: pip install networkx matplotlib
"""

try:
    import networkx as nx
    import matplotlib.pyplot as plt

    # --- Create a graph ---
    print("=== Creating a Graph ===")
    G = nx.Graph()  # undirected graph (edges have no direction)

    # Add nodes (cities)
    cities = ["London", "Paris", "Berlin", "Amsterdam", "Madrid", "Rome"]
    G.add_nodes_from(cities)

    # Add edges (connections/routes)
    routes = [
        ("London", "Paris", 343),       # weight = distance in km
        ("London", "Amsterdam", 357),
        ("Paris", "Berlin", 1054),
        ("Paris", "Madrid", 1273),
        ("Paris", "Rome", 1421),
        ("Berlin", "Amsterdam", 648),
        ("Amsterdam", "Berlin", 648),
        ("Madrid", "Rome", 1933),
    ]

    for city1, city2, distance in routes:
        G.add_edge(city1, city2, weight=distance)

    # --- Basic graph info ---
    print(f"Nodes: {list(G.nodes())}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Is connected: {nx.is_connected(G)}")  # can reach all nodes?

    # --- Shortest path ---
    print("\n=== Shortest Paths ===")
    start, end = "London", "Rome"

    # Unweighted shortest path (fewest hops)
    shortest = nx.shortest_path(G, start, end)
    print(f"Shortest route (hops): {' → '.join(shortest)}")
    print(f"Number of stops: {len(shortest) - 1}")

    # Weighted shortest path (by distance)
    shortest_weighted = nx.shortest_path(G, start, end, weight="weight")
    distance = nx.shortest_path_length(G, start, end, weight="weight")
    print(f"\nShortest route (distance): {' → '.join(shortest_weighted)}")
    print(f"Total distance: {distance} km")

    # --- Node centrality (who is most connected?) ---
    print("\n=== City Centrality (importance) ===")
    centrality = nx.degree_centrality(G)
    for city, score in sorted(centrality.items(), key=lambda x: -x[1]):
        connections = G.degree(city)
        bar = "●" * connections
        print(f"  {city:<12} connections: {connections}  {bar}")

    # --- Visualize ---
    plt.figure(figsize=(10, 7))
    pos = nx.spring_layout(G, seed=42)  # calculate node positions

    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="steelblue", alpha=0.8)
    nx.draw_networkx_labels(G, pos, font_size=10, font_color="white", font_weight="bold")
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.6)

    # Add edge labels (distances)
    edge_labels = {(u, v): f"{d['weight']}km" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)

    plt.title("European City Route Network")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("graph_network.png")
    plt.close()
    print("\nNetwork visualization saved: graph_network.png")

    import os
    os.remove("graph_network.png")

except ImportError:
    print("Install: pip install networkx matplotlib")

    # Show graph concept with pure Python
    print("\nGraph as adjacency dictionary:")
    graph = {
        "London": ["Paris", "Amsterdam"],
        "Paris":  ["London", "Berlin", "Madrid", "Rome"],
        "Berlin": ["Paris", "Amsterdam"],
    }
    for node, neighbors in graph.items():
        print(f"  {node}: {neighbors}")
