from typing import List


def minOperationsToFlip(expression: str) -> int:
    stack = []

    for e in expression:
        if e in '(&|':
            stack.append((e, 0))
            continue
        if e == ')':
            lastPair = stack.pop()
            stack.pop()
        else: 
            lastPair = (e, 1)

        if stack and stack[-1][0] in '&|':
            op = stack.pop()[0]
            a, costA = stack.pop()
            b, costB = lastPair

            if op == '&':
                if a == '0' and b == '0':
                    lastPair = ('0', 1 + min(costA, costB))
                elif (a == '0' and b == '1') or (a == '1' and b == '0'):
                    lastPair = ('0', 1)
                else:
                    lastPair = ('1', min(costA, costB))
            else:  # op == '|'
                if a == '0' and b == '0':
                    lastPair = ('0', min(costA, costB))
                elif (a == '0' and b == '1') or (a == '1' and b == '0'):
                    lastPair = ('1', 1)
                else:
                    lastPair = ('1', 1 + min(costA, costB))

        stack.append(lastPair)

    return stack[-1][1]
