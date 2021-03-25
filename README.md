# FantasyBasketballAuctionDraftSimulation
Python script simulating different formats that are used in Fantasy Basketball. 

# Simulations 
[data2.xlsx](https://github.com/WilliamZhai/FantasyBasketballAuctionDraftSimulation/blob/main/data2.xlsx) includes simulation samples of a traditional snake draft format in contrast to budget auction formats.

### Generating the valuations of items

- Common values are gernerated from a gamma distribution with input ***Γ*** and ***scale***.
- Private values are generated from a uniformed distribution with input ***a*** and ***b***.
- Their sum will represent the overall **valuation** of a bidder for an item.
- The input values are currently set to their default values but feel free to modify them for your uses.

### There are 30 sheets each with a sample simulation
- sim 1-10:
    - number of bidders = 2
    - number of items = 10
- sim 11-20:
    - number of bidders = 4
    - number of items = 24
- sim 21-30:
    - number of bidders = 8
    - number of items = 64

- Each simulation showcases different resulting **utilty** for the bidders.
