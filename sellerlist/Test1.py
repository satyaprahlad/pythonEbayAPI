import time
import concurrent.futures

def worker(i):
    time.sleep(i)
    return i,time.time()

e = concurrent.futures.ThreadPoolExecutor(2)
arrIn = range(1,7)[::-1]
print(arrIn)

f = []
print ('start submit',time.time())
for i in arrIn:
    f.append(e.submit(worker,i))
print('submitted',time.time())
for r in concurrent.futures.as_completed(f):
    print(r.result(),time.time())
print

f = []
print ('start map',time.time())
f = e.map(worker,arrIn)
print ('mapped',time.time())
for r in f:
    print (r,time.time())
print("good in man thread")