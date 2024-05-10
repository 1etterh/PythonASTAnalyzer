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
            self.generic_visit(stmt)  # Ensure nested structures are processed
            new_body.append(stmt)
            if isinstance(stmt, ast.Assign) or isinstance(stmt, ast.AugAssign):
                # Properly handle targets for Assign and target for AugAssign
                targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        value_src = astor.to_source(stmt.value).strip()
                        update_graph_code = f"""
import pprint
value_repr = pprint.pformat({target.id}, width=1)
dot.node('{target.id}', '<{target.id} = ' + value_repr.replace('\\n', '<BR/>') + '>', shape='none')
"""
                        update_graph_stmt = ast.parse(update_graph_code).body
                        new_body.extend(update_graph_stmt)

        # Append graph rendering statement at the end of the loop body
        render_stmt = ast.parse(f"dot.render(filename='{self.folder_name}/graph_' + str({node.target.id}), view=False)").body[0]
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
    y = {'a': i+1, 'b': i+2}
    z = [[i+1, i+2], [i+3, i+4]]
"""

# Create a tracker and modify the AST
tracker = ValueTracker(code)
tracker.track_values()

# Optionally execute the modified code
exec_globals = {'graphviz': graphviz, 'os': os, 'datetime': datetime, 'pprint': __import__('pprint')}
exec(compile(astor.to_source(tracker.ast), filename="<ast>", mode="exec"), exec_globals)

# Display the modified source code
print(astor.to_source(tracker.ast))
f=open('output.txt','w')
f.write(astor.to_source(tracker.ast))
f.close()