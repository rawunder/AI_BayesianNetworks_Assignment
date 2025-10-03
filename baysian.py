import pyagrum as gum
import pyagrum.lib.notebook as gnb
import pyagrum.lib.image as gumimage

# ===================================================================
#                      1. DEFINE NETWORK STRUCTURE
# ===================================================================
print("Creating Influence Diagram structure...")
# Create the Influence Diagram
bn = gum.InfluenceDiagram()


# --- CHANCE NODES ---
# Exogenous Drivers
gdp_var = gum.LabelizedVariable('GDP_Trend', 'GDP Trend', 4)
gdp_var.changeLabel(0, 'Recession'); gdp_var.changeLabel(1, 'Stagnant'); gdp_var.changeLabel(2, 'Moderate'); gdp_var.changeLabel(3, 'Strong')
bn.add(gdp_var)

inflation_var = gum.LabelizedVariable('Inflation_Env', 'Inflation Environment', 3)
inflation_var.changeLabel(0, 'Deflationary'); inflation_var.changeLabel(1, 'Low'); inflation_var.changeLabel(2, 'High')
bn.add(inflation_var)

# Endogenous Factors
interest_rate_var = gum.LabelizedVariable('Interest_Rate', 'Interest Rate Trajectory', 3)
interest_rate_var.changeLabel(0, 'Cutting'); interest_rate_var.changeLabel(1, 'Holding'); interest_rate_var.changeLabel(2, 'Hiking')
bn.add(interest_rate_var)

volatility_var = gum.LabelizedVariable('Market_Vol', 'Market Volatility', 3)
volatility_var.changeLabel(0, 'Low'); volatility_var.changeLabel(1, 'Normal'); volatility_var.changeLabel(2, 'High')
bn.add(volatility_var)

# Asset Performance Nodes
stock_perf_var = gum.LabelizedVariable('Stock_Perf', 'Stock Performance', 5)
stock_perf_var.changeLabel(0, 'Strong_Loss'); stock_perf_var.changeLabel(1, 'Minor_Loss'); stock_perf_var.changeLabel(2, 'Neutral'); stock_perf_var.changeLabel(3, 'Minor_Gain'); stock_perf_var.changeLabel(4, 'Strong_Gain')
bn.add(stock_perf_var)

bond_perf_var = gum.LabelizedVariable('Bond_Perf', 'Bond Performance', 5)
bond_perf_var.changeLabel(0, 'Strong_Loss'); bond_perf_var.changeLabel(1, 'Minor_Loss'); bond_perf_var.changeLabel(2, 'Neutral'); bond_perf_var.changeLabel(3, 'Minor_Gain'); bond_perf_var.changeLabel(4, 'Strong_Gain')
bn.add(bond_perf_var)

crypto_perf_var = gum.LabelizedVariable('Crypto_Perf', 'Crypto Performance', 5)
crypto_perf_var.changeLabel(0, 'Strong_Loss'); crypto_perf_var.changeLabel(1, 'Minor_Loss'); crypto_perf_var.changeLabel(2, 'Neutral'); crypto_perf_var.changeLabel(3, 'Minor_Gain'); crypto_perf_var.changeLabel(4, 'Strong_Gain')
bn.add(crypto_perf_var)

# Generalized Outcome
portfolio_outcome_var = gum.LabelizedVariable('Portfolio_Out', 'Portfolio Outcome', 5)
portfolio_outcome_var.changeLabel(0, 'Strong_Loss'); portfolio_outcome_var.changeLabel(1, 'Minor_Loss'); portfolio_outcome_var.changeLabel(2, 'Neutral'); portfolio_outcome_var.changeLabel(3, 'Minor_Gain'); portfolio_outcome_var.changeLabel(4, 'Strong_Gain')
bn.add(portfolio_outcome_var)

# User Profile Node
risk_tolerance_var = gum.LabelizedVariable('Risk_Tol', 'Investor Risk Tolerance', 3)
risk_tolerance_var.changeLabel(0, 'Conservative'); risk_tolerance_var.changeLabel(1, 'Moderate'); risk_tolerance_var.changeLabel(2, 'Aggressive')
bn.add(risk_tolerance_var)

# --- DECISION AND UTILITY NODES ---
# Decision Node
invest_in_var = gum.LabelizedVariable('Invest_In', 'Investment Choice', 4)
invest_in_var.changeLabel(0, 'Stocks'); invest_in_var.changeLabel(1, 'Bonds'); invest_in_var.changeLabel(2, 'Crypto'); invest_in_var.changeLabel(3, 'Cash')
bn.addDecisionNode(invest_in_var)

# Utility Node
utility_var = gum.DiscretizedVariable('Utility', 'Portfolio Utility Score')
utility_var.addTick(-100); utility_var.addTick(100) # Define range
bn.addUtilityNode(utility_var)

# --- ADD ARCS (CAUSAL RELATIONSHIPS) ---
# Economic flow
bn.addArc('Inflation_Env', 'Interest_Rate')
# Economic factors -> Asset Performance
bn.addArc('GDP_Trend',     'Stock_Perf')
bn.addArc('Inflation_Env', 'Stock_Perf')
bn.addArc('Interest_Rate', 'Stock_Perf')
bn.addArc('Market_Vol',    'Stock_Perf')
bn.addArc('Inflation_Env', 'Bond_Perf')
bn.addArc('Interest_Rate', 'Bond_Perf')
bn.addArc('Market_Vol',    'Bond_Perf')
bn.addArc('Inflation_Env', 'Crypto_Perf')
bn.addArc('Interest_Rate', 'Crypto_Perf')
bn.addArc('Market_Vol',    'Crypto_Perf')
# Decision flow
bn.addArc('Invest_In',     'Portfolio_Out')
bn.addArc('Stock_Perf',    'Portfolio_Out')
bn.addArc('Bond_Perf',     'Portfolio_Out')
bn.addArc('Crypto_Perf',   'Portfolio_Out')
# Utility flow
bn.addArc('Portfolio_Out', 'Utility')
bn.addArc('Risk_Tol',      'Utility')

print("Structure created. Populating CPTs...")
# ===================================================================
#                      2. POPULATE ALL CPTS
# ===================================================================

# --- ROOT NODE PRIORS ---
# Based on expert forecasts for 2025-2026 from your report [cite: 220-227]
# GDP: High probability of 'Moderate' growth [cite: 225]
bn.cpt('GDP_Trend')[:] = [0.10, 0.20, 0.60, 0.10] # P(Recession, Stagnant, Moderate, Strong)
# Inflation: Split between 'Low' and 'High' [cite: 226]
bn.cpt('Inflation_Env')[:] = [0.05, 0.45, 0.50] # P(Deflationary, Low, High)
# Market Volatility: Assume 'Normal' is most likely
bn.cpt('Market_Vol')[:] = [0.20, 0.60, 0.20] # P(Low, Normal, High)
# Risk Tolerance: Assume uniform distribution until user specifies
bn.cpt('Risk_Tol')[:] = [1/3, 1/3, 1/3]

# --- CONDITIONAL PROBABILITY TABLES ---
# Interest Rate Trajectory CPT (dependent on Inflation)
# Logically filling based on central bank reaction function 
bn.cpt('Interest_Rate')[{'Inflation_Env': 'Deflationary'}] = [0.70, 0.25, 0.05] # Cutting, Holding, Hiking
bn.cpt('Interest_Rate')[{'Inflation_Env': 'Low'}]          = [0.15, 0.70, 0.15]
bn.cpt('Interest_Rate')[{'Inflation_Env': 'High'}]         = [0.05, 0.25, 0.70]

# Asset Performance CPTs (using examples from your report's CPT table) [cite: 250]
# Filling with a default, then overriding specific, important cases.
default_dist = [0.20, 0.20, 0.20, 0.20, 0.20] # Uniform default
# Stock Performance
default_stock_dist = [0.15, 0.20, 0.30, 0.25, 0.10]
num_stock_parent_combos = 108
bn.cpt('Stock_Perf').fillWith(default_stock_dist * num_stock_parent_combos)
bn.cpt('Stock_Perf')[{'GDP_Trend':'Strong', 'Inflation_Env':'Low', 'Interest_Rate':'Holding', 'Market_Vol':'Low'}] = [0.01, 0.04, 0.10, 0.35, 0.50]
bn.cpt('Stock_Perf')[{'GDP_Trend':'Stagnant', 'Inflation_Env':'High', 'Interest_Rate':'Hiking', 'Market_Vol':'High'}] = [0.40, 0.30, 0.20, 0.08, 0.02]
bn.cpt('Stock_Perf')[{'GDP_Trend':'Recession', 'Inflation_Env':'Low', 'Interest_Rate':'Cutting', 'Market_Vol':'High'}] = [0.50, 0.25, 0.15, 0.07, 0.03]
# Bond Performance
num_bond_parent_combos = 27
default_bond_dist = [0.15, 0.20, 0.30, 0.25, 0.10]
bn.cpt('Bond_Perf').fillWith(default_bond_dist * num_bond_parent_combos)
bn.cpt('Bond_Perf')[{'Inflation_Env': 'High', 'Interest_Rate': 'Hiking', 'Market_Vol': 'Normal'}] = [0.60, 0.25, 0.10, 0.05, 0.00]
bn.cpt('Bond_Perf')[{'Inflation_Env': 'Low', 'Interest_Rate': 'Cutting', 'Market_Vol': 'High'}] = [0.01, 0.04, 0.15, 0.40, 0.40] # Flight to safety
# Crypto Performance
num_crypto_parent_combos = 27
default_crypto_dist = [0.20, 0.25, 0.30, 0.15, 0.10]
bn.cpt('Crypto_Perf').fillWith(default_crypto_dist * num_crypto_parent_combos)
bn.cpt('Crypto_Perf')[{'Inflation_Env': 'High', 'Interest_Rate': 'Hiking', 'Market_Vol': 'High'}] = [0.45, 0.30, 0.15, 0.08, 0.02]
bn.cpt('Crypto_Perf')[{'Inflation_Env': 'Low', 'Interest_Rate': 'Cutting', 'Market_Vol': 'Low'}] = [0.05, 0.10, 0.20, 0.30, 0.35]

# Portfolio Outcome CPT (Multiplexer Logic)
# The outcome of the portfolio deterministically follows the chosen asset class.
po_cpt = bn.cpt('Portfolio_Out')
for stock_label in bn.variable('Stock_Perf').labels():
    for bond_label in bn.variable('Bond_Perf').labels():
        for crypto_label in bn.variable('Crypto_Perf').labels():
            for decision_label in bn.variable('Invest_In').labels():
                # Default for 'Cash' is always 'Neutral'
                outcome_dist = [0.0, 0.0, 1.0, 0.0, 0.0]
                if decision_label == 'Stocks':
                    outcome_dist = [1.0 if l == stock_label else 0.0 for l in bn.variable('Portfolio_Out').labels()]
                elif decision_label == 'Bonds':
                    outcome_dist = [1.0 if l == bond_label else 0.0 for l in bn.variable('Portfolio_Out').labels()]
                elif decision_label == 'Crypto':
                    outcome_dist = [1.0 if l == crypto_label else 0.0 for l in bn.variable('Portfolio_Out').labels()]
                po_cpt[{'Stock_Perf': stock_label, 'Bond_Perf': bond_label, 'Crypto_Perf': crypto_label, 'Invest_In': decision_label}] = outcome_dist

# --- UTILITY TABLE ---
# Based on the utility matrix from your report [cite: 280]
utility_table = bn.utility('Utility')
utility_matrix = {
    'Strong_Loss': [-100, -50, -25], 'Minor_Loss':  [-50,  -20, -5],
    'Neutral':     [5,    0,   0],   'Minor_Gain':  [20,   25,  20],
    'Strong_Gain': [40,   60,  100]
}
for i, outcome_label in enumerate(bn.variable('Portfolio_Out').labels()):
    for j, risk_label in enumerate(bn.variable('Risk_Tol').labels()):
        utility_table[{'Portfolio_Out': outcome_label, 'Risk_Tol': risk_label}] = utility_matrix[outcome_label][j]

print("Model is complete and ready for inference.")
# ===================================================================
#                      3. PERFORM DECISION INFERENCE
# ===================================================================

# Add information arcs to the decision node
print("\nAdding information arcs to the decision node...")
bn.addArc('GDP_Trend', 'Invest_In')
bn.addArc('Inflation_Env', 'Invest_In')
bn.addArc('Interest_Rate', 'Invest_In')
bn.addArc('Market_Vol', 'Invest_In')
print("Information arcs added.")

# Create an Inference Engine
ie = gum.ShaferShenoyLIMIDInference(bn)

# --- SCENARIO 1: STAGFLATION (Moderate Investor) ---
# As described in your report [cite: 588]
ie.eraseAllEvidence()
ie.setEvidence({'GDP_Trend': 'Stagnant', 'Inflation_Env': 'High', 'Risk_Tol': 'Moderate'})

print("\n" + "="*60)
print("DECISION ANALYSIS: SCENARIO 1 - STAGFLATION")
print("="*60)
print("\nScenario Evidence: Stagnant GDP, High Inflation")
print("Investor Profile: Moderate")

ie.makeInference()
utilities_stagflation = ie.posteriorUtility('Invest_In')

# -- A more efficient way to find the best action --
labels = bn.variable('Invest_In').labels()
values = utilities_stagflation.tolist()
utility_map = dict(zip(labels, values))
recommended_action_stagflation = max(utility_map, key=utility_map.get)

max_expected_utility_stagflation = ie.MEU()['mean']


print(f"\nRecommended Action: Invest in '{recommended_action_stagflation}'")
print(f"Maximum Expected Utility (MEU): {max_expected_utility_stagflation:.4f}")
print("\nExpected Utilities for all choices:\n", utilities_stagflation)

# --- SCENARIO 2: GOLDILOCKS (Moderate Investor) ---
# As described in your report [cite: 603]
ie.eraseAllEvidence()
ie.setEvidence({'GDP_Trend': 'Strong', 'Inflation_Env': 'Low', 'Risk_Tol': 'Moderate'})

print("\n" + "="*60)
print("DECISION ANALYSIS: SCENARIO 2 - GOLDILOCKS")
print("="*60)
print("\nScenario Evidence: Strong GDP, Low Inflation")
print("Investor Profile: Moderate")

ie.makeInference()
utilities_goldilocks = ie.posteriorUtility('Invest_In')

# -- A more efficient way to find the best action --
labels = bn.variable('Invest_In').labels()
values = utilities_goldilocks.tolist()
utility_map = dict(zip(labels, values))
recommended_action_goldilocks = max(utility_map, key=utility_map.get)

max_expected_utility_goldilocks = ie.MEU()['mean']

print(f"\nRecommended Action: Invest in '{recommended_action_goldilocks}'")
print(f"Maximum Expected Utility (MEU): {max_expected_utility_goldilocks:.4f}")
print("\nExpected Utilities for all choices:\n", utilities_goldilocks)

# ===================================================================
#                      4. VISUALIZE THE MODEL
# ===================================================================

print("\n" + "="*60)
print("VISUALIZATIONS")
print("="*60)

# 1. Show network structure
print("\nDisplaying network structure...")
gnb.showInfluenceDiagram(bn, size="30")
gumimage.export(bn,"test_output.png")


