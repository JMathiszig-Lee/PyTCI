import time
from PyTCI.models.propofol import Marsh


pt1 = Marsh(70)
pt2 = Marsh(70)
x=1000

tic = time.perf_counter()
for _ in range(x):
    pt1.give_drug(10)
    pt1.wait_time(1000)
toc = time.perf_counter()
time1 = toc-tic

print(f"Standard test: {time1:.4}")

tic = time.perf_counter()
for _ in range(x):
    pt2.give_drug(10)
    pt2.jit_wait_time(1000)
toc = time.perf_counter()

time2 = toc-tic

print(f"jit test: {time2:.4}")
ratio = time2/time1
print(f"ratio: {ratio:.4}")

print(pt1.x1)
print(pt2.x2)