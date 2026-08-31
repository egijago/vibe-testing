import heapq
from typing import List


def maxPoints(grid: List[List[int]], queries: List[int]) -> List[int]:
    dirs = ((0, 1), (1, 0), (0, -1), (-1, 0))
    m = len(grid)
    n = len(grid[0])
    ans = [0] * len(queries)
    minHeap = [(grid[0][0], 0, 0)]
    seen = {(0, 0)}
    accumulate = 0

    class IndexedQuery:
        def __init__(self, queryIndex: int, query: int):
            self.queryIndex = queryIndex
            self.query = query

        def __iter__(self):
            yield self.queryIndex
            yield self.query

    for queryIndex, query in sorted(
        [IndexedQuery(i, query) for i, query in enumerate(queries)],
        key=lambda iq: iq.query
    ):
        while minHeap:
            val, i, j = heapq.heappop(minHeap)
            if val >= query:
                heapq.heappush(minHeap, (val, i, j))
                break
            accumulate += 1
            for dx, dy in dirs:
                x = i + dx
                y = j + dy
                if x < 0 or x == m or y < 0 or y == n:
                    continue
                if (x, y) in seen:
                    continue
                heapq.heappush(minHeap, (grid[x][y], x, y))
                seen.add((x, y))
        ans[queryIndex] = accumulate

    return ans
