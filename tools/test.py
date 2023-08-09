from time import time

def fib(n):
    if n<=1: return n
    return fib(n-2) + fib(n-1)

start = time()
for i in range(20):
    print(fib(i))

print(time() - start)