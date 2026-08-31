import heapq
import math
from typing import List

def findCrossingTime(n: int, k: int, time: List[List[int]]) -> int:
    ans = 0
    leftBridgeQueue = [(-leftToRight - rightToLeft, -i)
                       for i, (leftToRight, pickOld, rightToLeft, pickNew) in enumerate(time)]
    rightBridgeQueue = []
    leftWorkers = []
    rightWorkers = []

    heapq.heapify(leftBridgeQueue)

    while n > 0 or rightBridgeQueue or rightWorkers:
        while leftWorkers and leftWorkers[0][0] <= ans:
            i = heapq.heappop(leftWorkers)[1]
            heapq.heappush(leftBridgeQueue, (-time[i][0] - time[i][2], -i))
        while rightWorkers and rightWorkers[0][0] <= ans:
            i = heapq.heappop(rightWorkers)[1]
            heapq.heappush(rightBridgeQueue, (-time[i][0] - time[i][2], -i))
        if rightBridgeQueue:
            i = -heapq.heappop(rightBridgeQueue)[1]
            ans += time[i][2]
            heapq.heappush(leftWorkers, (ans + time[i][3], i))
        elif leftBridgeQueue and n > 0:
            i = -heapq.heappop(leftBridgeQueue)[1]
            ans += time[i][0]
            heapq.heappush(rightWorkers, (ans + time[i][1], i))
            n -= 1
        else:
            if leftWorkers and n > 0:
                ans1 = leftWorkers[0][0]
            else:
                ans1 = math.inf
            if rightWorkers:
                ans2 = rightWorkers[0][0]
            else:
                ans2 = math.inf
            ans = min(ans1, ans2)

    return ans
