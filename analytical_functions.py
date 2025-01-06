import numpy as np
from scipy.stats import norm
from decimal import Decimal, getcontext

"""'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
FUNCTION TO COMPUTE THE EQUITY VALUE BASED ON MERTON
"""''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def merton_equity(V,K,r,sigma,T,t):
    if K != 0:
        d1 = (np.log(V/K) + (r + 0.5*sigma**2)*(T-t))/ (sigma * np.sqrt(T-t))
        d2 = d1 - sigma*np.sqrt(T-t)
        St = V*norm.cdf(d1) - K*np.exp(-r*(T-t))*norm.cdf(d2)

    else:

        St = V

    return St

"""'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
FUNCTION TO COMPUTE THE DEBT VALUE BASED ON MERTON
"""''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def merton_debt(V,K,r,sigma,T,t):
    if K != 0: 
        d1 = (np.log(V/K) + (r + 0.5*sigma**2)*(T-t))/ (sigma * np.sqrt(T-t))
        d2 = d1 - sigma*np.sqrt(T-t)
        Bt = K*np.exp(-r*(T-t))*norm.cdf(d2) + V*(1-norm.cdf(d1))

    else:

        Bt = 0
    
    return Bt

"""'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
FUNCTION TO COMPUTE THE PROBABILY OF DEFAULT UNDER RISK-NEUTRAL MEASURE
"""''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def risk_neutral_default_probability(V, B, r, sigma, T, t, precision = 20):
    getcontext().prec = precision
    
    if B != 0:
        V = Decimal(V)
        B = Decimal(B)
        r = Decimal(r)
        sigma = Decimal(sigma)
        T = Decimal(T)
        #t = Decimal(t)
        d2 = (np.log(float(V / B)) + float((r - Decimal('0.5') * sigma**2) * (T - t))) / float(sigma * (T - t).sqrt())
        return float(norm.cdf(-d2))
    
    else:
        return 0

"""
This function computes the real-world probability of default according to the Merton's model

The Decimal package is used to increase the precision of the computations as for well-capitalized firms
and short maturities the probability of default can be quite small.
"""
def default_probability(V, B, r, sigma, T, t, precision = 20):
    getcontext().prec = precision
    
    if B != 0:
        V_d = Decimal(V)
        B_d = Decimal(B)
        r_d = Decimal(r)
        sigma_d = Decimal(sigma)
        T_d = Decimal(T)
        #t = Decimal(t)
        arg = ( np.log(float(B_d/V_d)) - float(0 - Decimal('0.5') *sigma_d**2) ) / float(sigma_d*np.sqrt(T_d-t))
        return float(norm.cdf(arg))
    
    else:
        return 0


"""
This function implements the Monte Carlo approximation of the probability of default according 
to the Merton's model.

The function also uses anthitetic variates to reduce the standard error of the approximation.

It also simulates the logarithm of the value of the assets and uses the logarithm of the debt
as a threshold for numerical stability purposes as we are dealing with public companies that 
can be valued in the order of trillions.

There are commments that can be activated for the purposes of debugging the results.
"""

def monte_carlo_merton_anti(V_0, K, r, sigma, T, M):

    V_d = Decimal(V_0)
    K_d = Decimal(K)
    r_d = Decimal(r)
    sigma_d = Decimal(sigma)
    T_d = Decimal(T)
    t_d = Decimal(0)

    threshold = (np.log(float(K_d/V_d)) - float(0 - Decimal('0.5') *sigma_d**2)) / float(sigma_d*np.sqrt(T_d-t_d))
    print(f'The threshold is: {threshold}\n')

    threshold = (np.log(K / V_0) - (-0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

    print(f'The threshold without the decimals is: {threshold}')

    W_T = np.random.randn(M) * np.sqrt(T)
    print(f'The number of observations below the threshold is: {np.sum(W_T < threshold)}')

    log_V_T = np.log(V_0) + ((-0.5 * sigma**2) * T) + (sigma * W_T)

    log_V_T_anti = np.log(V_0) + ((-0.5 * sigma**2) * T) - (sigma * W_T)

    total_sims = np.concatenate((log_V_T, log_V_T_anti))

    defaulted_simulations = np.sum(log_V_T < np.log(K))
    print(f'The number of simulated defaults is: {defaulted_simulations}')
    
    # Debug info
    print(f"Min log(V_T) - Anti: {np.min(total_sims)}, Max log(V_T) - Anti: {np.max(total_sims)}, Threshold - Anti: {np.log(K)}")
    prob_default = (defaulted_simulations / M)


    # num_decimal = np.log(float(K_d / V_d))
    # den_decimal = float(sigma_d * np.sqrt(T_d - t_d))
    # term_decimal = float(Decimal('0.5') * sigma_d**2) / den_decimal
    # threshold_decimal = num_decimal - term_decimal

    # print(f"Decimal Calculation -> num: {num_decimal}, den: {den_decimal}, term: {term_decimal}, threshold: {threshold_decimal}")


    # num_float = np.log(K / V_0)
    # den_float = sigma * np.sqrt(T)
    # term_float = (-0.5 * sigma**2) * T / den_float
    # threshold_float = (num_float - term_float) / den_float

    # print(f"Float Calculation -> num: {num_float}, den: {den_float}, term: {term_float}, threshold: {threshold_float}")

    
    return prob_default


"""
This function returns the simulated paths of Random Walks processes that were used
for the purposes of Monte Carlo approximation of the probability of default. 
"""

def monte_carlo_simulation_paths(V0, sigma, r, T, M, N, K, log = False):
    """
    Generate Monte Carlo simulated asset paths using geometric Brownian motion.

    Parameters:
    - V0 (float): Initial asset value.
    - sigma (float): Asset volatility.
    - r (float): Risk-free rate.
    - T (float): Time horizon (years).
    - M (int): Number of paths.
    - N (int): Number of time steps.

    Returns:
    - np.ndarray: Simulated asset paths (shape: [M, N]).
    """
    dt = T / N
    paths = np.zeros((M, N))
    if log:
        paths[:, 0] = np.log(V0)

        for t in range(1, N):
            z = np.random.standard_normal(M)
            paths[:, t] = paths[:, t - 1] + ((0 - 0.5 * sigma ** 2) * dt) + (sigma * np.sqrt(dt) * z)    

            defaults = np.sum(np.array(paths[:,-1] < np.log(K)))
        print(f"\nMin log(V_T) - Paths: {np.min(paths[:,-1])}, Max log(V_T) - Paths: {np.max(paths[:,-1])}, Threshold - Paths: {np.log(K)}")
        print(f'\n\nThe defaults of the monte carlo paths is {defaults}')
        print(f'For threshold: {np.log(K)}\n')

    else:

        paths[:, 0] = V0

        for t in range(1, N):
            z = np.random.standard_normal(M)
            paths[:, t] = paths[:, t - 1] * np.exp( ((0 - 0.5 * sigma ** 2) * dt) + (sigma * np.sqrt(dt) * z) )    

            defaults = np.sum(np.array(paths[:,-1] < K))
        print(f"\nMin V_T - Paths: {np.min(paths[:,-1])}, Max V_T - Paths: {np.max(paths[:,-1])}, Threshold - Paths: {K}")
        print(f'\n\nThe defaults of the monte carlo paths is {defaults}')
        print(f'For threshold: {np.log(K)}\n')

    return paths


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
FUNCTION TO COMPUTE THE CREDIT SPREAD
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def credit_spread_model(V, K, sigma, r, T, t):
    if K != 0:
        # 1) Riskless bond price (for face value K)
        p_0 = np.exp(-r * (T - t))

        # 2) Calculate d1 and d2
        d1 = (-(np.log((K*p_0)/V)) + (0 + 0.5*sigma**2) * (T - t)) / (sigma * np.sqrt(T -t))

        d2 = d1 - (sigma * np.sqrt(T - t))

        # 3) *Defaultable* bond price using Merton's debt formula
        #defaultable_bond = K * riskless * norm.cdf(d2) + V * (1 - norm.cdf(d1))

        # 4) Credit spread calculation: -1/(T - t) * ln(defaultable_bond / riskless_bond)
        credit_spread = -1/(T - t) * np.log(norm.cdf(d2) + (V/(K *p_0))*norm.cdf(-d1))

    else: 

        credit_spread = 0

    return credit_spread

