import logging
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from knowledge_graph import (
    generate_graph,
    visualize_knowledge_graph,
    visualize_knowledge_graph_interactive,
)
from models import KnowledgeGraph
from utils import log_directory_tree

logging.basicConfig(level=logging.INFO)


st.set_page_config(
    page_title="Pansophy",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Absolute paths
BASE_DIR = Path(__file__).resolve().parent
GRAPHS_DIR = BASE_DIR / "graphs"


def render_html(html_path: Path):
    with open(html_path, "r") as file:
        html_content = file.read()
    components.html(html_content, height=800, width=1200)


def get_file_paths(directory_path, topic):
    topic_filename = topic.replace(" ", "_").lower()
    return (
        directory_path / f"{topic_filename}.svg",
        directory_path / f"{topic_filename}.html",
    )


def delete_topic_graph(directory_path):
    import shutil

    shutil.rmtree(directory_path)


def render_topic_graph(directory_path, topic):
    svg_path, html_path = get_file_paths(directory_path, topic)

    if svg_path.exists():
        st.image(str(svg_path))
    else:
        st.error(f"File {svg_path} not found!")

    st.subheader("Interactive Knowledge Graph")
    render_html(str(html_path))


def main():
    # Debug: Recursively log directory structure in tree format
    log_directory_tree(GRAPHS_DIR)

    st.title("Pansophy 📚🧠💡")

    tab1, tab2 = st.tabs(["Create", "History"])

    existing_topics = [p.name for p in GRAPHS_DIR.iterdir() if p.is_dir()]

    with tab1:
        st.header("Generate Knowledge Graph 🌐")
        topic = st.text_input("enter a topic")

        if topic:
            directory_path = GRAPHS_DIR / topic.replace(" ", "_").lower()

            if directory_path.exists():
                st.write(f"Fetching pregenerated knowledge graph for {topic}...")
            else:
                with st.spinner(f"Generating knowledge graph for {topic}..."):
                    try:
                        graph: KnowledgeGraph = generate_graph(topic)
                        visualize_knowledge_graph(
                            graph, name=topic, directory=directory_path
                        )
                        visualize_knowledge_graph_interactive(
                            graph, name=topic, directory=directory_path
                        )
                        st.success("Knowledge graph generated!")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

            render_topic_graph(directory_path, topic)

            delete_button = st.button("🗑️ Delete this topic's graph")
            if delete_button:
                delete_topic_graph(directory_path)
                st.success(f"'{topic}' knowledge graph deleted!")

    with tab2:
        st.header("Explore Knowledge Graphs")
        selected_topic = st.selectbox("select a topic", existing_topics, index=0)

        submit = st.button("View")

        if submit:
            topic_directory = GRAPHS_DIR / selected_topic.replace(" ", "_").lower()
            render_topic_graph(topic_directory, selected_topic)


if __name__ == "__main__":
    main()
