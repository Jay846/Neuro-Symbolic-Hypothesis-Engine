import random
import ast

BINARY_OPERATORS = ['+', '-', '*', '/', '**']
UNARY_FUNCTIONS = ['sin', 'cos', 'exp', 'log', 'tanh', 'sinh', 'cosh', 'sqrt', 'abs']
LEAF_TYPES = ['variable', 'parameter', 'constant']

class MathNode:
    def __init__(self, node_type, value=None, left=None, right=None, child=None):
        """
        node_type: 'binary', 'unary', 'variable', 'parameter', 'constant'
        value: operator symbol, function name, variable name, or float value
        """
        self.node_type = node_type
        self.value = value
        self.left = left      # Binary left child
        self.right = right    # Binary right child
        self.child = child    # Unary child

    def to_string(self) -> str:
        """
        Recursively compiles the node tree into an executable python mathematical expression string.
        """
        if self.node_type == 'constant':
            return str(self.value)
        elif self.node_type == 'variable' or self.node_type == 'parameter':
            return str(self.value)
        elif self.node_type == 'unary':
            if self.value == 'neg':
                return f"-({self.child.to_string()})"
            return f"{self.value}({self.child.to_string()})"
        elif self.node_type == 'binary':
            # Return paren-wrapped terms to preserve correct priority
            return f"({self.left.to_string()}) {self.value} ({self.right.to_string()})"
        return ""

    def clone(self):
        """
        Returns a deep copy of this MathNode and its entire subtree.
        """
        return MathNode(
            node_type=self.node_type,
            value=self.value,
            left=self.left.clone() if self.left else None,
            right=self.right.clone() if self.right else None,
            child=self.child.clone() if self.child else None
        )

def parse_string_to_tree(equation_str: str) -> MathNode:
    """
    Parses a python mathematical equation string into an Expression Tree.
    """
    try:
        expr_ast = ast.parse(equation_str, mode='eval')
        return _parse_ast_node(expr_ast.body)
    except Exception as e:
        raise ValueError(f"Failed to parse equation AST: {str(e)}")

def _parse_ast_node(node) -> MathNode:
    if isinstance(node, ast.BinOp):
        op_map = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Pow: '**'
        }
        op_symbol = op_map.get(type(node.op))
        if not op_symbol:
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
        return MathNode(
            node_type='binary',
            value=op_symbol,
            left=_parse_ast_node(node.left),
            right=_parse_ast_node(node.right)
        )
    elif isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            return MathNode(
                node_type='unary',
                value='neg',
                child=_parse_ast_node(node.operand)
            )
        elif isinstance(node.op, ast.UAdd):
            return _parse_ast_node(node.operand)
        raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Calls must target registered functional names directly.")
        func_name = node.func.id
        if len(node.args) != 1:
            raise ValueError("All mathematical functions must take exactly 1 argument.")
        return MathNode(
            node_type='unary',
            value=func_name,
            child=_parse_ast_node(node.args[0])
        )
    elif isinstance(node, ast.Name):
        if node.id == 'x':
            return MathNode(node_type='variable', value='x')
        else:
            return MathNode(node_type='parameter', value=node.id)
    elif isinstance(node, (ast.Num, ast.Constant)):
        val = node.n if isinstance(node, ast.Num) else node.value
        return MathNode(node_type='constant', value=val)
    raise ValueError(f"Unmapped AST Node class: {type(node).__name__}")

def collect_nodes_list(node: MathNode):
    """
    Traverses the tree and returns a flat list of all nodes.
    """
    nodes = [node]
    if node.left:
        nodes.extend(collect_nodes_list(node.left))
    if node.right:
        nodes.extend(collect_nodes_list(node.right))
    if node.child:
        nodes.extend(collect_nodes_list(node.child))
    return nodes

def mutate_tree(root: MathNode, parameters: list) -> MathNode:
    """
    Performs a random mutation on the tree:
    1. Operator Swap (Binary swap: + to *; Unary swap: sin to cos)
    2. Leaf Growth (Constant/Variable turns into a product/sum with a parameter)
    3. Pruning (Replaces a subtree with a single child or leaf)
    """
    mutated_root = root.clone()
    all_nodes = collect_nodes_list(mutated_root)
    
    if not all_nodes:
        return mutated_root

    target_node = random.choice(all_nodes)
    mutation_type = random.choice(['swap', 'grow', 'prune'])
    
    # Generate a next parameter letter
    next_param = chr(ord('a') + len(parameters)) if len(parameters) < 10 else 'c'
    if next_param not in parameters:
        parameters.append(next_param)
        
    if mutation_type == 'swap':
        if target_node.node_type == 'binary':
            # Swap with another binary operator
            target_node.value = random.choice([op for op in BINARY_OPERATORS if op != target_node.value])
        elif target_node.node_type == 'unary':
            # Swap with another function
            target_node.value = random.choice([func for func in UNARY_FUNCTIONS if func != target_node.value])
            
    elif mutation_type == 'grow':
        # Replace a leaf (or any node) with a binary expansion: Node -> (Node) * param or (Node) + param
        if target_node.node_type in ['variable', 'parameter', 'constant']:
            original_type = target_node.node_type
            original_val = target_node.value
            
            # Make target node a binary node
            target_node.node_type = 'binary'
            target_node.value = random.choice(['+', '*'])
            target_node.left = MathNode(node_type=original_type, value=original_val)
            target_node.right = MathNode(node_type='parameter', value=next_param)
            
    elif mutation_type == 'prune':
        # Replace binary or unary node with its child to simplify the structure
        if target_node.node_type == 'binary':
            child_to_keep = random.choice([target_node.left, target_node.right])
            # Copy child properties to target_node
            target_node.node_type = child_to_keep.node_type
            target_node.value = child_to_keep.value
            target_node.left = child_to_keep.left
            target_node.right = child_to_keep.right
            target_node.child = child_to_keep.child
        elif target_node.node_type == 'unary':
            child_to_keep = target_node.child
            target_node.node_type = child_to_keep.node_type
            target_node.value = child_to_keep.value
            target_node.left = child_to_keep.left
            target_node.right = child_to_keep.right
            target_node.child = child_to_keep.child
            
    return mutated_root
