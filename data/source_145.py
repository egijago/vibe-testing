from typing import List


def countUnguarded(m: int, n: int, guards: List[List[int]], walls: List[List[int]]) -> int:
    ans = 0
    grid = [[0] * n for _ in range(m)]
    left = [[0] * n for _ in range(m)]
    right = [[0] * n for _ in range(m)]
    up = [[0] * n for _ in range(m)]
    down = [[0] * n for _ in range(m)]

    # Place guards and walls
    for row, col in guards:
        grid[row][col] = 'G'
    for row, col in walls:
        grid[row][col] = 'W'

    # Scan rows left-to-right and right-to-left
    for i in range(m):
        lastCell = 0
        for j in range(n):
            if grid[i][j] in ('G', 'W'):
                lastCell = grid[i][j]
            else:
                left[i][j] = lastCell
        lastCell = 0
        for j in range(n - 1, -1, -1):
            if grid[i][j] in ('G', 'W'):
                lastCell = grid[i][j]
            else:
                right[i][j] = lastCell

    # Scan columns top-to-bottom and bottom-to-top
    for j in range(n):
        lastCell = 0
        for i in range(m):
            if grid[i][j] in ('G', 'W'):
                lastCell = grid[i][j]
            else:
                up[i][j] = lastCell
        lastCell = 0
        for i in range(m - 1, -1, -1):
            if grid[i][j] in ('G', 'W'):
                lastCell = grid[i][j]
            else:
                down[i][j] = lastCell

    # Count unguarded cells
    for i in range(m):
        for j in range(n):
            if (
                grid[i][j] == 0
                and left[i][j] != 'G'
                and right[i][j] != 'G'
                and up[i][j] != 'G'
                and down[i][j] != 'G'
            ):
                ans += 1

    return ans
