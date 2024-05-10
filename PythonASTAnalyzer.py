import ast
import astor
from collections import defaultdict
class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, code):
        self.ast = ast.parse(code)
        self.variables = defaultdict(lambda:None)
        self.functions = {}
        self.classes={}
        self.loop_variables = defaultdict(lambda:None)
        
    def visit_Assign(self,node):
        self.generic_visit(node)
        for target in node.targets:
            if isinstance(target,ast.Name):
                self.variables[target.id]
        return node
    
    def visit_For(self, node):
        self.generic_visit(node)
        loop_var = astor.to_source(node.target).strip()
        self.loop_variables[loop_var]
        
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        # Capture function definition in string format
        function_code = astor.to_source(node)
        self.functions[node.name] = function_code.strip()
        return node
    
    def visit_ClassDef(self, node):
        self.generic_visit(node)
        # Capture class definition in string format
        class_code = astor.to_source(node)
        self.classes[node.name] = class_code.strip()
        return node
    
    def analyze(self):
        self.visit(self.ast)


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

analyzer = CodeAnalyzer(code)
analyzer.analyze()
print("Variables:", *analyzer.variables)
print("Loop Variables:",analyzer.loop_variables)
print("Functions:",analyzer.functions)
print("Classes:",analyzer.classes)