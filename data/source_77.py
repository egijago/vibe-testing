from collections import deque
from typing import List

def shortestPath(grid: List[List[int]], k: int) -> int:
    m = len(grid)
    n = len(grid[0])
    if m == 1 and n == 1:
        return 0

    dirs = ((0, 1), (1, 0), (0, -1), (-1, 0))
    steps = 0
    q = deque([(0, 0, k)])
    seen = {(0, 0, k)}

    while q:
        steps += 1
        for _ in range(len(q)):
            i, j, eliminate = q.popleft()
            for dx, dy in dirs:
                x = i + dx
                y = j + dy
                if x < 0 or x == m or y < 0 or y == n:
                    continue
                if x == m - 1 and y == n - 1:
                    return steps
                if grid[x][y] == 1 and eliminate == 0:
                    continue
                new_eliminate = eliminate - grid[x][y]
                if (x, y, new_eliminate) in seen:
                    continue
                q.append((x, y, new_eliminate))
                seen.add((x, y, new_eliminate))

    return -1
