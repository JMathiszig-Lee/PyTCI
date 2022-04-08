import time
from PyTCI.models.propofol import Marsh


pt1 = Marsh(70)
pt2 = Marsh(70)
x=100

tic = time.perf_counter()
for _ in range(x):
    pt1.give_drug(10)
    pt1.wait_time(100)
toc = time.perf_counter()
time1 = toc-tic


tic = time.perf_counter()
for _ in range(x):
    pt2.give_drug(10)
    pt2.jit_wait_time(100)
toc = time.perf_counter()

time2 = toc-tic
print(time1, time2, time2/time1)

print(pt1.x1)
print(pt2.x2)