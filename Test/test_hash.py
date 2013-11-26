#!/usr/bin/python3

K = 16

def ma_hash(i, hashes):
    footprint = str(i)[::-1].lstrip("0")

    for n in range(len(footprint), 0, -1):
        result = footprint[:n]
        hashes.add(result)


def autre_hash(i, hashes):
    footprint = str(i).lstrip("0")

    for n in range(len(footprint), 0, -1):
        result = footprint[:n]
        hashes.add(result)


def collecter(function, hashes):
    for i in range(2**K):
        function(i, hashes)


def tester(function):
    resultats = dict()
    hashes = set()

    for i in range(1, 10):
        resultats[str(i)] = 0

    collecter(function, hashes)
    for hash in sorted(hashes):
        print(hash)
        resultats[hash[0]] += 1

    print("-" * 72)
    for clef in sorted(resultats.keys()):
        print("{} : {}".format(clef, resultats[clef]))


if __name__ == "__main__":
    tester(ma_hash)
    tester(autre_hash)
