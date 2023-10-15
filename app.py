import logging
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from knowledge_graph import (
    generate_graph,
    visualize_knowledge_graph,
    visualize_knowledge_graph_interactive,
    save_edge_nodes,
)
from models import KnowledgeGraph

logging.basicConfig(level=logging.INFO)


st.set_page_config(
    page_title="Pansophy",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
GRAPHS_DIR = BASE_DIR / "graphs"


def render_html(html_path: Path):
    with open(html_path, "r") as file:
        html_content = file.read()
    components.html(html_content, height=800, width=1200, scrolling=True)


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
        with open(svg_path, "rb") as file:
            st.download_button(
                label="Download knowledge graph",
                data=file,
                file_name=f"{topic}.svg",
                mime="image/svg+xml",
            )
    else:
        st.error(f"File {svg_path} not found!")

    st.divider()
    st.subheader("Interactive Knowledge Graph")
    render_html(str(html_path))


def deep_dive_options(directory_path, topic, div):
    header = st.empty()
    if not (directory_path / "edges.txt").exists():
        # backwards compatibility
        return

    with header.container():
        with open(directory_path / "edges.txt", "r") as f:
            edge_nodes = f.read().splitlines()

        st.subheader("Dive into a subtopic")
        options = edge_nodes
        options.insert(0, "None (Skip)")
        choice = st.selectbox(
            "Which concept would you like to dive deeper into?", options
        )

    if choice != "None (Skip)":
        deeper_topic = choice
        deeper_depth = "deep"
        deeper_directory_path = GRAPHS_DIR / deeper_topic.replace(" ", "_").lower()
        div.empty()
        show_graphs(deeper_directory_path, deeper_topic, header, deeper_depth)


def show_graphs(directory_path, topic, div, depth="overview"):
    div.empty()  # clear previous block
    if not directory_path.exists():
        with st.spinner(f"Generating knowledge graph for {topic}..."):
            try:
                graph: KnowledgeGraph = generate_graph(topic, depth)
                visualize_knowledge_graph(graph, name=topic, directory=directory_path)
                visualize_knowledge_graph_interactive(
                    graph, name=topic, directory=directory_path
                )
                save_edge_nodes(graph, directory_path)
                st.success("Knowledge graph generated!")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    with div.container():
        render_topic_graph(directory_path, topic)

    if st.button("Delete"):
        delete_topic_graph(directory_path)
        st.success(f"Deleted {topic}!")

    deep_dive_options(directory_path, topic, div)


def create_tab():
    st.header("Discover Knowledge Graph 🌐")

    header = st.empty()
    with header.container():
        topic = st.text_input("Enter a topic", placeholder="Meaning of life").strip()
        depth = st.radio("Detail Level:", ["Overview", "Deep"], index=0).lower()

        if not topic:
            return st.warning("Please enter a topic!")

    directory_path = GRAPHS_DIR / topic.replace(" ", "_").lower()
    show_graphs(directory_path, topic, header, depth)


def history_tab():
    st.header("Explore Knowledge Graphs")
    existing_topics = [p.name for p in GRAPHS_DIR.iterdir() if p.is_dir()]
    existing_topics = [t.replace("_", " ").title() for t in existing_topics]
    selected_topic = st.selectbox("Select a topic", existing_topics, index=0)
    topic_directory = GRAPHS_DIR / selected_topic.replace(" ", "_").lower()

    if st.button("View"):
        render_topic_graph(topic_directory, selected_topic)


def main():
    # Displaying the logo at the top of the page
    st.image("img/logo.jpeg", use_column_width=True)

    st.title("Welcome to **Pansophy**!")

    st.markdown(
        """
        [Pansophy](https://github.com/benthecoder/pansophy) 
        empowers you to visualize and delve deep into any topic. Leveraging the strength of LLMs, it crafts comprehensive [knowledge graphs](https://en.wikipedia.org/wiki/Knowledge_graph) to present both foundational concepts and intricate nuances in an interconnected web. 
        
        Built with ❤️ by [Benedict Neo](https://www.bneo.xyz/) and [Wei Chun](https://github.com/weichunnn)
        """
    )

    tab1, tab2 = st.tabs(["Create", "History"])

    with tab1:
        create_tab()

    with tab2:
        history_tab()


if __name__ == "__main__":
    main()
