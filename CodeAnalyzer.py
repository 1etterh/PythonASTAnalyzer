# import ast
# import astor
# import graphviz
# import os
# import datetime

# class CodeVisualizer(ast.NodeTransformer):
#     def __init__(self):
#         base_directory = "graphs"
#         if not os.path.exists(base_directory):
#             os.makedirs(base_directory)
#         self.folder_name = os.path.join(base_directory, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
#         os.makedirs(self.folder_name, exist_ok=True)
#         self.graph_counter = 0

    

import ast
import graphviz
import os
import datetime

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, code):
        self.ast = ast.parse(code)
        base_directory = "graphs"
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
        self.folder_name = os.path.join(base_directory, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.folder_name, exist_ok=True)
        self.graph_counter = 0
        self.global_env = {}  # Store the environment for the entire script
        exec(code, self.global_env)  # Load initial state from code, including function definitions.
        self.previous_states = {k: v for k, v in self.global_env.items() if k not in ["__builtins__", "__name__"]}

    def visit_For(self, node):
        iter_range = eval(ast.unparse(node.iter), self.global_env)
        loop_var = node.target.id
        loop_body = ast.unparse(node.body)

        for value in iter_range:
            self.global_env[loop_var] = value
            exec(loop_body, self.global_env)  # Execute using the global environment
            self.visualize_changes()

        self.generic_visit(node)

    def visualize_changes(self):
        dot = graphviz.Digraph(comment='Variables at each loop turn')
        dot.attr('node', shape='box')

        for var, value in self.global_env.items():
            if var not in ["__builtins__", "__name__"]:
                if var in self.previous_states and self.previous_states[var] != value:
                    # Only add nodes and edges for changed values
                    prev_val = self.previous_states[var]
                    current_val = value
                    dot.node(f'{var}_prev_{self.graph_counter}', f'{var} = {prev_val}')
                    dot.node(f'{var}_{self.graph_counter}', f'{var} = {current_val}')
                    dot.edge(f'{var}_prev_{self.graph_counter}', f'{var}_{self.graph_counter}')

                # Update the previous states for the next iteration
                self.previous_states[var] = value

        filename = os.path.join(self.folder_name, f'graph_{self.graph_counter}')
        dot.render(filename, format='png')
        self.graph_counter += 1

    def analyze(self):
        self.visit(self.ast)

code = """
def compute(x, y):
    return x + y

x = 0
for i in range(5):
    compute(i, i+1)
    x += i
"""

analyzer = CodeAnalyzer(code)
analyzer.analyze()
