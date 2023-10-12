import logging
import sys
import threading
import time
import webbrowser
from pathlib import Path

import instructor
import openai
import streamlit as st
from graphviz import Digraph
from pydantic import ValidationError
from pyvis.network import Network

from models import KnowledgeGraph

logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

if OPENAI_API_KEY is None:
    st.error("OPENAI API key Missing")
    st.stop()

openai.api_key = OPENAI_API_KEY


# Adds response_model to ChatCompletion
# Allows the return of Pydantic model rather than raw JSON
instructor.patch()


def loading_animation(stop_event):
    chars = "|/-\\"
    prefix = "Generating graph... "
    sys.stdout.write(prefix)
    sys.stdout.flush()
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write("\r" + prefix + chars[idx % len(chars)])
        sys.stdout.flush()
        time.sleep(0.1)
        idx += 1
    sys.stdout.write(
        "\r" + prefix + "Done!    "
    )  # extra spaces to ensure clearing any leftover chars
    sys.stdout.flush()


def generate_file_path(topic, directory, extension):
    filepath = directory / f"{topic.replace(' ', '_').lower()}.{extension}"
    return filepath


def create_prompt(input):
    return f"""
    Construct a detailed and expansive knowledge graph for the topic '{input}'. Begin by identifying the core concepts directly related to the topic. For each of these concepts, further branch out to nodes that provide specific details or sub-concepts. Continuously expand upon each node, ensuring every concept is further elaborated upon, until a comprehensive understanding of the topic is achieved.

    Key guidelines:
    - Avoid generic placeholders like "primary node" or "secondary node". Every node should represent a concrete concept or detail.
    - Describe the significance and relationship of each node to the overarching topic.
    - Define relationships with precision. For instance, specify if a node "is a type of", "results in", "is used for", "is an example of", etc.
    - Assign each node an 'id', 'label', and 'color' based on its importance or depth in the topic (e.g., fundamental concepts might be red, detailed explanations blue, and so on).
    - If there's ambiguity in any node's placement or relevance, provide a brief reasoning or source for clarity.

    Aim for a detailed, interconnected, and specific representation, ensuring that the essence of the topic is captured from all angles and depths.
    """  # noqa: E501


def generate_graph(input, max_retries=3) -> KnowledgeGraph:
    stop_event = threading.Event()
    t = threading.Thread(target=loading_animation, args=(stop_event,))
    t.start()

    for _ in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": create_prompt(input)}],
                response_model=KnowledgeGraph,
            )
            stop_event.set()
            return response
        except ValidationError:
            print(f"\nRetry attempt {_ + 1} failed. Trying again...")
            continue

    stop_event.set()
    raise Exception(f"Failed to generate graph after {max_retries} attempts.")


def visualize_knowledge_graph_interactive(kg, name, directory):
    filepath = generate_file_path(name, directory, "html")
    nt = Network(notebook=True, width="100%", height="800px", cdn_resources="in_line")

    for node in kg.nodes:
        nt.add_node(node.id, node.label, title=node.label, color=node.color)
    for edge in kg.edges:
        nt.add_edge(edge.source, edge.target, label=edge.label, color=edge.color)

    nt.save_graph(str(filepath))
    logging.info(f"Saved interactive graph to: {filepath}")
    return filepath


def visualize_knowledge_graph(kg, name, directory):
    filepath = generate_file_path(name, directory, "svg")
    dot = Digraph(comment=name, format="svg")

    # Graph aesthetics
    dot.attr(
        bgcolor="#F5F5F5",
        rankdir="TB",
        nodesep="0.5",
        ranksep="1",
        overlap="false",
        outputorder="edgesfirst",
        pad="0.5",
    )

    # Node aesthetics
    for node in kg.nodes:
        dot.node(
            str(node.id),
            node.label,
            shape="ellipse",
            fontsize="12",
            color=node.color,
            gradientangle="90",
        )

    # Edge aesthetics
    for edge in kg.edges:
        dot.edge(
            str(edge.source),
            str(edge.target),
            label=edge.label,
            color="#A9A9A9",
            arrowsize="0.5",
            penwidth="1.5",
        )

    dot.render(filename=str(filepath))
    logging.info(f"Saved graph to: {filepath}")
    return filepath


def user_interaction():
    topic = input("Enter the topic you want to learn about: ")
    directory_path = Path("graphs") / topic.replace(" ", "_").lower()

    svg_path = directory_path / f"{topic.replace(' ', '_').lower()}.svg.svg"
    html_path = directory_path / f"{topic.replace(' ', '_').lower()}.html"

    # If both files exist, no need to regenerate
    if not svg_path.exists() or not html_path.exists():
        graph: KnowledgeGraph = generate_graph(topic)

        visualize_knowledge_graph(graph, name=topic, directory=directory_path)
        visualize_knowledge_graph_interactive(
            graph, name=topic, directory=directory_path
        )

    choice = input("\nDo you want an interactive graph? (yes/no): ").strip().lower()
    if choice == "yes":
        webbrowser.open("file://" + str(html_path.absolute()))
    else:
        webbrowser.open("file://" + str(svg_path.absolute()))


if __name__ == "__main__":
    user_interaction()
