Excellent! Getting the model to run is a major milestone. Congratulations!

You've correctly identified the next big question: what to do with the `Portfolio_Out` node.

Right now, it's a disconnected root node, which means its probabilities are static and don't react to changes in the economy or individual asset performances. To make it useful, we need to reconnect it to the network.

You have two main paths forward:

1.  **The Simple Path (Good for Analysis):** Define the portfolio outcome using a simplified, programmatic CPT. This is great for understanding the network's behavior.
2.  **The Advanced Path (Best for Decision-Making):** Convert the model into a proper **Influence Diagram** (also known as a Decision Network). This is the most powerful approach and the true purpose of this kind of model.

Let's start with the simple path to get it working, and then I'll explain the advanced path.

---

### Path 1: The Simple, Programmatic CPT

The core challenge is that the CPT for `Portfolio_Out` is enormous (5x5x5 parent states = 125 combinations). We cannot manually write it out. Instead, we can create a function to calculate the outcome based on the parent states.

A logical way to do this is to assign a numerical score to each performance level and calculate a weighted average.

**Step 1: Re-enable the Arcs**

First, uncomment the arcs you previously commented out so the dependency is restored.

```python
# Asset performances influence portfolio outcome
bn.addArc('Stock_Perf', 'Portfolio_Out')
bn.addArc('Bond_Perf', 'Portfolio_Out')
bn.addArc('Crypto_Perf', 'Portfolio_Out')
```

**Step 2: Programmatically Fill the CPT**

Now, instead of using a simple `.fillWith()`, we will loop through every possible scenario and calculate the resulting portfolio distribution.

Here is the code to do it. You can replace your old `po_cpt` section with this:

```python
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
```

**What this code does:**
1.  It assigns a numerical score to each performance level (e.g., 'Strong_Gain' = 2).
2.  It defines a sample portfolio allocation (60/30/10). **You can change these weights!**
3.  It loops through all 125 parent combinations.
4.  In each loop, it calculates the portfolio's total score based on the weights.
5.  It uses a set of `if/elif/else` statements to convert that score into a probability distribution for the `Portfolio_Out` node.
6.  Finally, it assigns that distribution to the specific scenario in the CPT.

Your model will now be fully connected and runnable! You can perform inference and see how, for example, a "Recession" in `GDP_Trend` flows all the way through to affect the `Portfolio_Out`.

---

### Path 2: The Advanced (and more powerful) Path

The code above has a hard-coded assumption: the 60/30/10 asset allocation. But the whole point of a model like this is to help you *choose* the best allocation.

This is where you transform your Bayesian Network into an **Influence Diagram**. You do this by adding **Decision Nodes** and **Utility Nodes**.

*   **Decision Node (`Allocation_Choice`):** This node wouldn't have probabilities. Instead, it represents a choice you can make. Its states could be 'Conservative' (e.g., 10% stocks, 70% bonds, 0% crypto), 'Balanced' (60/30/10), and 'Aggressive' (80/10/10).
*   **Utility Node (`Portfolio_Value`):** This node represents the ultimate goal. It doesn't have probabilities, but rather a "value" or "utility" for each possible outcome. For example, a Strong Gain might have a utility of +100, while a Strong Loss has a utility of -150. The goal of the diagram is to find the choice in the Decision Node that maximizes the expected utility.

Your `Portfolio_Out` node's CPT would then be conditioned on **both** the asset performances *and* the `Allocation_Choice` decision node.

This is a more advanced topic, but it's the natural next step for this model. For now, **I strongly recommend implementing Path 1 successfully.** Once you have that working and can perform inference on it, you will be in a great position to explore turning it into a full-fledged decision network.

Excellent question! Now that your Bayesian network is fully specified, you can start asking it questions. This process is called inference.

Inference allows you to calculate the updated probabilities of certain events, given that you have observed other events (this is called "setting evidence").

Let's say you want to answer the question:

"If we enter a High Inflation environment and the market becomes Highly Volatile, what is the most likely outcome for my portfolio?"

Here’s how you do that using pyagrum. Add this code to the end of your script.

Performing Inference: A Step-by-Step Guide

The process is always the same:

Create an "inference engine" for your network.

Set the evidence you have observed.

Make a query to get the new probabilities for your target node.

Here is the complete code to add to your script:

code
Python
download
content_copy
expand_less
# ===================================================================
#                      PERFORMING INFERENCE
# ===================================================================

# 1. Create an Inference Engine
# Using the LazyPropagation engine is a good general-purpose choice.
ie = gum.LazyPropagation(bn)

# 2. Set Evidence
# Let's define a scenario: High Inflation and High Market Volatility.
# The evidence is set using a dictionary where keys are node names
# and values are the observed states (as strings).
ie.setEvidence({'Inflation_Env': 'High', 'Market_Vol': 'High'})

# You can also set evidence on multiple nodes at once
# ie.setEvidence({'GDP_Trend': 'Recession', 'Interest_Rate': 'Hiking'})

# 3. Make a Query
# We want to know the new probability distribution for 'Portfolio_Out'.
ie.makeInference()
posterior_portfolio = ie.posterior('Portfolio_Out')

# 4. Display the Results
print("\n" + "="*60)
print("INFERENCE RESULTS")
print("="*60)
print("\nScenario (Evidence): High Inflation, High Market Volatility")
print("\nPosterior probability of Portfolio Outcome:")
print(posterior_portfolio)

# The result is an object, you can access specific probabilities
print(f"\nProbability of a Strong Loss: {posterior_portfolio['Strong_Loss']:.2%}")
print(f"Probability of a Strong Gain: {posterior_portfolio['Strong_Gain']:.2%}")


# ===================================================================
#         ANOTHER COMMON QUERY: MOST PROBABLE EXPLANATION (MPE)
# ===================================================================
# MPE finds the most likely state for *all* unobserved variables.

# We'll use the same evidence as before.
# ie.setEvidence({'Inflation_Env': 'High', 'Market_Vol': 'High'}) # Already set from before
ie.makeInference()
mpe_scenario = ie.MPE()

print("\n" + "="*60)
print("MOST PROBABLE EXPLANATION (MPE)")
print("="*60)
print("\nGiven High Inflation and High Volatility, the most likely overall scenario is:")

# The MPE result is a dictionary of node IDs and their state indices.
# We need to look up the names and labels to make it readable.
for nodeId, state_index in mpe_scenario.items():
    nodeName = bn.variable(nodeId).name()
    stateLabel = bn.variable(nodeId).label(state_index)
    # We only care about the variables that weren't part of our evidence
    if nodeName not in ['Inflation_Env', 'Market_Vol']:
        print(f"- {nodeName}: {stateLabel}")
How to Interpret the Output

When you run this new code, you will see output like this (the exact numbers will depend on your CPTs):

code
Code
download
content_copy
expand_less
============================================================
INFERENCE RESULTS
============================================================

Scenario (Evidence): High Inflation, High Market Volatility

Posterior probability of Portfolio Outcome:
<Strong_Loss:0.35, Minor_Loss:0.38, Neutral:0.20, Minor_Gain:0.06, Strong_Gain:0.01>

Probability of a Strong Loss: 35.00%
Probability of a Strong Gain: 1.00%

============================================================
MOST PROBABLE EXPLANATION (MPE)
============================================================

Given High Inflation and High Volatility, the most likely overall scenario is:
- GDP_Trend: Moderate
- Interest_Rate: Hiking
- Stock_Perf: Minor_Loss
- Bond_Perf: Strong_Loss
- Crypto_Perf: Strong_Loss
- Risk_Tol: Moderate
- Portfolio_Out: Minor_Loss

This tells you:

Posterior Probability: Under these adverse conditions, the probability of having a Strong_Loss or Minor_Loss is now very high, and the chance of a gain is very low. This is the updated belief based on the evidence.

MPE: The single most likely chain of events is that the central bank will be Hiking rates, all asset classes will perform poorly (especially bonds and crypto), and your portfolio will suffer a Minor_Loss.

You can now experiment by changing the evidence in the ie.setEvidence({...}) line to analyze any scenario you can imagine