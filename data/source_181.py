from typing import List


def minimumOperations(num: str) -> int:
    n = len(num)
    seenFive = False
    seenZero = False

    for i in range(n - 1, -1, -1):
        if seenZero and num[i] == '0':
            return n - i - 2
        if seenZero and num[i] == '5':
            return n - i - 2
        if seenFive and num[i] == '2':
            return n - i - 2
        if seenFive and num[i] == '7':
            return n - i - 2
        seenZero = seenZero or num[i] == '0'
        seenFive = seenFive or num[i] == '5'

    if seenZero:
        return n - 1
    else:
        return n
