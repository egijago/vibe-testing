from typing import List

def palindromePairs(words: List[str]) -> List[List[int]]:
    ans = []
    word_map = {word[::-1]: i for i, word in enumerate(words)}

    for i, word in enumerate(words):
        if "" in word_map and word_map[""] != i and word == word[::-1]:
            ans.append([i, word_map[""]])

        for j in range(1, len(word) + 1):
            l = word[:j]
            r = word[j:]
            if l in word_map and word_map[l] != i and r == r[::-1]:
                ans.append([i, word_map[l]])
            if r in word_map and word_map[r] != i and l == l[::-1]:
                ans.append([word_map[r], i])

    return ans
