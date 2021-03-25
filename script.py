import numpy
import xlsxwriter
import copy

# create file for simulations
workbook = xlsxwriter.Workbook("data.xlsx")

# globals
upperline = workbook.add_format(
    {
        "top": 1,
    }
)

header_border = workbook.add_format(
    {
        "bottom": 1,
    }
)

# snake draft order
def get_draft_order(num_drafter, num_rounds):
    order = []
    direction = 1

    i = 0
    while i < num_rounds / num_drafter:
        if direction % 2 == 1:
            for j in range(num_drafter):
                order.append(j)
        else:
            for j in range(num_drafter - 1, -1, -1):
                order.append(j)

        direction += 1
        i += 1
    return order

# set auction order
def set_auction_order(bidders_valuation_copy):
    item_valuation_tuples = []

    for i in range(len(bidders_valuation_copy[0])):
        item_sum = 0
        for j in range(len(bidders_valuation_copy)):
            item_sum += bidders_valuation_copy[j][i]
        item_valuation_tuples.append((item_sum, i))

    # order it
    item_valuation_tuples.sort(key=lambda x: x[0])

    res = []
    for tup in item_valuation_tuples:
        res.append(tup[1])

    return res

# calculate winner for second price auction 
def get_winner_second_price_auctiion(bids):
    second_highest = 1
    highest = bids[0]
    winner = 0

    for i in range(1, len(bids)):
        if bids[i] > highest:
            second_highest = highest
            highest = bids[i]
            winner = i
        elif bids[i] > second_highest:
            second_highest = bids[i]
        

    # print("bidding round", bids)
    # print("    winner", winner + 1)
    # print("    price", second_highest)
    return [winner, second_highest]

# create 1 worksheet for a simluation
def create_sheet(sheet_name, num_bidder, num_item, gamma_input=3, gamma_scale=10, uniform_left=0, uniform_right=6):
    
    # =============================================== setup worksheet ===============================================
    sheet = workbook.add_worksheet(sheet_name)
    sheet.set_column(0, 0, 40)

    sheet.write(0, 0, "SIMULATION INPUTS", header_border)
    for i in range(1, num_item + 1):
        sheet.write(0, i, "", header_border)
    
    sheet.write(1, 0, "number of bidders = " + str(num_bidder))
    sheet.write(1, 1, "number of items = " + str(num_item))
    sheet.write(1, 4, "common value: gamma distribution Γ = " + str(gamma_input) + " and scale = " + str(gamma_scale))
    sheet.write(1, 10, "private value: uniform distribution ~ [" + str(uniform_left) + "," + str(uniform_right) + "]")

    row_start = 3

    sheet.write(row_start, 0, "PLAYER VALUATIONS GENERATED", header_border)
    for i in range(1, num_item + 1):
        sheet.write(row_start, i, "", header_border)
    sheet.write(row_start + 1, 0, "Items")
    
    row_start += 2
    # we will generate the common value component of each item with Γ = 3 (default)
    # a smaller gamma  will indicate a more positive(right) skewed distribution
    # for examples see https://homepage.divms.uiowa.edu/~mbognar/applets/pois.html 
    common_values = []
    for i in range(num_item):
        common_values.append(int(numpy.random.gamma(gamma_input, gamma_scale)))    
        
    # for each bidder, we will generate the private value component of each item 
    # using a uniform distribution between a and b (default a=0, b=6)
    private_values = [ [] for _ in range(num_bidder) ]
    for i in range(num_bidder):
        for j in range(num_item):
            private_values[i].append(int(numpy.random.uniform(uniform_left, uniform_right)))

    # write to workbook the common values 
    sheet.write(row_start, 0, "Common Values")
    for x in range(num_item):
        sheet.write(row_start - 1, x + 1, "item" + str(x+1))
        sheet.write(row_start, x + 1, common_values[x])

    row_start = row_start + 2
    # write to workbook the private values 
    for y in range(num_bidder):
        sheet.write(row_start + y, 0, "bidder" + str(y + 1) + " private values")
        for x in range(num_item):
            sheet.write(row_start + y, x + 1, private_values[y][x])
    
    # write the overall valuation of bidders and items
    row_start += num_bidder + 1

    for y in range(num_bidder):
        sheet.write(row_start + y, 0, "bidder" + str(y + 1) + " total valuation")

        for x in range(num_item):
            sheet.write(row_start + y, x + 1, private_values[y][x] + common_values[x])
    
    row_start += num_bidder

    # =============================================== a snake draft fomat ===============================================
    row_start = row_start + 1

    sheet.write(row_start, 0, "SNAKE DRAFT RESULT", header_border)
    for i in range(1, num_item + 1):
        sheet.write(row_start, i, "", header_border)

    # setup
    bidder_items = [ [] for _ in range(num_bidder) ]
    bidders_valuation_copy = copy.deepcopy(private_values)
    for y in range(num_bidder):
        for x in range(num_item):
            bidders_valuation_copy[y][x] = bidders_valuation_copy[y][x] + common_values[x]

    # compute each round
    row_start = row_start + 2
    drafter_order = get_draft_order(num_bidder, num_item)
    for bidder_index in (drafter_order):

        item = max(bidders_valuation_copy[bidder_index]) # highest value item for bidder i
        index = bidders_valuation_copy[bidder_index].index(item) # index of that item

        bidder_items[bidder_index].append(item) # add item to bidder i's list of items
        
        # remove that item from list of available items
        for j in range(num_bidder):
            bidders_valuation_copy[j].pop(index)
        
    # write to sheet
    for x in range(len(bidder_items[y])):
        sheet.write(row_start - 1, x + 1, "pick" + str(x + 1))
    sheet.write(row_start - 1, len(bidder_items[y]) + 1, "total utility")

    sum_total = 0
    for y in range(num_bidder):
        total = 0
        sheet.write(row_start + y, 0, "bidder" + str(y + 1) + " item values: ")
        for x in range(len(bidder_items[y])):
            sheet.write(row_start + y, x + 1, bidder_items[y][x])
            total += bidder_items[y][x]
        sheet.write(row_start + y, x + 2, total)
        sum_total += total
    
    row_start += num_bidder
    sheet.write(row_start, x + 2, sum_total, upperline)


    # =============================================== second price budget auction ===============================================
    row_start += 2
    # generate fair budget from avg utility in snake draft
    budget = int((sum_total / 4) * 1.1)

    sheet.write(row_start, 0, "SECOND PRICE BUDGET AUCTION RESULT", header_border)
    sheet.write(row_start, 1, "budget=" + str(budget), header_border)
    for i in range(2, num_item + 1):
        sheet.write(row_start, i, "", header_border)
    
    # setup
    bidder_items = [ [] for _ in range(num_bidder) ]
    budgets = [ budget for _ in range(num_bidder) ]

    bidders_valuation_copy = copy.deepcopy(private_values)
    for y in range(num_bidder):
        for x in range(num_item):
            bidders_valuation_copy[y][x] = bidders_valuation_copy[y][x] + common_values[x]

    # set the auction order for items based on overall valuations
    auction_order = set_auction_order(bidders_valuation_copy)
    # print(auction_order)

    # compute each round
    row_start = row_start + 2

    for i in range(num_item):
        index = auction_order[i]
        bids = []
        for j in range(num_bidder):
            if len(bidder_items[j]) < (num_item / num_bidder):
                bid = min(bidders_valuation_copy[j][index], budgets[j]) # bids his valuation or remaining budget
                bids.append(bid)
            else:
                bid = 0
                bids.append(bid)

        # compute round
        [winner_index, price] = get_winner_second_price_auctiion(bids)

        # give item to the winner
        bidder_items[winner_index].append(bidders_valuation_copy[winner_index][index])

        # reduce winner's budget by the second highest bid
        budgets[winner_index] -= price

    # write to sheet
    for x in range(len(bidder_items[y])):
        sheet.write(row_start - 1, x + 1, "item" + str(x + 1))
    sheet.write(row_start - 1, len(bidder_items[y]) + 1, "total utility")

    sum_total = 0
    for y in range(num_bidder):
        total = 0
        sheet.write(row_start + y, 0, "bidder" + str(y + 1) + " item values: ")
        for x in range(len(bidder_items[y])):
            sheet.write(row_start + y, x + 1, bidder_items[y][x])
            total += bidder_items[y][x]
        sheet.write(row_start + y, x + 2, total)
        sum_total += total
    
    row_start += num_bidder
    sheet.write(row_start, x + 2, sum_total, upperline)

    # =============================================== first price budget auction ===============================================
    row_start += 2
    # generate fair budget from avg utility in snake draft

    sheet.write(row_start, 0, "FIRST PRICE BUDGET AUCTION RESULT", header_border)
    sheet.write(row_start, 1, "budget=" + str(budget), header_border)
    for i in range(2, num_item + 1):
        sheet.write(row_start, i, "", header_border)
    
    # setup
    bidder_items = [ [] for _ in range(num_bidder) ]
    budgets = [ budget for _ in range(num_bidder) ]

    bidders_valuation_copy = copy.deepcopy(private_values)
    for y in range(num_bidder):
        for x in range(num_item):
            bidders_valuation_copy[y][x] = bidders_valuation_copy[y][x] + common_values[x]

    # set the auction order for items based on overall valuations
    auction_order = set_auction_order(bidders_valuation_copy)

    # compute each round
    row_start = row_start + 2

    for i in range(num_item):
        index = auction_order[i]
        bids = []
        for j in range(num_bidder):
            if len(bidder_items[j]) < (num_item / num_bidder):
                bid_from_strategy = int(bidders_valuation_copy[j][index] * num_bidder / (num_bidder - 1))
                bid = min(bid_from_strategy , budgets[j]) # bids his valuation or remaining budget
                bids.append(bid)
            else:
                bid = 0
                bids.append(bid)

        # compute round
        [winner_index, price] = get_winner_second_price_auctiion(bids)

        # give item to the winner
        bidder_items[winner_index].append(bidders_valuation_copy[winner_index][index])

        # reduce winner's budget by the second highest bid
        budgets[winner_index] -= price

    # write to sheet
    for x in range(len(bidder_items[y])):
        sheet.write(row_start - 1, x + 1, "item" + str(x + 1))
    sheet.write(row_start - 1, len(bidder_items[y]) + 1, "total utility")

    sum_total = 0
    for y in range(num_bidder):
        total = 0
        sheet.write(row_start + y, 0, "bidder" + str(y + 1) + " item values: ")
        for x in range(len(bidder_items[y])):
            sheet.write(row_start + y, x + 1, bidder_items[y][x])
            total += bidder_items[y][x]
        sheet.write(row_start + y, x + 2, total)
        sum_total += total
    
    row_start += num_bidder
    sheet.write(row_start, x + 2, sum_total, upperline)


# SET INPUT HERE

for i in range(10):
    create_sheet(
        sheet_name="sim" + str(i + 1), 
        num_bidder=2, 
        num_item=10, 
        gamma_input=3, 
        gamma_scale=10, 
        uniform_left=0, 
        uniform_right=10)

for i in range(10, 20):
    create_sheet(
        sheet_name="sim" + str(i + 1), 
        num_bidder=4, 
        num_item=24, 
        gamma_input=3, 
        gamma_scale=10, 
        uniform_left=0, 
        uniform_right=10)

for i in range(20, 30):
    create_sheet(
        sheet_name="sim" + str(i + 1), 
        num_bidder=8, 
        num_item=64, 
        gamma_input=3, 
        gamma_scale=10, 
        uniform_left=0, 
        uniform_right=10)

workbook.close()