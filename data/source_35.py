from typing import List

def maxSumOfThreeSubarrays(nums: List[int], k: int) -> List[int]:
    n = len(nums) - k + 1
    sums = [0] * n
    l = [0] * n
    r = [0] * n

    # Compute sums of all windows of size k
    summ = 0
    for i, num in enumerate(nums):
        summ += num
        if i >= k:
            summ -= nums[i - k]
        if i >= k - 1:
            sums[i - k + 1] = summ

    # Compute best left positions for each i
    maxIndex = 0
    for i in range(n):
        if sums[i] > sums[maxIndex]:
            maxIndex = i
        l[i] = maxIndex

    # Compute best right positions for each i
    maxIndex = n - 1
    for i in range(n - 1, -1, -1):
        if sums[i] >= sums[maxIndex]:
            maxIndex = i
        r[i] = maxIndex

    # Evaluate the max sum by trying middle interval
    ans = [-1, -1, -1]
    for i in range(k, n - k):
        left = l[i - k]
        right = r[i + k]
        total = sums[left] + sums[i] + sums[right]
        if ans[0] == -1 or total > sums[ans[0]] + sums[ans[1]] + sums[ans[2]]:
            ans[0], ans[1], ans[2] = left, i, right

    return ans
