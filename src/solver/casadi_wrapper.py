import casadi as ca
import numpy as np
from scipy.optimize import OptimizeResult

def casadi_minimize(fun, x0, constraints=(), tol=None, options=None):
    """
    Wrapper around CasADi (IPOPT), mimicking the scipy.optimize.minimize interface.
    
    Important: The function `fun` and functions inside `constraints` must be written 
    such that they can accept CasADi symbolic variables (MX). 
    This means: use numpy instead of math, avoid if/else statements dependent on x.
    """
    
    # Option normalization
    options = options if options else {}
    verbose = options.get('disp', False)
    
    # Initialize CasADi Opti
    opti = ca.Opti()
    
    # Create variables
    # x0 must be a flat array
    x0_arr = np.array(x0, dtype=float).flatten()
    n_vars = len(x0_arr)
    
    x = opti.variable(n_vars)
    opti.set_initial(x, x0_arr)
    
    # Construct the Objective Function (Tracing)
    # We call the passed function `fun` with symbolic variables `x`
    try:
        obj = fun(x)
        opti.minimize(obj)
    except Exception as e:
        print (str(e))

    # Process Constraints
    # Scipy accepts either a dict or a list of dicts
    if isinstance(constraints, dict):
        constraints = [constraints]
        
    for constraint in constraints:
        c_type = constraint.get('type') # 'eq' or 'ineq'
        c_fun = constraint.get('fun')
        
        if c_fun is None:
            continue
            
        try:
            # Calculate constraint values (symbolically)
            res = c_fun(x)
            
            # Add to Opti
            for r in res:
                if c_type == 'eq':
                    opti.subject_to(r == 0)
                elif c_type == 'ineq':
                    opti.subject_to(r >= 0)
                    
        except Exception as e:
            print (str(e))

    # Solver Setup (IPOPT)
    s_opts = {
        "max_iter": options.get('maxiter', 100),
        "tol": tol if tol else 1e-4,
        "acceptable_tol": 1e-3,
        "print_level": 5 if verbose else 0, # 0 - silent
        "sb": "yes" # Suppress banner
    }

    p_opts = {
        "expand": True,
        "print_time": verbose, 
        "error_on_fail": True
    }
    
    opti.solver('ipopt', p_opts, s_opts)
    
    # Solve
    res_x = x0_arr
    success = False
    status_msg = ""
    fun_val = 0.0
    
    try:
        sol = opti.solve()
        res_x = sol.value(x)
        fun_val = sol.value(obj)
        success = True
        status_msg = "Optimization terminated successfully."
    except Exception:
        # If it didn't converge perfectly, take the "debug" value (last best known)
        try:
            res_x = opti.debug.value(x)
            fun_val = opti.debug.value(obj)
            status_msg = "Optimization failed to converge to target tolerance."
        except:
            status_msg = "Optimization failed completely."

    # Form the result in Scipy style
    result = OptimizeResult(
        x = res_x,
        success = success,
        status = 0 if success else 1,
        message = status_msg,
        fun = fun_val,
        nit = opti.debug.stats()['iter_count'] if hasattr(opti.debug, 'stats') else 0
    )
    
    return result