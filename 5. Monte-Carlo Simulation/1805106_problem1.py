import random
SEED = 1
LEVEL = 10
ITER = 10000
MAXN = 4
N = 3

random.seed(SEED)

count = [[0 for i in range(MAXN + 1)] for j in range(LEVEL + 1)]
def getInt(dist, x):
    i = 0
    # print(x)
    while dist[i] <= x:
        i += 1
    return i

def monte_carlo(n, dist, dep = 0):
    global count
    if dep > LEVEL:
        return 
    if n <= MAXN:
        count[dep][n] += 1
    sum = 0
    for i in range(n):
        u = random.random()
        u = getInt(dist, u)
        sum += u

    monte_carlo(sum, dist, dep + 1)



dist = [0 for i in range(N + 1)]
sum = 0
for i in range(1, N + 1):
    dist[i] = (0.2126) * (0.5893 ** (i - 1))
    sum += dist[i]

dist[0] = 1 - sum

for i in range(1, N + 1):
    dist[i] += dist[i - 1]
print(dist)

for i in range(ITER):
    monte_carlo(1, dist)


for i in range(1, LEVEL + 1):
    print(f"Generation-{i}:")
    for j in range(0, MAXN + 1):
        print(f"p[{j}] = {(count[i][j] / ITER):.4f}")
    print()