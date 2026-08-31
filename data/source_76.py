from collections import deque
from typing import List

def minFlips(mat: List[List[int]]) -> int:
    m = len(mat)
    n = len(mat[0])

    def get_hash(mat: List[List[int]], m: int, n: int) -> int:
        hash_val = 0
        for i in range(m):
            for j in range(n):
                if mat[i][j]:
                    hash_val |= 1 << (i * n + j)
        return hash_val

    initial_hash = get_hash(mat, m, n)
    if initial_hash == 0:
        return 0

    dirs = ((0, 1), (1, 0), (0, -1), (-1, 0))
    step = 0
    q = deque([initial_hash])
    seen = {initial_hash}

    while q:
        step += 1
        for _ in range(len(q)):
            curr = q.popleft()
            for i in range(m):
                for j in range(n):
                    nxt = curr ^ (1 << (i * n + j))
                    for dx, dy in dirs:
                        x = i + dx
                        y = j + dy
                        if 0 <= x < m and 0 <= y < n:
                            nxt ^= 1 << (x * n + y)
                    if nxt == 0:
                        return step
                    if nxt not in seen:
                        seen.add(nxt)
                        q.append(nxt)

    return -1
