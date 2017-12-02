# -----------------------------------------
# These are threat attack patterns which are used to calculate heuristic values
# o (alphabet o) means attacker's stone
# - (dash) means empty space
# x (alphabet x) means attacker's opponent's stone
# w means wall(out of bounds)
# each pattern must be 6 characters long
# -----------------------------------------
# (Reference)
# I have also added Open2 for heuristics calculation.
# They pose of low value, but, multiple Open2s can turn into a Open3xOpen3.
# Also, Open2s can make better decisions in the opening, where making as many threats as possible is good.
# -----------------------------------------
# Vanilla Weights:
# Open2:5 Open3:40000 Open4:10000000 Open5:1000000000 Closed4:50000
Open2 = [
    "-oo---",
    "--oo--",
    "---oo-",
    "-o-o--",
    "--o-o-",
    "-oo--w",
    "--oo-w",
    "-o-o-w",
    "w--oo-",
    "w-oo--",
    "w-o-o-"

]
Open2Val = 5
# -----------------------------------------
# Open3 is a threat in which all the ends of 3 repetitive stones are open
# The third and fourth are also counted as Open3
Open3 = [
    "-ooo--",
    "--ooo-",
    "-o-oo-",
    "-oo-o-",
    "x-ooo-",
    "w-ooo-",
    "-ooo-x",
    "-ooo-w",
    "w-ooo-",
]
Open3Val = 20
# -----------------------------------------
# Open4 is a threat in which all the ends of 4 repetitive stones are open
# If the attacker does not have an Closed4 or Open4 to make into 5 immediately, Attacker is guaranteed to win next turn
Open4 = [
    "-oooo-"  # TSS OK
]
Open4Val = 500
# -----------------------------------------
# Open5 is a win condition.
Open5 = [
    "xooooo",  # TSS OK
    "ooooox",  # the algorithm will not count this as a 5 win , because it is not possible
    "-ooooo",  # TSS OK
    "ooooo-",  # TSS OK same as above
    "wooooo"
]
Open5Val = 100000
# -----------------------------------------
# Closed4 is a threat in which one of the ends of 4 repetitive stones are open
# If the defender does not block the other end, Attacker is guaranteed to win next turn.
Closed4 = [
    "xoooo-",  # TSS OK
    "-oooox",  # TSS OK
    "xoo-oo",  # TSS OK
    "woooo-",  # TSS OK
    "xo-ooo",  # TSS OK
    "xoo-oo",  # TSS OK
    "-o-ooo",  # TSS OK
    "-oo-oo",  # TSS OK
    "-ooo-o"   # TSS OK
    "xooo-o",
    "wo-ooo",
    "woo-oo",
    "wooo-o"
]
Closed4Val = 20
