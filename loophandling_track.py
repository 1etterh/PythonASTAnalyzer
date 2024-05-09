import ast
import astor
import graphviz
import os

class CodeVisualizer(ast.NodeTransformer):
    def __init__(self):
        self.graph_counter = 0
        self.folder_name = "graphs"
        os.makedirs(self.folder_name, exist_ok=True)
        
    def visit_FunctionDef(self, node):
        # No graph creation for function definitions, just traverse
        self.generic_visit(node)
        return node

    def visit_Assign(self, node):
        # Visualize variable assignments
        self.generic_visit(node)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.create_graph(target.id, astor.to_source(node.value).strip())
        return node
   
    def visit_ClassDef(self, node):
        # No graph creation for class definitions, just traverse
        self.generic_visit(node)
        return node

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


    def create_graph(self, variable_id, expression):
        dot = graphviz.Digraph('G', filename=f'{self.folder_name}/graph_{self.graph_counter}.gv', format='png')
        dot.node(variable_id, f'{variable_id} = {expression}')
        dot.render(view=False)
        self.graph_counter += 1

# Example Python code to visualize
code = """
def compute(x, y):
    result = x + y
    return result

class Example:
    def method(self):
        pass

x = 0
for i in range(5):
    compute(i, i+1)
    x += i
"""

# Parse the code to an AST
parsed_code = ast.parse(code)

# Create a visualizer and modify the AST
visualizer = CodeVisualizer()
visualizer.visit(parsed_code)

# Execute the original code for comparison or further use
exec(astor.to_source(parsed_code))
