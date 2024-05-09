import ast
import astor
import graphviz
import os
import datetime

class CodeVisualizer(ast.NodeTransformer):
    def __init__(self):
        base_directory = "graphs"
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
        self.folder_name = os.path.join(base_directory, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.folder_name, exist_ok=True)
        self.graph_counter = 0

    