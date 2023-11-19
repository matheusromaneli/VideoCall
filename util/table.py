def table(cols, rows):
    rows = [[str(x) for x in col] for col in rows]
    out = ""

    spaces = [len(x) + 2 for x in cols]
    for row in rows:
        i = 0
        for col in row:
            if len(col) + 2 > spaces[i]:
                spaces[i] = len(col) + 2
            i += 1

    for x in range(len(cols)):
        s = spaces[x] - len(cols[x])
        s2 = s % 2
        s //= 2

        cols[x] = " " * s + cols[x] + " " * (s + s2)

    out += "|" + "|".join(cols) + "|\n"

    for row in rows:
        x = 0
        for col in row:
            out += "|"
            s = spaces[x] - len(col)
            s2 = s % 2
            s //= 2
            out += " " * s + col + " " * (s + s2)

            x += 1
        out += "|\n"

    return out
