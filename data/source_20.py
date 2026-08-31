import heapq
from typing import List, Set, Tuple

def trapRainWater(heightMap: List[List[int]]) -> int:
    if not heightMap or not heightMap[0]:
        return 0

    dirs = ((0, 1), (1, 0), (0, -1), (-1, 0))
    m = len(heightMap)
    n = len(heightMap[0])
    ans = 0
    minHeap: List[Tuple[int, int, int]] = []
    seen: Set[Tuple[int, int]] = set()

    for i in range(m):
        heapq.heappush(minHeap, (heightMap[i][0], i, 0))
        heapq.heappush(minHeap, (heightMap[i][n - 1], i, n - 1))
        seen.add((i, 0))
        seen.add((i, n - 1))

    for j in range(1, n - 1):
        heapq.heappush(minHeap, (heightMap[0][j], 0, j))
        heapq.heappush(minHeap, (heightMap[m - 1][j], m - 1, j))
        seen.add((0, j))
        seen.add((m - 1, j))

    while minHeap:
        h, i, j = heapq.heappop(minHeap)
        for dx, dy in dirs:
            x = i + dx
            y = j + dy
            if x < 0 or x == m or y < 0 or y == n:
                continue
            if (x, y) in seen:
                continue
            seen.add((x, y))
            if heightMap[x][y] < h:
                ans += h - heightMap[x][y]
                heapq.heappush(minHeap, (h, x, y))
            else:
                heapq.heappush(minHeap, (heightMap[x][y], x, y))

    return ans
