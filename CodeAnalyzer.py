import ast
import graphviz
import os
import datetime

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, code):
        self.ast = ast.parse(code)
        self.folder_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(self.folder_name, exist_ok=True)
        self.graph_counter = 0
        # Prepare a single execution environment
        self.exec_env = {}
        exec(code, self.exec_env)  # Preload defined functions and classes into the environment

    def visit_For(self, node):
        # Extract the range and initialize the loop variable
        iter_range = eval(ast.unparse(node.iter), self.exec_env)
        loop_var = node.target.id  # the loop variable, e.g., 'i'
        loop_body = ast.unparse(node.body)

        # Manually execute each iteration of the loop
        for value in iter_range:
            self.exec_env[loop_var] = value  # Set loop variable for this iteration
            exec(loop_body, self.exec_env)  # Execute the loop body using the updated environment

            # After executing, visualize the current state of variables
            self.visualize()

        self.generic_visit(node)

    def visualize(self):
        dot = graphviz.Digraph(comment='Variables at each loop turn')
        dot.attr('node', shape='box')  # Set nodes to be box-shaped

        # Create a node for each variable in the environment (excluding built-ins and __name__)
        for var, value in self.exec_env.items():
            if var not in ["__builtins__", "__name__"]:
                current_var = f'{var}_{self.graph_counter}'
                prev_var = f'{var}_{self.graph_counter - 1}'
                dot.node(current_var, f'{var} = {value}')
                if self.graph_counter > 0:
                    dot.edge(prev_var, current_var)

        filename = os.path.join(self.folder_name, f'graph_{self.graph_counter}')
        dot.render(filename, format='png')
        self.graph_counter += 1

    def analyze(self):
        self.visit(self.ast)

# Example Python code to analyze
code = """
def compute(x, y):
    result = x + y
    return result

x=0
for i in range(5):
    compute(i, i+1)
    x+=i
"""

analyzer = CodeAnalyzer(code)
analyzer.analyze()
