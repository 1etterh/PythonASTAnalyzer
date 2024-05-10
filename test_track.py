import ast
import astor
import graphviz
from datetime import datetime

class PythonASTAnalyzer(ast.NodeVisitor):
    def __init__(self, code):
        self.ast = ast.parse(code)
        self.dot = graphviz.Digraph(comment="AST", format='png')
        self.node_count = 0

    def add_node(self, node, label):
        node_id = f'node{self.node_count}'
        detailed_label = f"{self.node_count}: {label}"

        # Add extra details based on node type
        if hasattr(node, 'id'):
            detailed_label += f"\\nID: {node.id}"
        if hasattr(node, 'name'):
            detailed_label += f"\\nName: {node.name}"
        if hasattr(node, 'arg'):
            detailed_label += f"\\nArg: {node.arg}"
        if isinstance(node, ast.Constant):
            detailed_label += f"\\nValue: {node.value}"
        if isinstance(node, ast.Name):
            detailed_label += f"\\nVar: {node.id}"

        self.dot.node(node_id, detailed_label, shape="box")
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

    def analyze(self):
        self.visit(self.ast)
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
    if x > 5:
        break
'''

analyzer = PythonASTAnalyzer(code)
analyzer.analyze()
