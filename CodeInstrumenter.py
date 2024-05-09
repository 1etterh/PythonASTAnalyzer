import ast
import astor

class CodeInstrumentor(ast.NodeTransformer): #extend ast.NodeTransformer
    def visit_FunctionDef(self, node):
        # Instrument function entry
        print_stmt = ast.parse(f"print('Function: {node.name}, Line number: {node.lineno}')").body
        node.body = print_stmt + node.body
        self.generic_visit(node)
        return node

    def visit_Assign(self, node):
        # Instrument variable assignments
        self.generic_visit(node)  # Visit all other child nodes first
        print_statements = []
        
        for target in node.targets:
            print("target Id = ",target.id)
            print_stmt = ast.parse(f"print('Variable: {target.id} updated to =', {astor.to_source(node.value).strip()})").body
            print_statements.extend(print_stmt)
        return [node] + print_statements

    def visit_ClassDef(self, node):
        # Instrument class definitions
        print_stmt = ast.parse(f"print('Class: {node.name}, Line number: {node.lineno}')").body
        node.body = print_stmt + node.body
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


    def visit_While(self, node):
        # Instrument While loops similarly
        self.generic_visit(node)
        print_stmt = ast.parse("print('While loop iteration')").body
        new_body = [print_stmt[0]]
        for stmt in node.body:
            new_body.append(stmt)
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        print_stmt = ast.parse(f"print('During loop, {target.id} =', {target.id})").body[0]
                        new_body.append(print_stmt)
        node.body = new_body
        return node

# Example Python code to instrument
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

# Parse the code to an AST
parsed_code = ast.parse(code)

# Create an instrumentor and modify the AST
instrumentor = CodeInstrumentor()
instrumented_code = instrumentor.visit(parsed_code)

# Convert the modified AST back to source code and execute it
instrumented_source = astor.to_source(instrumented_code)
# print(instrumented_source)  # Optionally print the modified code to see the changes
exec(instrumented_source)
# print(ast.dump(parsed_code, indent = 4))
print(parsed_code)
f=open(r'output.txt','w')
f.write(ast.dump(parsed_code, indent = 4))
f.close()