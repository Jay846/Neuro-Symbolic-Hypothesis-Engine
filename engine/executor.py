import ast
import sympy as sp
import requests
from config import WOLFRAM_APP_ID, WOLFRAM_API_URL

# Allowed functions in our math sandbox
ALLOWED_FUNCTIONS = {
    'sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'sinh', 'cosh', 'tanh',
    'asin', 'acos', 'atan', 'pi', 'e', 'abs'
}

def check_ast_safety(equation_str: str, parameters: list = None) -> bool:
    """
    AST Guardrail: Scan the equation string to verify it contains only math operations
    and safe variables/functions. Prevents code injection.
    """
    if parameters is None:
        parameters = []
    import builtins
    builtins_list = dir(builtins)
    
    try:
        tree = ast.parse(equation_str, mode='eval')
        
        # Whitelisted AST node classes for safe mathematical expressions
        allowed_classes = (
            ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
            ast.Name, ast.Call, ast.Load,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd
        )
        
        for node in ast.walk(tree):
            if not isinstance(node, allowed_classes):
                return False
            if isinstance(node, ast.Name):
                name_id = node.id
                if name_id not in ALLOWED_FUNCTIONS and name_id != 'x' and name_id not in parameters:
                    # Allow parameter name if it's a valid identifier and not a python builtin
                    if name_id in builtins_list or not name_id.isidentifier():
                        return False
            elif isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCTIONS:
                    return False
        return True
    except SyntaxError:
        return False
        
def validate_and_simplify(equation_str: str, parameters: list) -> dict:
    """
    Validates SymPy compatibility, simplfies the expression, and detects singularities.
    """
    if not check_ast_safety(equation_str, parameters):
        return {"success": False, "error": "AST verification failed: Unsafe expression or syntax error."}
    
    try:
        # Define symbols
        symbols_dict = {name: sp.Symbol(name) for name in parameters + ['x']}
        
        # Parse using SymPy
        # Using sympy's parse_expr which supports standard python syntax
        expr = sp.parse_expr(equation_str, local_dict=symbols_dict)
        
        # Check if expression is simplified
        simplified = sp.simplify(expr)
        
        # Check for division by zero risk
        # Find points where denominator could be zero (basic check)
        singularities = []
        denom = sp.denom(simplified)
        if denom != 1:
            try:
                # Solve denom = 0 for x
                sols = sp.solve(denom, symbols_dict['x'])
                singularities = [float(sol.evalf()) for sol in sols if sol.is_real]
            except Exception:
                # If solving fails, just flag denominator presence
                singularities = ["unknown"]
                
        return {
            "success": True,
            "expr": expr,
            "simplified_str": str(simplified),
            "singularities": singularities
        }
    except Exception as e:
        return {"success": False, "error": f"SymPy evaluation error: {str(e)}"}

def query_wolfram_alpha(query: str) -> str:
    """
    Query the Wolfram | Alpha API for symbolic derivation or simplification.
    """
    if not WOLFRAM_APP_ID:
        return "Wolfram AppID not configured. Skipping."
        
    params = {
        "appid": WOLFRAM_APP_ID,
        "input": query,
        "output": "json"
    }
    
    try:
        response = requests.get(WOLFRAM_API_URL, params=params)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Wolfram API Error: {str(e)}"
