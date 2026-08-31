from typing import List, Tuple


def maximumSumQueries(nums1: List[int], nums2: List[int], queries: List[List[int]]) -> List[int]:
    class Pair:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y

        def __iter__(self):
            yield self.x
            yield self.y

    class IndexedQuery:
        def __init__(self, queryIndex: int, minX: int, minY: int):
            self.queryIndex = queryIndex
            self.minX = minX
            self.minY = minY

        def __iter__(self):
            yield self.queryIndex
            yield self.minX
            yield self.minY

    def _firstGreaterEqual(A: List[Tuple[int, int]], target: int) -> int:
        l, r = 0, len(A)
        while l < r:
            m = (l + r) // 2
            if A[m][0] >= target:
                r = m
            else:
                l = m + 1
        return l

    pairs = sorted(
        [Pair(nums1[i], nums2[i]) for i in range(len(nums1))],
        key=lambda p: p.x,
        reverse=True,
    )
    ans = [0] * len(queries)
    stack = []  # [(y, x + y)]

    pairsIndex = 0
    for queryIndex, minX, minY in sorted(
        [IndexedQuery(i, query[0], query[1]) for i, query in enumerate(queries)],
        key=lambda iq: -iq.minX,
    ):
        while pairsIndex < len(pairs) and pairs[pairsIndex].x >= minX:
            x, y = pairs[pairsIndex]
            while stack and x + y >= stack[-1][1]:
                stack.pop()
            if not stack or y > stack[-1][0]:
                stack.append((y, x + y))
            pairsIndex += 1
        j = _firstGreaterEqual(stack, minY)
        if j == len(stack):
            ans[queryIndex] = -1
        else:
            ans[queryIndex] = stack[j][1]

    return ans
