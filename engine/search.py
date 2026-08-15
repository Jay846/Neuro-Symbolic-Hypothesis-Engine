import numpy as np
from engine.generator import generate_equations, self_heal_equation
from engine.executor import validate_and_simplify
from engine.optimizer import fit_parameters

def run_hypothesis_search(x_data: np.ndarray, y_data: np.ndarray, data_summary: str, domain_context: str = "") -> dict:
    """
    Search loop that generates, validates, optimizes, and heals candidate models.
    """
    leaderboard = []
    logs = []
    
    # 1. Generate candidate equations
    candidates = generate_equations(data_summary, domain_context, logs)
    
    logs.append(f"Generated {len(candidates)} initial candidates from Featherless AI.")
    
    for idx, cand in enumerate(candidates):
        eq_str = cand.get("equation_str", "")
        params = cand.get("parameters", [])
        reasoning = cand.get("reasoning", "")
        
        logs.append(f"\n--- Evaluating Candidate {idx+1}: {eq_str} ---")
        logs.append(f"Reasoning: {reasoning}")
        
        # Validation & Self-Healing Loop
        max_attempts = 3
        attempt = 1
        current_eq = eq_str
        current_params = params
        
        while attempt <= max_attempts:
            logs.append(f"Attempt {attempt}: Validating structure...")
            val_res = validate_and_simplify(current_eq, current_params)
            
            if not val_res["success"]:
                error_msg = val_res["error"]
                logs.append(f"Validation failed: {error_msg}")
                if attempt == max_attempts:
                    logs.append("Reached max healing attempts. Skipping candidate.")
                    break
                logs.append("Triggering self-healing...")
                heal_res = self_heal_equation(current_eq, error_msg)
                current_eq = heal_res.get("equation_str", current_eq)
                current_params = heal_res.get("parameters", current_params)
                attempt += 1
                continue
                
            # If validation succeeded, try optimization/fitting
            logs.append(f"Validation succeeded. Simplified Form: {val_res['simplified_str']}")
            logs.append("Fitting parameters to dataset...")
            fit_res = fit_parameters(val_res["expr"], current_params, x_data, y_data)
            
            if not fit_res["success"]:
                error_msg = fit_res["error"]
                logs.append(f"Fitting failed: {error_msg}")
                if attempt == max_attempts:
                    logs.append("Reached max healing attempts. Skipping candidate.")
                    break
                logs.append("Triggering self-healing for fitting failure...")
                heal_res = self_heal_equation(current_eq, error_msg)
                current_eq = heal_res.get("equation_str", current_eq)
                current_params = heal_res.get("parameters", current_params)
                attempt += 1
                continue
            
            # If everything succeeded
            logs.append(f"Fitting successful! R^2: {fit_res['r2']:.4f}, AIC: {fit_res['aic']:.2f}")
            leaderboard.append({
                "original_eq": eq_str,
                "final_eq": current_eq,
                "simplified_eq": val_res["simplified_str"],
                "parameters": fit_res["parameters"],
                "r2": fit_res["r2"],
                "aic": fit_res["aic"],
                "bic": fit_res["bic"],
                "reasoning": reasoning,
                "y_pred": fit_res["y_pred"]
            })
            
            # --- Local Mutation Search (Expression Trees) ---
            try:
                from engine.tree import parse_string_to_tree, mutate_tree
                tree_root = parse_string_to_tree(current_eq)
                logs.append("Triggering local Expression Tree mutations...")
                
                # Generate 2 distinct mutations
                mutations_tried = set()
                mut_idx = 0
                while len(mutations_tried) < 2 and mut_idx < 10:
                    mut_idx += 1
                    mut_params = list(current_params)
                    mutated_tree = mutate_tree(tree_root, mut_params)
                    mutated_eq = mutated_tree.to_string()
                    
                    if mutated_eq in mutations_tried or mutated_eq == current_eq:
                        continue
                    
                    mutations_tried.add(mutated_eq)
                    logs.append(f"  Mutation Candidate: {mutated_eq}")
                    
                    # Validate mutated candidate
                    mut_val = validate_and_simplify(mutated_eq, mut_params)
                    if mut_val["success"]:
                        # Fit mutated candidate
                        mut_fit = fit_parameters(mut_val["expr"], mut_params, x_data, y_data)
                        if mut_fit["success"]:
                            logs.append(f"    Mutation successful! R^2: {mut_fit['r2']:.4f}, AIC: {mut_fit['aic']:.2f}")
                            leaderboard.append({
                                "original_eq": eq_str,
                                "final_eq": mutated_eq,
                                "simplified_eq": mut_val["simplified_str"],
                                "parameters": mut_fit["parameters"],
                                "r2": mut_fit["r2"],
                                "aic": mut_fit["aic"],
                                "bic": mut_fit["bic"],
                                "reasoning": f"Local mutation search derived from: {reasoning}",
                                "y_pred": mut_fit["y_pred"]
                            })
                        else:
                            logs.append(f"    Mutation fitting failed: {mut_fit['error']}")
                    else:
                        logs.append(f"    Mutation validation failed: {mut_val['error']}")
            except Exception as e:
                logs.append(f"Local mutation search error: {str(e)}")
            break
            
    # Sort leaderboard by R-squared descending, then AIC ascending
    leaderboard.sort(key=lambda x: (-x["r2"], x["aic"]))
    
    return {
        "leaderboard": leaderboard,
        "logs": logs
    }
