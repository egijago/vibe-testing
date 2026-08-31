from typing import List

def pathsWithMaxScore(board: List[str]) -> List[int]:
    kMod = 1_000_000_007
    n = len(board)
    dirs = ((0, 1), (1, 0), (1, 1))
    dp = [[-1] * (n + 1) for _ in range(n + 1)]
    count = [[0] * (n + 1) for _ in range(n + 1)]

    dp[n - 1][n - 1] = 0
    count[n - 1][n - 1] = 1

    for i in reversed(range(n)):
        for j in reversed(range(n)):
            if board[i][j] == 'S' or board[i][j] == 'X':
                continue
            for dx, dy in dirs:
                x = i + dx
                y = j + dy
                if x >= n or y >= n:
                    continue
                if dp[i][j] < dp[x][y]:
                    dp[i][j] = dp[x][y]
                    count[i][j] = count[x][y]
                elif dp[i][j] == dp[x][y]:
                    count[i][j] += count[x][y]
                    count[i][j] %= kMod

            if dp[i][j] != -1 and board[i][j] != 'E':
                dp[i][j] += int(board[i][j])
                dp[i][j] %= kMod

    return [dp[0][0], count[0][0]]
