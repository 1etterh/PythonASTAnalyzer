import ast
import astor
import graphviz
from datetime import datetime
import os
from collections import deque
class CodeAnalyzer(ast.NodeTransformer):
    def __init__(self, code):
        self.ast = ast.parse(code)
        self.variables = deque()
        base_dir = "graphs"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        self.folder_name = os.path.join(base_dir, datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.folder_name, exist_ok=True)

    def visit_Assign(self,node):
        self.generic_visit(node)
        for target in node.targets:
            if isinstance(target,ast.Name):
                self.variables.append(target.id)
        return node
    
    def visit_For(self, node):
        self.generic_visit(node)
        loop_var = astor.to_source(node.target).strip()
        self.variables.append(loop_var)
        # for stmt in node.body:
        #     if isinstance(stmt, (ast.Assign, ast.AugAssign)):
        #         targets = stmt.targets if isinstance(stmt, (ast.Assign)) else [stmt.target]
        #         for target in targets:
        #             if isinstance(target, ast.Name):
        #                 self.variables.append(target.id)
        # return node
    def analyze(self):
        self.visit(self.ast)

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
print(analyzer.variables)
