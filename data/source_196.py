import math
from typing import List, Dict

def minimumCost(source: str, target: str, original: List[str], changed: List[str], cost: List[int]) -> int:
    subLengths = set(len(s) for s in original)

    def _getSubToId(original: List[str], changed: List[str]) -> Dict[str, int]:
        subToId: Dict[str, int] = {}
        for s in original + changed:
            if s not in subToId:
                subToId[s] = len(subToId)
        return subToId

    subToId = _getSubToId(original, changed)
    subCount = len(subToId)
    dist = [[math.inf for _ in range(subCount)] for _ in range(subCount)]
    dp = [math.inf for _ in range(len(source) + 1)]

    for a, b, c in zip(original, changed, cost):
        u = subToId[a]
        v = subToId[b]
        dist[u][v] = min(dist[u][v], c)

    # Floyd–Warshall over substring graph
    for k in range(subCount):
        for i in range(subCount):
            if dist[i][k] < math.inf:
                for j in range(subCount):
                    if dist[k][j] < math.inf:
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    dp[0] = 0

    for i, (s_char, t_char) in enumerate(zip(source, target)):
        if dp[i] == math.inf:
            continue
        if s_char == t_char:
            dp[i + 1] = min(dp[i + 1], dp[i])
        for subLength in subLengths:
            if i + subLength > len(source):
                continue
            subSource = source[i:i + subLength]
            subTarget = target[i:i + subLength]
            if subSource not in subToId or subTarget not in subToId:
                continue
            u = subToId[subSource]
            v = subToId[subTarget]
            if dist[u][v] != math.inf:
                dp[i + subLength] = min(dp[i + subLength], dp[i] + dist[u][v])

    return -1 if dp[len(source)] == math.inf else dp[len(source)]
