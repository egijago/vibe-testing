from typing import List
from enum import Enum

class State(Enum):
    kInit = 0
    kVisiting = 1
    kVisited = 2

def isPrintable(targetGrid: List[List[int]]) -> bool:
    kMaxColor = 60
    m = len(targetGrid)
    n = len(targetGrid[0])

    graph = [set() for _ in range(kMaxColor + 1)]

    for color in range(1, kMaxColor + 1):
        minI = m
        minJ = n
        maxI = -1
        maxJ = -1
        for i in range(m):
            for j in range(n):
                if targetGrid[i][j] == color:
                    minI = min(minI, i)
                    minJ = min(minJ, j)
                    maxI = max(maxI, i)
                    maxJ = max(maxJ, j)
        for i in range(minI, maxI + 1):
            for j in range(minJ, maxJ + 1):
                if 0 <= i < m and 0 <= j < n and targetGrid[i][j] != color:
                    graph[color].add(targetGrid[i][j])

    states = [State.kInit] * (kMaxColor + 1)

    def hasCycle(u: int) -> bool:
        if states[u] == State.kVisiting:
            return True
        if states[u] == State.kVisited:
            return False
        states[u] = State.kVisiting
        if any(hasCycle(v) for v in graph[u]):
            return True
        states[u] = State.kVisited
        return False

    for i in range(1, kMaxColor + 1):
        if hasCycle(i):
            return False
    return True
