import logging


def log_directory_tree(start_path):
    def _generate_tree(path, prefix=""):
        contents = list(path.iterdir())
        pointers = ["├──", "└──"]

        for i, item in enumerate(contents):
            if len(contents) > 1 and i != len(contents) - 1:
                yield prefix + pointers[0] + item.name
                extension = "│   "
            else:
                yield prefix + pointers[1] + item.name
                extension = "    "

            if item.is_dir():
                yield from _generate_tree(item, prefix=prefix + extension)

    tree_structure = "\n".join(_generate_tree(start_path))
    logging.info(f"Directory tree for {start_path}:\n{tree_structure}")
