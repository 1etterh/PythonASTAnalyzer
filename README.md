# visualize-ast
 visualize ast for code analysis
# used libraries
 ast, graphviz
#### _CodeAnalyzer(ast.NodeTransformer)_
1. **custom** **subclass** of *ast.NodeTransformer*
2. _visit_  : save variable names
3. used for understanding the overall structure of Algorithm code
4. since it is used for understanding overall structure of code, it doesn't track actual value on runtime