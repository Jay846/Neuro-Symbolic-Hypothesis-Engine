import sys
import os
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# Adjust sys.path to find ReverieHacks packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.search import run_hypothesis_search

def generate_and_verify_galactic():
    # 1. Synthesize Galactic Rotation Data
    np.random.seed(42)
    r = np.linspace(0.5, 30, 100)
    # True velocity curve: rises to ~220 km/s and flattens out
    v_true = 220.0 * r / (r + 2.0)
    v_noisy = v_true + np.random.normal(0, 5.0, size=100)
    
    summary = """Columns: 'r' (radius) and 'v' (velocity).
Data Points Count: 100
X Range: [0.5, 30.0]
"""
    print("Step 1: Running the Symbolic Regression Engine...")
    # Search for the best functional form
    res = run_hypothesis_search(r, v_noisy, summary, "Astrophysics")
    
    best_model = res["leaderboard"][0]
    simplified_eq = best_model["simplified_eq"]
    p_vals = best_model["parameters"] # Dict of name -> value
    
    print(f"\nBest Discovered Equation: {simplified_eq}")
    print(f"Discovered parameters: {p_vals}")
    
    # Compile sympy expression for dynamic evaluation
    expr = sp.parse_expr(simplified_eq)
    
    # 2. Extract best equation and evaluate points
    print("\nStep 2: Generating Verification Table")
    print("-" * 75)
    print(f"{'Radius (kpc)':<15} | {'Observed Velocity':<22} | {'Fitted Velocity (km/s)':<22} | {'Error':<10}")
    print("-" * 75)
    
    # We will compute the fitted values using SymPy substitution to ensure absolute correctness
    test_indices = np.linspace(0, len(r) - 1, 10, dtype=int)
    for idx in test_indices:
        r_val = r[idx]
        v_val = v_noisy[idx]
        
        # Build substitution dictionary: map parameter names and 'x' to values
        subs = {sp.Symbol(name): float(val) for name, val in p_vals.items()}
        subs[sp.Symbol('x')] = float(r_val)
        
        # Evaluate
        v_fit = float(expr.subs(subs).evalf())
        
        err = abs(v_val - v_fit)
        print(f"{r_val:<15.2f} | {v_val:<22.2f} | {v_fit:<22.2f} | {err:<10.2f}")
    print("-" * 75)
    
    # 3. Save plot
    print("\nStep 3: Generating Visual Plot...")
    os.makedirs("static", exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.scatter(r, v_noisy, color='orange', alpha=0.6, label='Simulated Star Velocities (Raw Data)')
    
    # Generate smooth line using fitted parameters
    r_smooth = np.linspace(0.5, 30, 200)
    v_smooth = []
    for r_val in r_smooth:
        subs = {sp.Symbol(name): float(val) for name, val in p_vals.items()}
        subs[sp.Symbol('x')] = float(r_val)
        v_smooth.append(float(expr.subs(subs).evalf()))
        
    plt.plot(r_smooth, v_smooth, color='cyan', linewidth=3, label=f'Engine Discovery: {simplified_eq}')
    plt.title("Galactic Rotation Velocity Curve: Raw Observations vs. Engine Discovery", fontsize=14)
    plt.xlabel("Galactic Core Distance r (kpc)", fontsize=12)
    plt.ylabel("Orbital Velocity v (km/s)", fontsize=12)
    
    # Theme the plot to match the dark dashboard
    ax = plt.gca()
    ax.set_facecolor('#0d1117')
    plt.gcf().patch.set_facecolor('#0d1117')
    ax.spines['bottom'].set_color('#30363d')
    ax.spines['top'].set_color('#30363d')
    ax.spines['left'].set_color('#30363d')
    ax.spines['right'].set_color('#30363d')
    ax.xaxis.label.set_color('#8b949e')
    ax.yaxis.label.set_color('#8b949e')
    ax.tick_params(colors='#8b949e')
    plt.grid(color='#30363d', linestyle='--', linewidth=0.5)
    plt.legend(facecolor='#161b22', edgecolor='#30363d', labelcolor='white')
    
    plot_path = "static/galactic_fit.png"
    plt.savefig(plot_path, dpi=150)
    print(f"Visual plot successfully saved to: {plot_path}")

if __name__ == "__main__":
    generate_and_verify_galactic()
