import numpy as np
from random import random
from random import seed
from queue import PriorityQueue

def lcs(tckrs, correlations, sub):
    # seed(1)
    # tckrs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    # # tckrs = ['A', 'B', 'C', 'D']
    # correlations = np.identity(len(tckrs), dtype=None)
    # # Will need code that actually calculates get_stock_data between x and y
    # for x in range(len(tckrs)):
    #     for y in range(x):
    #         value = random() * 2 - 1
    #         correlations[x, y] = value
    #         correlations[y, x] = value
    # # print(correlations)
    #
    # sub = 4

    # Beginning of search algorithm
    solutions = PriorityQueue()
    sols = []

    for x in range(len(tckrs)):
        curr = (x, 0.0, [x])
        # (currInd, total get_stock_data, list of path)
        # prevstates = []
        # prevstates.append(set(curr[2]))
        open = PriorityQueue()
        while not len((curr[2])) is (sub + 1):
            for y in range(len(tckrs)):
                temp = curr[2].copy()
                check = temp.copy()
                if y not in temp:
                    check.append(y)
                    # if set(check) not in prevstates:
                    total = 0
                    for i in range(len(temp)):
                        total += correlations[y, temp[i]]
                    temp.append(y)
                    open.put((abs(total + curr[1]), (y, total + curr[1], temp)))
            curr = open.get()[1]
            # while set(curr[2]) in prevstates:
            #     curr = open.get()[1]
            # prevstates.append(set(curr[2]))
            if len(curr[2]) is sub:
                solutions.put((abs(curr[1]), curr[2]))
    finCor, finInds = solutions.get()
    # finInds = sorted(finInds)
    stocks = []
    finfincor = 0
    for r in finInds:
        for c in finInds:
                if c > r:
                    finfincor += correlations[r][c]
    print(finInds)
    print(finfincor)
    for x in finInds:
        stocks.append(tckrs[x])

    return stocks, finCor




    # # Beginning of SFS algorithm
    # count = 0
    # for x in range(len(tckrs)):
    #     inds = [x]
    #     sols = PriorityQueue()
    #     pq = PriorityQueue()
    #     prevstates = []
    #     prevstates.append(set(inds))
    #     while not len(inds) == sub:
    #         # pq = PriorityQueue()
    #         for y in range(len(tckrs)):
    #             if y not in inds:
    #                 temp = inds.copy()
    #                 temp.append(y)
    #                 total = 0
    #                 for r in temp:
    #                     for c in temp:
    #                         if c > r:
    #                             total += correlations[r][c]
    #                 if set(temp) not in prevstates:
    #                     pq.put((abs(total), temp))
    #         inds = pq.get()[1]
    #         prevstates.append(set(inds))
    #         count += 1
    #     total = 0
    #     for r in inds:
    #         for c in inds:
    #             if c > r:
    #                 total += correlations[r][c]
    #     sols.put((abs(total), inds))
    # cor, final = sols.get()
    # final = sorted(final)
    # stocks = []
    # for x in final:
    #     stocks.append(tckrs[x])
    # print(stocks)
    # print(cor)
    # print(count)
