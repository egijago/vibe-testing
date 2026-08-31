def minMovesToCaptureTheQueen(a: int, b: int, c: int, d: int, e: int, f: int) -> int:
    if a == e:
        if c == a and (b < d < f or b > d > f):
            return 2
        else:
            return 1
    if b == f:
        if d == f and (a < c < e or a > c > e):
            return 2
        else:
            return 1
    if c + d == e + f:
        if a + b == c + d and (c < a < e or c > a > e):
            return 2
        else:
            return 1
    if c - d == e - f:
        if a - b == c - d and (c < a < e or c > a > e):
            return 2
        else:
            return 1
    return 2
