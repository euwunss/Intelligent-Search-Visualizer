import os
import json
from flask import Flask, render_template, jsonify, request

from uninformed import bfs, dfs, ucs, ids
from informed import greedy_best_first, a_star

app = Flask(__name__)

MAP_DATA_FILE = "map_data.json"


def load_map_data():
    """Load graph and location data from map_data.json if available."""
    if os.path.exists(MAP_DATA_FILE):
        try:
            with open(MAP_DATA_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {MAP_DATA_FILE}: {e}")
    return {
        "region": "State / Metro Area",
        "total_cities": 0,
        "total_edges": 0,
        "locations": {},
        "graph": {}
    }


@app.route("/")
def index():
    """Renders the main deployment webpage."""
    return render_template("index.html")


@app.route("/api/map", methods=["GET"])
def get_map():
    """Returns map locations and graph connections."""
    data = load_map_data()
    return jsonify(data)


@app.route("/api/search", methods=["POST"])
def search():
    """
    Search endpoint placeholder for deployment testing.
    """
    payload = request.get_json() or {}
    start = payload.get("start", "")
    goal = payload.get("goal", "")
    algorithm = payload.get("algorithm", "")

    data = load_map_data()

    # Convert map_data.json graph into the format used by the algorithms
    connections = {}

    for city, neighbors in data.get("graph", {}).items():
        connections[city] = [
            {
                "node": neighbor,
                "distance": distance
            }
            for neighbor, distance in neighbors.items()
        ]

    graph = {
        "nodes": data.get("locations", {}),
        "connections": connections
    }

    if algorithm == "bfs":
        result = bfs(graph, start, goal)

    elif algorithm == "dfs":
        result = dfs(graph, start, goal)

    elif algorithm == "ucs":
        result = ucs(graph, start, goal)

    elif algorithm == "ids":
        result = ids(graph, start, goal)

    elif algorithm == "greedy":
        result = greedy_best_first(graph, start, goal)

    elif algorithm == "astar":
        result = a_star(graph, start, goal)

    else:
        return jsonify({
            "status": "error",
            "message": "Invalid algorithm.",
            "path": [],
            "cost": 0,
            "nodes_expanded": 0
        })

    return jsonify({
        "status": "ready",
        "message": f"Deployment server active. Request received for algorithm '{algorithm}' from '{start}' to '{goal}'.",
        "path": result["path"] or [],
        "cost": result["distance"],
        "nodes_expanded": len(result["expanded"])
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)