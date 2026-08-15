import numpy as np
import sympy as sp
from scipy.optimize import curve_fit

def fit_parameters(expr, parameter_names: list, x_data: np.ndarray, y_data: np.ndarray) -> dict:
    """
    Fits the parameters of a SymPy expression to x_data and y_data using SciPy.
    Computes quality metrics: R^2, AIC, and BIC.
    """
    try:
        # Define x as symbol
        x_symbol = sp.Symbol('x')
        param_symbols = [sp.Symbol(name) for name in parameter_names]
        
        # Lambdify the expression to a fast NumPy function
        # The signature must be (x, param1, param2, ...)
        f_lambdified = sp.lambdify([x_symbol] + param_symbols, expr, modules=['numpy', 'scipy'])
        
        # Wrap it for curve_fit: curve_fit expects function signature f(x, *params)
        def fit_func(x, *params):
            return f_lambdified(x, *params)
            
        # Initial guess of 1.0 for all parameters
        p0 = [1.0] * len(parameter_names)
        
        # Perform curve fit
        # We handle bounds or errors when calculations result in NaNs/Infs
        popt, pcov = curve_fit(fit_func, x_data, y_data, p0=p0, maxfev=5000)
        
        # Calculate residuals and metrics
        y_pred = fit_func(x_data, *popt)
        residuals = y_data - y_pred
        rss = np.sum(residuals ** 2)
        tss = np.sum((y_data - np.mean(y_data)) ** 2)
        
        # R-squared
        r2 = 1.0 - (rss / tss) if tss != 0 else 0.0
        
        # Number of parameters (k) and data points (N)
        k = len(parameter_names)
        N = len(x_data)
        
        # AIC & BIC
        # Avoid log of zero
        eps = 1e-10
        mse = max(rss / N, eps)
        aic = N * np.log(mse) + 2 * k
        bic = N * np.log(mse) + k * np.log(N)
        
        # Format parameters dict
        fitted_params = {name: float(val) for name, val in zip(parameter_names, popt)}
        
        return {
            "success": True,
            "parameters": fitted_params,
            "r2": float(r2),
            "aic": float(aic),
            "bic": float(bic),
            "rss": float(rss),
            "y_pred": y_pred.tolist()
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Optimization curve fit failed: {str(e)}"
        }
