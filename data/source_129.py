from typing import List


def smallestSubsequence(s: str, k: int, letter: str, repetition: int) -> str:
    stack = []
    required = repetition
    nLetters = s.count(letter)

    for i, c in enumerate(s):
        while (
            stack
            and stack[-1] > c
            and len(stack) + len(s) - i - 1 >= k
            and (stack[-1] != letter or nLetters > required)
        ):
            if stack.pop() == letter:
                required += 1

        if len(stack) < k:
            if c == letter:
                stack.append(c)
                required -= 1
            elif k - len(stack) > required:
                stack.append(c)

        if c == letter:
            nLetters -= 1

    return ''.join(stack)
