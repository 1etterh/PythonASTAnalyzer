import ast
import graphviz

class ASTVisualizer(ast.NodeVisitor):
    def __init__(self):
        self.dot = graphviz.Digraph(comment='AST', format='png')
        self.node_count = 0  # To keep track of the order of nodes

    def add_node(self, node, label):
        # Enhance the label with the node order number
        extended_label = f'{self.node_count}: {label}'
        # Add additional information depending on the node type
        if hasattr(node, 'id'):
            extended_label += f'\\n(id: {node.id})'
        if hasattr(node, 'name'):
            extended_label += f'\\n(name: {node.name})'
        if hasattr(node, 'attr'):
            extended_label += f'\\n(attr: {node.attr})'
        if hasattr(node, 'arg'):
            extended_label += f'\\n(arg: {node.arg})'
        if hasattr(node, 'value'):
            # Safely try to add the value by unparsing, if possible
            try:
                value = ast.unparse(node.value)
                extended_label += f'\\n(value: {value})'
            except Exception:
                # If unparsing fails, ignore or handle exceptions
                pass

        node_id = f'node{self.node_count}'
        self.dot.node(node_id, label=extended_label, shape="box")
        self.node_count += 1
        return node_id

    def generic_visit(self, node):
        label = type(node).__name__
        node_id = self.add_node(node, label)

        for field, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                child_id = self.visit(value)
                self.dot.edge(node_id, child_id, label=field)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        child_id = self.visit(item)
                        self.dot.edge(node_id, child_id, label=f"{field}[]")
        return node_id

    def visualize(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        # Save the graph to a file and open it
        self.dot.render('ast-graph', view=True)

# Example Python code to visualize
code = """
def compute(x, y):
    result = x + y
    return result

class Example:
    def method(self):
        pass
x=0
for i in range(5):
    compute(i, i+1)
    x+=i
"""

# Create an instance of the visualizer and run it
visualizer = ASTVisualizer()
visualizer.visualize(code)
