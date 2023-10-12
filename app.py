from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from knowledge_graph import (
    generate_graph,
    visualize_knowledge_graph,
    visualize_knowledge_graph_interactive,
)
from models import KnowledgeGraph

st.set_page_config(
    page_title="Pansophy",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_html(html_path: Path):
    """Renders HTML file"""
    with open(html_path, "r") as file:
        html_content = file.read()
    components.html(html_content, height=800, width=1200)


def get_file_paths(directory_path, topic):
    """Get file paths for SVG and HTML based on topic"""
    topic_filename = topic.replace(" ", "_").lower()
    return (
        directory_path / f"{topic_filename}.svg.svg",
        directory_path / f"{topic_filename}.html",
    )


def delete_topic_graph(directory_path):
    """Delete the topic graph directory and its contents"""
    import shutil

    shutil.rmtree(directory_path)


def render_topic_graph(directory_path, topic):
    """Render the topic graph from given directory and topic"""
    svg_path, html_path = get_file_paths(directory_path, topic)

    st.image(str(svg_path))

    st.subheader("Interactive Knowledge Graph")
    render_html(str(html_path))


def main():
    st.image("img/logo.jpeg", use_column_width=True)

    st.markdown(
        """
    Welcome to Pansophy! 

    Pansophy is an innovative tool designed to help you visualize and understand any topic in depth. 
    By leveraging the power of AI, Pansophy constructs detailed [knowledge graphs](https://en.wikipedia.org/wiki/Knowledge_graph) for your chosen topic, 
    presenting both core concepts and intricate details in an interconnected manner. 
    
    Whether you're a student, researcher, or just curious, Pansophy aims to provide a comprehensive perspective on any subject 
    you're keen to explore.
    """
    )

    tab1, tab2 = st.tabs(["Create", "History"])

    existing_topics = [p.name for p in Path("graphs").iterdir() if p.is_dir()]

    with tab1:
        st.header("Generate Knowledge Graph 🌐")
        topic = st.text_input(label="Enter a topic", placeholder="love")

        if topic:
            directory_path = Path("graphs") / topic.replace(" ", "_").lower()

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
        selected_topic = st.selectbox("Select a topic", existing_topics, index=0)

        submit = st.button("View")

        if submit:
            topic_directory = Path("graphs") / selected_topic.replace(" ", "_").lower()
            render_topic_graph(topic_directory, selected_topic)


if __name__ == "__main__":
    main()
