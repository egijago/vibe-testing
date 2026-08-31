import math
from typing import List

def findUnsortedSubarray(nums: List[int]) -> int:
    mini = math.inf
    maxi = -math.inf
    flag = False

    for i in range(1, len(nums)):
        if nums[i] < nums[i - 1]:
            flag = True
        if flag:
            mini = min(mini, nums[i])

    flag = False

    for i in reversed(range(len(nums) - 1)):
        if nums[i] > nums[i + 1]:
            flag = True
        if flag:
            maxi = max(maxi, nums[i])

    for l in range(len(nums)):
        if nums[l] > mini:
            break
    else:
        l = len(nums)

    for r in reversed(range(len(nums))):
        if nums[r] < maxi:
            break
    else:
        r = -1

    return 0 if l >= r else r - l + 1
