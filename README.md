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


#### _ValueTracker(ast.NodeTransformer)_
1. used for observing variables in runtime
2. visualizes each turns of loop through graphviz
3. show values of variables in runtime