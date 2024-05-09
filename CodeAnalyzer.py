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
        self.functions = {}
        self.classes = {}
        self.variables = defaultdict(list)
        self.dot = None  # Initialized in init_graph()
        self.base_dir = "graphs"

        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.folder_name = os.path.join(self.base_dir, datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.folder_name, exist_ok=True)

    def init_graph(self):
        # Initialize a new Graphviz graph
        self.dot = graphviz.Digraph(f'Graph_{self.graph_counter}', format='png')

    def create_graph(self):
        # Save the current graph to a file, ensuring each graph is unique
        filename = os.path.join(self.folder_name, f'graph_{self.graph_counter}')
        self.dot.render(filename=filename, view=False)
        self.graph_counter += 1  # Increment the counter to ensure the next graph has a unique name
        
        ##############Debug
        print("create_graph",self.graph_counter)

    def visit_For(self, node):
        self.generic_visit(node)  # Process the loop body first to capture internal changes
        loop_var = astor.to_source(node.target).strip()
        new_body = [ast.parse(f"print('Loop iteration with {loop_var} =', {loop_var})").body[0]]
        for stmt in node.body:
            new_body.append(stmt)
            if isinstance(stmt, (ast.Assign, ast.AugAssign)):
                for target in getattr(stmt, 'targets', [stmt.target]):
                    if isinstance(target, ast.Name):
                        value_src = astor.to_source(stmt.value).strip() if isinstance(stmt, ast.Assign) else f"{target.id} + {astor.to_source(stmt.value).strip()}"
                        print_stmt = ast.parse(f"print('During loop, {target.id} =', {value_src})").body[0]
                        new_body.append(print_stmt)
        node.body = new_body
        return node
    
    def operator_to_string(self, operator):
        operators = {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.Mod: '%'
        }
        return operators.get(type(operator), '?')

    def analyze(self):
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