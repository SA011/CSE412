import random
import numpy as np
import matplotlib.pyplot as plt

SEED = 1
ITER = 10000

random.seed(SEED)

n = int(input("Population Size: "))
s = int(input("Success criteria: "))

success_count = [0 for i in range(n)]

for it in range(ITER):
    v = [i for i in range(1, n + 1)]
    random.shuffle(v)
    cur = n + 1
    last = 0
    for j in range(n):
        if v[j] < cur:
            if v[j] <= s:
                #success
                while last <= j:
                    success_count[last] += 1
                    last += 1
            last = j + 1
            cur = v[j]

for i in range(n):
    success_count[i] /= ITER / 100

best = np.argmax(success_count)
print(f"Optimal Strategy(M): {best / n * 100:.2f}%")

plt.plot(success_count)

plt.xlim([0, n - 1])
plt.ylim([0, 100])

plt.xlabel('sample size (M)')
plt.ylabel('success rate')
plt.title(f"n = {n} and s = {s}")
plt.show()