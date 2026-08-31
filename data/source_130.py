from typing import List

def kthSmallestProduct(nums1: List[int], nums2: List[int], k: int) -> int:
    A1 = [-num for num in nums1 if num < 0][::-1]
    A2 = [num for num in nums1 if num >= 0]
    B1 = [-num for num in nums2 if num < 0][::-1]
    B2 = [num for num in nums2 if num >= 0]

    negCount = len(A1) * len(B2) + len(A2) * len(B1)

    if k > negCount:
        k -= negCount
        sign = 1
    else:
        k = negCount - k + 1
        sign = -1
        B1, B2 = B2, B1

    def numProductNoGreaterThan(A: List[int], B: List[int], m: int) -> int:
        ans = 0
        j = len(B) - 1
        for i in range(len(A)):
            while j >= 0 and A[i] * B[j] > m:
                j -= 1
            ans += j + 1
        return ans

    l, r = 0, 10**10

    while l < r:
        m = (l + r) // 2
        if numProductNoGreaterThan(A1, B1, m) + numProductNoGreaterThan(A2, B2, m) >= k:
            r = m
        else:
            l = m + 1

    return sign * l
