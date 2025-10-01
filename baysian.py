import os
import pyagrum as gum
import pyagrum.lib.notebook as gnb
import pyagrum.lib.image as gumimage

# Create the Bayesian Network
bn = gum.BayesNet('Strategic Asset Allocation Network')

# Create the variable, add it to the network, and then get the object back to modify it.
'''bn.add(gum.LabelizedVariable('GDP_Trend', 'GDP Trend', 4))
gdp = bn.variable('GDP_Trend') # Get the variable object by its name
gdp.changeLabel(0, 'Recession')
gdp.changeLabel(1, 'Stagnant')
gdp.changeLabel(2, 'Moderate')
gdp.changeLabel(3, 'Strong')
'''

# 1. Create the LabelizedVariable object
gdp_var = gum.LabelizedVariable('GDP_Trend', 'GDP Trend', 4)

# 2. Modify the object by changing its labels
gdp_var.changeLabel(0, 'Recession')
gdp_var.changeLabel(1, 'Stagnant')
gdp_var.changeLabel(2, 'Moderate')
gdp_var.changeLabel(3, 'Strong')

# 3. Add the fully configured variable to the network
bn.add(gdp_var)

inflation = gum.LabelizedVariable('Inflation_Env', 'Inflation Environment', 3)

#inflation = bn.variable('Inflation_Env') # Get the variable object
inflation.changeLabel(0, 'Deflationary')
inflation.changeLabel(1, 'Low')
inflation.changeLabel(2, 'High')

bn.add(inflation)

# Endogenous factors - Interest Rate
interest_rate = gum.LabelizedVariable('Interest_Rate', 'Interest Rate Trajectory', 3)

#interest_rate = bn.variable('Interest_Rate')  # Get the variable object
interest_rate.changeLabel(0, 'Cutting')
interest_rate.changeLabel(1, 'Holding')
interest_rate.changeLabel(2, 'Hiking')

bn.add(interest_rate)

# Endogenous factors - Market Volatility
volatility = gum.LabelizedVariable('Market_Vol', 'Market Volatility', 3)

#volatility = bn.variable('Market_Vol')  # Get the variable object
volatility.changeLabel(0, 'Low')
volatility.changeLabel(1, 'Normal')
volatility.changeLabel(2, 'High')

bn.add(volatility)

# Asset performance nodes - Stock Performance
stock_perf = gum.LabelizedVariable('Stock_Perf', 'Stock Performance', 5)

#stock_perf = bn.variable('Stock_Perf')  # Get the variable object
stock_perf.changeLabel(0, 'Strong_Loss')
stock_perf.changeLabel(1, 'Minor_Loss')
stock_perf.changeLabel(2, 'Neutral')
stock_perf.changeLabel(3, 'Minor_Gain')
stock_perf.changeLabel(4, 'Strong_Gain')

bn.add(stock_perf)

# Asset performance nodes - Bond Performance
bond_perf = gum.LabelizedVariable('Bond_Perf', 'Bond Performance', 5)

#bond_perf = bn.variable('Bond_Perf')  # Get the variable object
bond_perf.changeLabel(0, 'Strong_Loss')
bond_perf.changeLabel(1, 'Minor_Loss')
bond_perf.changeLabel(2, 'Neutral')
bond_perf.changeLabel(3, 'Minor_Gain')
bond_perf.changeLabel(4, 'Strong_Gain')

bn.add(bond_perf)

# Asset performance nodes - Crypto Performance
crypto_perf = gum.LabelizedVariable('Crypto_Perf', 'Crypto Performance', 5)

#crypto_perf = bn.variable('Crypto_Perf')  # Get the variable object
crypto_perf.changeLabel(0, 'Strong_Loss')
crypto_perf.changeLabel(1, 'Minor_Loss')
crypto_perf.changeLabel(2, 'Neutral')
crypto_perf.changeLabel(3, 'Minor_Gain')
crypto_perf.changeLabel(4, 'Strong_Gain')

bn.add(crypto_perf)

# Risk tolerance node
risk_tolerance = gum.LabelizedVariable('Risk_Tol', 'Investor Risk Tolerance', 3)

#risk_tolerance = bn.variable('Risk_Tol')  # Get the variable object
risk_tolerance.changeLabel(0, 'Conservative')
risk_tolerance.changeLabel(1, 'Moderate')
risk_tolerance.changeLabel(2, 'Aggressive')

bn.add(risk_tolerance)

# Portfolio outcome node
portfolio_outcome = gum.LabelizedVariable('Portfolio_Out', 'Portfolio Outcome', 5)

#portfolio_outcome = bn.variable('Portfolio_Out')  # Get the variable object
portfolio_outcome.changeLabel(0, 'Strong_Loss')
portfolio_outcome.changeLabel(1, 'Minor_Loss')
portfolio_outcome.changeLabel(2, 'Neutral')
portfolio_outcome.changeLabel(3, 'Minor_Gain')
portfolio_outcome.changeLabel(4, 'Strong_Gain')

# Add arcs (causal relationships)
bn.add(portfolio_outcome)

# Inflation influences interest rates
bn.addArc('Inflation_Env', 'Interest_Rate')

# Economic factors influence stock performance
bn.addArc('GDP_Trend', 'Stock_Perf')
bn.addArc('Inflation_Env', 'Stock_Perf')
bn.addArc('Interest_Rate', 'Stock_Perf')
bn.addArc('Market_Vol', 'Stock_Perf')

# Factors influence bond performance
bn.addArc('Inflation_Env', 'Bond_Perf')
bn.addArc('Interest_Rate', 'Bond_Perf')
bn.addArc('Market_Vol', 'Bond_Perf')

# Factors influence crypto performance
bn.addArc('Inflation_Env', 'Crypto_Perf')
bn.addArc('Interest_Rate', 'Crypto_Perf')
bn.addArc('Market_Vol', 'Crypto_Perf')

# Asset performances influence portfolio outcome
bn.addArc('Stock_Perf', 'Portfolio_Out')
bn.addArc('Bond_Perf', 'Portfolio_Out')
bn.addArc('Crypto_Perf', 'Portfolio_Out')

print("Network Structure Created")
print(f"Number of nodes: {bn.size()}")
print(f"Number of arcs: {bn.sizeArcs()}")\

# ===================================================================
#                      VISUALIZE THE BAYESIAN NETWORK
# ===================================================================
gumimage.export(bn,"test_output.png")


# --- Corrected CPT for Bond Performance ---
bond_cpt = bn.cpt('Bond_Perf')
# Calculate parent combinations: Interest_Rate(3) * Inflation_Env(3) * Market_Vol(3) = 27
num_bond_parent_combos = 27
default_bond_dist = [0.15, 0.20, 0.30, 0.25, 0.10]

# FIRST, explicitly create the full list of 135 values and fill the table
bond_cpt.fillWith(default_bond_dist * num_bond_parent_combos)

# SECOND, override the specific combinations you care about
bond_cpt[{'Interest_Rate': 'Cutting', 'Inflation_Env': 'Low', 'Market_Vol': 'Low'}] = \
    [0.02, 0.08, 0.20, 0.50, 0.20]
bond_cpt[{'Interest_Rate': 'Hiking', 'Inflation_Env': 'High', 'Market_Vol': 'High'}] = \
    [0.60, 0.25, 0.10, 0.04, 0.01]

# --- Corrected CPT for Stock Performance ---
stock_cpt = bn.cpt('Stock_Perf')
# Calculate parent combinations: GDP_Trend(4) * Inflation_Env(3) * Interest_Rate(3) * Market_Vol(3) = 108
num_stock_parent_combos = 108
default_stock_dist = [0.15, 0.20, 0.30, 0.25, 0.10]

# FIRST, fill the entire table (108 * 5 = 540 values)
stock_cpt.fillWith(default_stock_dist * num_stock_parent_combos)

# SECOND, override specific cases
stock_cpt[{'GDP_Trend': 'Strong', 'Inflation_Env': 'Low', 'Interest_Rate': 'Holding', 'Market_Vol': 'Low'}] = \
    [0.01, 0.04, 0.10, 0.35, 0.50]
stock_cpt[{'GDP_Trend': 'Recession', 'Inflation_Env': 'High', 'Interest_Rate': 'Hiking', 'Market_Vol': 'High'}] = \
    [0.50, 0.30, 0.12, 0.06, 0.02]


# --- Corrected CPT for Crypto Performance ---
crypto_cpt = bn.cpt('Crypto_Perf')
# Calculate parent combinations: Inflation_Env(3) * Interest_Rate(3) * Market_Vol(3) = 27
num_crypto_parent_combos = 27
default_crypto_dist = [0.20, 0.25, 0.30, 0.15, 0.10]

# FIRST, fill the entire table (27 * 5 = 135 values)
crypto_cpt.fillWith(default_crypto_dist * num_crypto_parent_combos)

# SECOND, override specific cases
crypto_cpt[{'Inflation_Env': 'High', 'Interest_Rate': 'Hiking', 'Market_Vol': 'High'}] = \
    [0.45, 0.30, 0.15, 0.08, 0.02]
crypto_cpt[{'Inflation_Env': 'Low', 'Interest_Rate': 'Cutting', 'Market_Vol': 'Low'}] = \
    [0.05, 0.10, 0.20, 0.30, 0.35]

# --- Portfolio Outcome CPT ---
# IMPORTANT: As predicted in my last message, this node will cause the next error.
# For now, you MUST simplify the model to get it running.
# Comment out the arcs leading to Portfolio_Out in the "Add arcs" section.
# e.g., # bn.addArc('Stock_Perf', 'Portfolio_Out')
po_cpt = bn.cpt('Portfolio_Out')
num_po_parent_combos = 125
default_po_dist = [0.15, 0.20, 0.30, 0.25, 0.10]

po_cpt.fillWith(default_po_dist * num_po_parent_combos)

'''# Set prior probabilities for root nodes
# GDP Trend priors (based on expert forecasts)
bn.cpt('GDP_Trend').fillWith([0.10, 0.15, 0.60, 0.15])  # [Recession, Stagnant, Moderate, Strong]

# Inflation Environment priors
bn.cpt('Inflation_Env').fillWith([0.05, 0.50, 0.45])  # [Deflationary, Low, High]

# Market Volatility priors
bn.cpt('Market_Vol').fillWith([0.30, 0.50, 0.20])  # [Low, Normal, High]

# Risk Tolerance priors (uniform - user will set evidence)
bn.cpt('Risk_Tol').fillWith([0.33, 0.34, 0.33])  # [Conservative, Moderate, Aggressive]

# Example CPT for Interest Rate Trajectory (conditional on Inflation)
# Format: [Cutting, Holding, Hiking] for each inflation state
ir_cpt = bn.cpt('Interest_Rate')
# Deflationary
ir_cpt[{'Inflation_Env': 'Deflationary'}] = [0.70, 0.25, 0.05]
# Low
ir_cpt[{'Inflation_Env': 'Low'}] = [0.30, 0.50, 0.20]
# High
ir_cpt[{'Inflation_Env': 'High'}] = [0.05, 0.15, 0.80]

# Example CPT for Bond Performance (based on Table 1 from document)
# Simplified version - full implementation would include all combinations
bond_cpt = bn.cpt('Bond_Perf')

# Fill remaining combinations with default values
bond_cpt.fillWith([0.15, 0.20, 0.30, 0.25, 0.10])

# Example: Cutting rates with Low inflation
bond_cpt[{'Interest_Rate': 'Cutting', 'Inflation_Env': 'Low', 'Market_Vol': 'Low'}] = \
    [0.02, 0.08, 0.20, 0.50, 0.20]  # [Strong Loss, Minor Loss, Neutral, Minor Gain, Strong Gain]

# Example: Hiking rates with High inflation
bond_cpt[{'Interest_Rate': 'Hiking', 'Inflation_Env': 'High', 'Market_Vol': 'High'}] = \
    [0.60, 0.25, 0.10, 0.04, 0.01]



# Example CPT for Stock Performance
stock_cpt = bn.cpt('Stock_Perf')

# Fill remaining with default values
stock_cpt.fillWith([0.15, 0.20, 0.30, 0.25, 0.10])

# Strong economy, low inflation, holding rates, low volatility
stock_cpt[{'GDP_Trend': 'Strong', 'Inflation_Env': 'Low', 'Interest_Rate': 'Holding', 'Market_Vol': 'Low'}] = \
    [0.01, 0.04, 0.10, 0.35, 0.50]

# Recession, high inflation, hiking rates, high volatility
stock_cpt[{'GDP_Trend': 'Recession', 'Inflation_Env': 'High', 'Interest_Rate': 'Hiking', 'Market_Vol': 'High'}] = \
    [0.50, 0.30, 0.12, 0.06, 0.02]



# Example CPT for Crypto Performance
crypto_cpt = bn.cpt('Crypto_Perf')

crypto_cpt.fillWith([0.20, 0.25, 0.30, 0.15, 0.10])

# High volatility generally bad for crypto
crypto_cpt[{'Inflation_Env': 'High', 'Interest_Rate': 'Hiking', 'Market_Vol': 'High'}] = \
    [0.45, 0.30, 0.15, 0.08, 0.02]

# Low volatility, cutting rates can be good for crypto
crypto_cpt[{'Inflation_Env': 'Low', 'Interest_Rate': 'Cutting', 'Market_Vol': 'Low'}] = \
    [0.05, 0.10, 0.20, 0.30, 0.35]


# Portfolio Outcome CPT (simplified - would depend on investment choice in full model)
po_cpt = bn.cpt('Portfolio_Out')
# This is a simplified aggregation - in full decision network would be conditioned on choice
po_cpt.fillWith([0.15, 0.20, 0.30, 0.25, 0.10])'''

print("\nCPTs populated with example probabilities")
print("\nNetwork ready for inference!")

# Display network structure
print("\n" + "="*60)
print("NETWORK NODES:")
print("="*60)
for node in bn.names():
    print(f"- {node}: {bn.variable(node).labels()}")

print("\n" + "="*60)
print("NETWORK ARCS (Causal Relationships):")
print("="*60)
for arc in bn.arcs():
    parent = bn.variable(arc[0]).name()
    child = bn.variable(arc[1]).name()
    print(f"{parent} → {child}")

print("\nCalculating CPT for Portfolio_Out...")

po_cpt = bn.cpt('Portfolio_Out')

# Define a scoring system for outcomes
# Strong_Loss=-2, Minor_Loss=-1, Neutral=0, Minor_Gain=1, Strong_Gain=2
scores = [-2, -1, 0, 1, 2]
score_map = {label: score for label, score in zip(stock_perf.labels(), scores)}

# Define portfolio weights (e.g., 60% stocks, 30% bonds, 10% crypto)
weights = {'Stock_Perf': 0.60, 'Bond_Perf': 0.30, 'Crypto_Perf': 0.10}

# Iterate through every possible combination of parent states
for stock_label in stock_perf.labels():
    for bond_label in bond_perf.labels():
        for crypto_label in crypto_perf.labels():
            # Calculate the weighted average score for this scenario
            weighted_score = (score_map[stock_label] * weights['Stock_Perf'] +
                              score_map[bond_label] * weights['Bond_Perf'] +
                              score_map[crypto_label] * weights['Crypto_Perf'])

            # Determine the most likely portfolio outcome based on the score
            # This is a simple mapping. A more complex model could create a distribution.
            if weighted_score > 1.25:
                # Strong Gain
                outcome_dist = [0.0, 0.0, 0.1, 0.3, 0.6]
            elif weighted_score > 0.5:
                # Minor Gain
                outcome_dist = [0.0, 0.1, 0.3, 0.5, 0.1]
            elif weighted_score > -0.5:
                # Neutral
                outcome_dist = [0.1, 0.2, 0.4, 0.2, 0.1]
            elif weighted_score > -1.25:
                # Minor Loss
                outcome_dist = [0.1, 0.5, 0.3, 0.1, 0.0]
            else:
                # Strong Loss
                outcome_dist = [0.6, 0.3, 0.1, 0.0, 0.0]

            # Set the probability distribution for this specific scenario
            po_cpt[{'Stock_Perf': stock_label, 'Bond_Perf': bond_label, 'Crypto_Perf': crypto_label}] = outcome_dist

print("Portfolio_Out CPT populated.")

