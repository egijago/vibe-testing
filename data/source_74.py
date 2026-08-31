from typing import List, Tuple
from collections import deque

def minPushBox(grid: List[List[str]]) -> int:
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == "T":
                target = (i, j)
            if grid[i][j] == "B":
                box = (i, j)
            if grid[i][j] == "S":
                person = (i, j)

    def valid(x: int, y: int) -> bool:
        return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] != '#'

    def check(curr: Tuple[int, int], dest: Tuple[int, int], box: Tuple[int, int]) -> bool:
        que = deque([curr])
        visited = set()
        while que:
            pos = que.popleft()
            if pos == dest:
                return True
            new_positions = [
                (pos[0] + 1, pos[1]),
                (pos[0] - 1, pos[1]),
                (pos[0], pos[1] + 1),
                (pos[0], pos[1] - 1)
            ]
            for x, y in new_positions:
                if valid(x, y) and (x, y) not in visited and (x, y) != box:
                    visited.add((x, y))
                    que.append((x, y))
        return False

    q = deque([(0, box, person)])
    visited_states = {box + person}

    while q:
        dist, box, person = q.popleft()
        if box == target:
            return dist

        b_coords = [
            (box[0] + 1, box[1]),
            (box[0] - 1, box[1]),
            (box[0], box[1] + 1),
            (box[0], box[1] - 1)
        ]
        p_coords = [
            (box[0] - 1, box[1]),
            (box[0] + 1, box[1]),
            (box[0], box[1] - 1),
            (box[0], box[1] + 1)
        ]

        for new_box, new_person in zip(b_coords, p_coords):
            if valid(*new_box) and new_box + box not in visited_states:
                if valid(*new_person) and check(person, new_person, box):
                    visited_states.add(new_box + box)
                    q.append((dist + 1, new_box, box))

    return -1
