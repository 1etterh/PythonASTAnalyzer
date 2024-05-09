import ast
import astor
import graphviz
from datetime import datetime
import os
from collections import defaultdict

class CodeAnalyzer(ast.NodeTransformer):
    def __init__(self, code):
        self.ast = ast.parse(code)
        self.graph_counter = 0
        self.variables = defaultdict(list)
        self.dot = None  # Graph will be initialized later
        self.base_dir = "graphs"

        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.folder_name = os.path.join(self.base_dir, datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.folder_name, exist_ok=True)

    def init_graph(self):
        self.dot = graphviz.Digraph(f'Graph_{self.graph_counter}', format='png')
        for var, values in self.variables.items():
            self.dot.node(var, f'{var}={values[-1]}' if values else var)  # Display the latest value

    def update_graph(self, var_name, value):
        # Update variable's list and reinitialize graph to reflect the change
        self.variables[var_name].append(value)
        self.init_graph()
        self.dot.render(os.path.join(self.folder_name, f'graph_{self.graph_counter}'))
        self.graph_counter += 1

    def visit_Assign(self, node):
        self.generic_visit(node)
        for target in node.targets:
            if isinstance(target, ast.Name):
                value = astor.to_source(node.value).strip()
                self.update_graph(target.id, value)
        return node

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        if isinstance(node.target, ast.Name):
            operation = self.operator_to_string(node.op)
            value = f'{node.target.id} {operation} {astor.to_source(node.value).strip()}'
            self.update_graph(node.target.id, value)
        return node

    def operator_to_string(self, operator):
        operators = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.Mod: '%'
        }
        return operators.get(type(operator), '?')

    def analyze(self):
        self.init_graph()  # Initialize the graph with initial state of variables
        self.visit(self.ast)
        exec(astor.to_source(self.ast))

# Sample code for analysis
code = '''
def compute(x, y):
    result = x + y
    return result

x = 0
for i in range(5):
    compute(i, i + 1)
    x += i
'''
analyzer = CodeAnalyzer(code)
analyzer.analyze()
