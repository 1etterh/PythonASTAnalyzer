# visualize-ast
 visualize ast for code analysis
# used libraries
 ast, astor, graphviz
#### _PythonASTAnalyzer(ast.NodeTransformer)_
1. **custom** **subclass** of *ast.NodeTransformer*
2. _visit_  : save variable names
3. used for understanding the overall structure of Algorithm code
4. since it is used for understanding overall structure of code, it doesn't track actual value on runtime
5. creates AST structure of tree and order and nodes.
