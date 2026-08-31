def originalDigits(s: str) -> str:
    count = [0] * 10

    for c in s:
        if c == 'z':
            count[0] += 1  # zero
        if c == 'o':
            count[1] += 1  # one (after zero, two, four)
        if c == 'w':
            count[2] += 1  # two
        if c == 'h':
            count[3] += 1  # three (after eight)
        if c == 'u':
            count[4] += 1  # four
        if c == 'f':
            count[5] += 1  # five (after four)
        if c == 'x':
            count[6] += 1  # six
        if c == 's':
            count[7] += 1  # seven (after six)
        if c == 'g':
            count[8] += 1  # eight
        if c == 'i':
            count[9] += 1  # nine (after five, six, eight)

    # Adjust overlapping character counts
    count[1] -= count[0] + count[2] + count[4]
    count[3] -= count[8]
    count[5] -= count[4]
    count[7] -= count[6]
    count[9] -= count[5] + count[6] + count[8]

    return ''.join(chr(i + ord('0')) * count[i] for i in range(10))
