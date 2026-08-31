from typing import List


def canMakePalindromeQueries(s: str, queries: List[List[int]]) -> List[bool]:
    n = len(s)

    def getMirroredDiffs(s: str) -> List[int]:
        diffs = [0]
        for i, j in zip(range(len(s)), reversed(range(len(s)))):
            if i >= j:
                break
            diffs.append(diffs[-1] + (s[i] != s[j]))
        return diffs

    def getCounts(s: str) -> List[List[int]]:
        count = [0] * 26
        counts = [count.copy()]
        for c in s:
            count[ord(c) - ord('a')] += 1
            counts.append(count.copy())
        return counts

    def subtractArrays(a: List[int], b: List[int]) -> List[int]:
        return [x - y for x, y in zip(a, b)]

    mirroredDiffs = getMirroredDiffs(s)
    counts = getCounts(s)
    ans = []

    for a, b, c, d in queries:
        b += 1
        d += 1
        ra = n - a
        rb = n - b
        rc = n - c
        rd = n - d

        if (
            (min(a, rd) > 0 and mirroredDiffs[min(a, rd)] > 0)
            or (n // 2 > max(b, rc) and mirroredDiffs[n // 2] - mirroredDiffs[max(b, rc)] > 0)
            or (rd > b and mirroredDiffs[rd] - mirroredDiffs[b] > 0)
            or (a > rc and mirroredDiffs[a] - mirroredDiffs[rc] > 0)
        ):
            ans.append(False)
        else:
            leftRangeCount = subtractArrays(counts[b], counts[a])
            rightRangeCount = subtractArrays(counts[d], counts[c])
            if a > rd:
                rightRangeCount = subtractArrays(
                    rightRangeCount, subtractArrays(counts[min(a, rc)], counts[rd])
                )
            if rc > b:
                rightRangeCount = subtractArrays(
                    rightRangeCount, subtractArrays(counts[rc], counts[max(b, rd)])
                )
            if c > rb:
                leftRangeCount = subtractArrays(
                    leftRangeCount, subtractArrays(counts[min(c, ra)], counts[rb])
                )
            if ra > d:
                leftRangeCount = subtractArrays(
                    leftRangeCount, subtractArrays(counts[ra], counts[max(d, rb)])
                )
            ans.append(
                min(leftRangeCount) >= 0
                and min(rightRangeCount) >= 0
                and leftRangeCount == rightRangeCount
            )

    return ans
