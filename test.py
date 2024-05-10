# import ast
# import astor
# import graphviz
# import os
# from datetime import datetime

# class ValueTracker(ast.NodeTransformer):
#     def __init__(self, code):
#         self.ast = ast.parse(code)
#         self.folder_name = "graphs/" + datetime.now().strftime("%Y%m%d_%H%M%S")

#     def visit_For(self, node):
#         self.generic_visit(node)  # Process the loop body first to capture internal changes

#         # Dynamically create a folder if it does not exist, executed before the loop
#         check_folder_stmt = ast.parse(f"import os\nif not os.path.exists('{self.folder_name}'): os.makedirs('{self.folder_name}')")
#         init_graph_stmt = ast.parse("import graphviz\ndot = graphviz.Digraph('G', format='png')")

#         # Prepare a new body for the loop with the folder check and graph initialization
#         new_body = [check_folder_stmt.body[0], check_folder_stmt.body[1], init_graph_stmt.body[0], init_graph_stmt.body[1]]
        
#         for stmt in node.body:
#             new_body.append(stmt)
#             if isinstance(stmt, (ast.Assign, ast.AugAssign)):
#                 for target in getattr(stmt, 'targets', [stmt.target]):
#                     if isinstance(target, ast.Name):
#                         value_src = astor.to_source(stmt.value).strip() if isinstance(stmt, ast.Assign) else f"{target.id} + {astor.to_source(stmt.value).strip()}"
#                         # Add graph update statement
#                         graph_stmt = ast.parse(f"dot.node('{target.id}', '{target.id} = {value_src}', shape='box')")
#                         new_body.append(graph_stmt.body[0])

#         # Render the graph at the end of the loop
#         render_stmt = ast.parse(f"dot.render(filename='{self.folder_name}/graph_{node.target.id}_' + str({node.target.id}) + '.png', view=False)")
#         new_body.append(render_stmt.body[0])

#         node.body = new_body
#         return node

#     def track_values(self):
#         self.visit(self.ast)

# # Example Python code to visualize
# code = """
# def compute(x, y):
#     result = x + y
#     return result

# x = 0
# for i in range(5):
#     compute(i, i+1)
#     x += i
# """

# # Create a visualizer and modify the AST
# visualizer = ValueTracker(code)
# visualizer.track_values()

# # Optionally execute the modified code
# exec_globals = {'graphviz': graphviz, 'os': os, 'datetime': datetime}
# exec(compile(astor.to_source(visualizer.ast), filename="<ast>", mode="exec"), exec_globals)

# # Display the modified source code
# print(astor.to_source(visualizer.ast))


import ast
import astor
import graphviz
import os
from datetime import datetime

class ValueTracker(ast.NodeTransformer):
    def __init__(self, code):
        self.ast = ast.parse(code)
        self.folder_name = "graphs/" + datetime.now().strftime("%Y%m%d_%H%M%S")

    def visit_For(self, node):
        self.generic_visit(node)  # Process the loop body first to capture internal changes

        # Initialize Graphviz graph at the start of the loop
        init_graph_stmt = ast.parse("import graphviz\ndot = graphviz.Digraph('G', format='png')").body
        folder_check_stmt = ast.parse(f"import os\nif not os.path.exists('{self.folder_name}'): os.makedirs('{self.folder_name}')").body

        new_body = folder_check_stmt + init_graph_stmt

        for stmt in node.body:
            self.generic_visit(stmt)  # Make sure any nested structures are processed
            new_body.append(stmt)
            if isinstance(stmt, (ast.Assign, ast.AugAssign)):
                for target in getattr(stmt, 'targets', [stmt.target]):
                    if isinstance(target, ast.Name):
                        update_graph_code = f"""
dot.node('{target.id}', '{target.id} = ' + str({target.id}), shape='box')
"""
                        update_graph_stmt = ast.parse(update_graph_code).body[0]
                        new_body.append(update_graph_stmt)

        # Append graph rendering statement at the end of the loop body
        render_stmt = ast.parse(f"dot.render(filename='{self.folder_name}/graph_' + str({node.target.id}) + '.png', view=False)").body[0]
        new_body.append(render_stmt)

        node.body = new_body
        return node

    def track_values(self):
        self.visit(self.ast)

# Example Python code to visualize
code = """
def compute(x, y):
    result = x + y
    return result

x = 0
for i in range(5):
    compute(i, i+1)
    x += i
"""

# Create a visualizer and modify the AST
visualizer = ValueTracker(code)
visualizer.track_values()

# Optionally execute the modified code
exec_globals = {'graphviz': graphviz, 'os': os, 'datetime': datetime}
exec(compile(astor.to_source(visualizer.ast), filename="<ast>", mode="exec"), exec_globals)

# Display the modified source code
print(astor.to_source(visualizer.ast))
