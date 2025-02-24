import math
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
import plotly.graph_objects as go
import numpy as np
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for session management

# Store graphs using a dictionary (Graph ID -> Equations List)
graph_store = {}

# Map simplified functions to math module functions
math_functions = {
    'sin': 'math.sin',
    'cos': 'math.cos',
    'tan': 'math.tan',
    'log': 'math.log',
    'sqrt': 'math.sqrt',
    'exp': 'math.exp',
    'abs': 'abs',  # No need to map, Python already has abs()
}

def generate_plot(equations):
    """Generate a Plotly graph for the given equations."""
    x_vals = np.linspace(-10, 10, 400)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink']
    traces = []

    for i, expression in enumerate(equations):
        # Replace simplified function names with math module equivalents
        for func, replacement in math_functions.items():
            expression = re.sub(rf'\b{func}\b', replacement, expression)

        y_vals = []
        try:
            y_vals = [eval(expression.replace('x', f'({x})')) for x in x_vals]
        except Exception as e:
            return f"Error in expression: {e}"

        traces.append(go.Scatter(x=x_vals, y=y_vals, mode="lines", name=expression, line=dict(color=colors[i % len(colors)])))

    fig = go.Figure(data=traces)
    fig.update_layout(title="Multiple Equations",
                      xaxis_title="x", yaxis_title="y",
                      legend_title="Equations")

    return fig.to_html(full_html=False)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            expression = request.form["expression"]
            graph_id = session.get("graph_id")

            # If no graph ID exists, generate a new one
            if not graph_id:
                graph_id = str(uuid.uuid4())  # Generate unique ID
                session["graph_id"] = graph_id  # Save in session
                graph_store[graph_id] = []  # Initialize graph storage

            graph_store[graph_id].append(expression)  # Store equation

            return redirect(url_for("graph", graph_id=graph_id))

        elif action == "new":
            session.pop("graph_id", None)  # Clear session graph ID
            return redirect(url_for("index"))

    return render_template("index.html", graph_html="", graph_id=None, equations=[])

@app.route("/graph/<graph_id>", methods=["GET", "POST"])
def graph(graph_id):
    equations = graph_store.get(graph_id, [])

    if request.method == "POST":
        action = request.form.get("action")

        if action == "remove":
            equation_index = int(request.form["equation_index"])
            equations.pop(equation_index)
            graph_store[graph_id] = equations  # Update stored equations

        return redirect(url_for("graph", graph_id=graph_id))

    graph_html = generate_plot(equations) if equations else ""

    return render_template("index.html", graph_html=graph_html, graph_id=graph_id, equations=equations)

if __name__ == "__main__":
    app.run(debug=True)
