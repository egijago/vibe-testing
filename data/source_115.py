from typing import List
import collections


def largestPathValue(colors: str, edges: List[List[int]]) -> int:
    n = len(colors)
    ans = 0
    processed = 0
    graph = [[] for _ in range(n)]
    inDegrees = [0] * n
    q = collections.deque()
    count = [[0] * 26 for _ in range(n)]

    # Build graph and in-degrees
    for u, v in edges:
        graph[u].append(v)
        inDegrees[v] += 1

    # Initialize queue with nodes having in-degree 0
    for i, degree in enumerate(inDegrees):
        if degree == 0:
            q.append(i)

    # Topological order traversal with color counts
    while q:
        u = q.popleft()
        processed += 1
        color_index = ord(colors[u]) - ord('a')
        count[u][color_index] += 1
        ans = max(ans, count[u][color_index])

        for v in graph[u]:
            for i in range(26):
                count[v][i] = max(count[v][i], count[u][i])
            inDegrees[v] -= 1
            if inDegrees[v] == 0:
                q.append(v)

    return ans if processed == n else -1
