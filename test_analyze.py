import ast
import astor
import graphviz
from collections import defaultdict
from datetime import datetime

class PythonASTAnalyzer(ast.NodeVisitor):
    def __init__(self, code):
        self.ast = ast.parse(code)
        self.graph = graphviz.Digraph('AST', filename='ast.gv', format='png', node_attr={'shape': 'box'})
        self.node_count = 0
        self.node_map = {}  # Map AST node to Graphviz node name

    def visit(self, node):
        """Visit a node and set parent for all children."""
        if not hasattr(node, 'parent'):
            # If there's no parent set, assume this node is the root
            node.parent = None
        
        for child in ast.iter_child_nodes(node):
            child.parent = node
            self.visit(child)

        node_name = f'node{self.node_count}'
        label = self.get_label(node)
        self.graph.node(node_name, label)
        
        if node.parent and hasattr(node.parent, 'graph_name'):
            self.graph.edge(node.parent.graph_name, node_name)
        
        node.graph_name = node_name
        self.node_count += 1

    def get_label(self, node):
        """Generate label based on node type and content."""
        label = f"{type(node).__name__}"
        if hasattr(node, 'name'):
            label += f": {node.name}"
        elif hasattr(node, 'id'):
            label += f": {node.id}"
        elif hasattr(node, 'value'):
            label += f": {astor.to_source(node).strip()}"
        return label

    def analyze(self):
        """Run analysis and render graph."""
        self.visit(self.ast)
        self.graph.render()

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
