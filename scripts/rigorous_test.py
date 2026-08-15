import sys
import os
import numpy as np

# Adjust sys.path to find ReverieHacks packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.search import run_hypothesis_search

def test_part_1_harmonic():
    print("\n=============================================")
    print("TESTING PART 1: Damped Harmonic Oscillator (Physics)")
    print("=============================================")
    np.random.seed(42)
    x = np.linspace(0, 10, 100)
    # y = 5 * exp(-0.3 * x) * cos(2 * x) + noise
    y = 5.0 * np.exp(-0.3 * x) * np.cos(2.0 * x) + np.random.normal(0, 0.1, size=100)
    
    summary = """Columns: 'x' (time) and 'y' (amplitude).
Data Points Count: 100
X Range: [0.0, 10.0]
Y Range: Damped sinusoidal oscillations with decay.
"""
    res = run_hypothesis_search(x, y, summary, "Astrophysics & Wave Mechanics")
    
    print("\nDiscovered Leaderboard:")
    for idx, model in enumerate(res["leaderboard"][:3]):
        print(f"Rank {idx+1}: {model['simplified_eq']} | R^2: {model['r2']:.4f} | AIC: {model['aic']:.2f}")
    return res

def test_part_2_piecewise():
    print("\n=============================================")
    print("TESTING PART 2: Piecewise Step Function (Discontinuous)")
    print("=============================================")
    np.random.seed(42)
    x = np.linspace(-5, 5, 100)
    y = np.where(x > 0, 1.0, -1.0)
    
    summary = """Columns: 'x' (input) and 'y' (state).
Data Points Count: 100
X Range: [-5.0, 5.0]
Y Range: Step function (-1 for negative X, +1 for positive X).
"""
    res = run_hypothesis_search(x, y, summary, "Digital Signal Processing")
    
    print("\nDiscovered Leaderboard:")
    if not res["leaderboard"]:
        print("No models converged (expected behavior for pure discontinuous step functions).")
    else:
        for idx, model in enumerate(res["leaderboard"][:3]):
            print(f"Rank {idx+1}: {model['simplified_eq']} | R^2: {model['r2']:.4f} | AIC: {model['aic']:.2f}")
    return res

def test_part_3_galactic():
    print("\n=============================================")
    print("TESTING PART 3: Galactic Rotation Velocity Curve (Dark Matter / MOND)")
    print("=============================================")
    np.random.seed(42)
    # Distance from galactic core (kpc)
    r = np.linspace(0.5, 30, 100)
    # v(r) = 220 * r / (r + 2.0) + noise (Monomial rise to flat orbital speed)
    v = 220.0 * r / (r + 2.0) + np.random.normal(0, 5.0, size=100)
    
    summary = """Columns: 'r' (radius in kpc) and 'v' (orbital velocity in km/s).
Data Points Count: 100
X Range: [0.5, 30.0]
Y Range: Rises sharply at core, then flattens out around 220 km/s.
"""
    res = run_hypothesis_search(r, v, summary, "Astrophysics")
    
    print("\nDiscovered Leaderboard:")
    for idx, model in enumerate(res["leaderboard"][:3]):
        print(f"Rank {idx+1}: {model['simplified_eq']} | R^2: {model['r2']:.4f} | AIC: {model['aic']:.2f}")
    return res

if __name__ == "__main__":
    test_part_1_harmonic()
    test_part_2_piecewise()
    test_part_3_galactic()
