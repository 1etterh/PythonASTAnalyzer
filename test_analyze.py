import ast
import astor
import graphviz
from collections import defaultdict
from datetime import datetime

class PythonASTAnalyzer(ast.NodeVisitor):
    def __init__(self, code):
        self.ast = ast.parse(code)
        self.variables = defaultdict(lambda: None)
        self.loop_variables = defaultdict(lambda: None)
        self.functions = {}
        self.classes = {}
        self.dot = graphviz.Digraph(comment="AST", format='png')
        self.node_count = 0

    def add_node(self, node, label):
        node_id = f'node{self.node_count}'
        self.dot.node(node_id, label=f"{self.node_count}: {label}")
        self.node_count += 1
        return node_id

    def generic_visit(self, node):
        label = type(node).__name__
        node_id = self.add_node(node, label)

        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        child_id = self.visit(item)
                        self.dot.edge(node_id, child_id, label=f"{field}[]")
            elif isinstance(value, ast.AST):
                child_id = self.visit(value)
                self.dot.edge(node_id, child_id, label=field)

        return node_id

    def visit_Assign(self, node):
        node_id = self.generic_visit(node)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables[target.id]
        return node_id
    
    def visit_For(self, node):
        node_id = self.generic_visit(node)
        loop_var = astor.to_source(node.target).strip()
        self.loop_variables[loop_var]
        return node_id

    def visit_FunctionDef(self, node):
        node_id = self.generic_visit(node)
        function_code = astor.to_source(node)
        self.functions[node.name] = function_code.strip()
        return node_id

    def visit_ClassDef(self, node):
        node_id = self.generic_visit(node)
        class_code = astor.to_source(node)
        self.classes[node.name] = class_code.strip()
        return node_id

    def analyze(self):
        self.visit(self.ast)

    def visualize(self):
        # Save the graph to a file and open it
        self.dot.render('ast-graph', view=True)

# Sample code for analysis
code = '''
class Math:
    def add(self, x, y):
        return x + y

def compute(x, y):
    result = x + y
    return result

x = 0
for i in range(5):
    compute(i, i + 1)
    x += i
'''

analyzer = PythonASTAnalyzer(code)
analyzer.analyze()
analyzer.visualize()

print("Variables:", analyzer.variables)
print("Loop Variables:", analyzer.loop_variables)
print("Functions:", analyzer.functions)
print("Classes:", analyzer.classes)
