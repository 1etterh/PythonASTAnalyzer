import ast
import astor
import os
import graphviz
from datetime import datetime

class ValueTracker(ast.NodeTransformer):
    def __init__(self, code):
        self.ast = ast.parse(code)
        self.folder_name = self.create_graph_folder()
        
    def create_graph_folder(self):
        base_dir = "graphs"
        folder_name = os.path.join(base_dir, datetime.now().strftime("%Y%m%d_%H%M%S"))
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        return folder_name
    
    def visit_For(self, node):
        self.generic_visit(node)  # Visit the loop body
        
        loop_var = node.target.id if isinstance(node.target, ast.Name) else None
        if loop_var:
            # Prepare Graphviz visualization
            init_graph = ast.parse(f"self.init_graph('{loop_var}')").body[0]
            node.body.insert(0, init_graph)
        
        # Inject code to update the graph at the end of each iteration
        update_graph = ast.parse("self.update_graph()").body[0]
        node.body.append(update_graph)
        
        return node

    def init_graph(self, loop_var):
        self.dot = graphviz.Digraph('G', format='png', directory=self.folder_name)
        self.dot.node(loop_var, label=f"{loop_var} starts at 0")

    def update_graph(self):
        # This method needs to be adapted to work with dynamic variable values
        pass

    def save_graph(self, loop_counter):
        filename = f"loop_{loop_counter}"
        self.dot.render(filename=filename, cleanup=True)

    def instrument_and_run(self, code_globals, code_locals):
        code_globals['self'] = self  # Include 'self' in the globals dict
        instrumented_ast = self.visit(self.ast)
        exec(compile(instrumented_ast, filename="<ast>", mode="exec"), code_globals, code_locals)
    
    def analyze(self, code_globals, code_locals):
        self.instrument_and_run(code_globals, code_locals)

# Sample code for analysis
code = '''
x = 0
for i in range(5):
    x += i
print(x)
'''

tracker = ValueTracker(code)
globals_dict = {}
locals_dict = {}
tracker.analyze(globals_dict, locals_dict)
