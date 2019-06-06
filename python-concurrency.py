When you call `future.result()`, that blocks until the value is ready. So, you’re not getting any benefits out of parallelism here—you start one task, wait for it to finish, start another, wait for it to finish, and so on.

Of course your example won’t benefit from threading in the first place. Your tasks are doing nothing but CPU-bound Python computation, which means that (at least in CPython, MicroPython, and PyPy, which are the only complete implementations that come with `concurrent.futures`), the GIL (Global Interpreter Lock) will prevent more than one of your threads from progressing at a time.

Hopefully your real program is different. If it’s doing I/O-bound stuff (making network requests, reading files, etc.), or using an extension library like NumPy that releases the GIL around heavy CPU work, then it will work fine. But otherwise, you’ll want to use `ProcessPoolExecutor` here.

Anyway, what you want to do is append future itself to a list, so you get a list of all of the futures before waiting for any of them:

```
for number in couple_ods:
    future=executor.submit(task,number)
    futures.append(future)
```
And then, after you’ve started all of the jobs, you can start waiting for them. There are three simple options, and one complicated one when you need more control.

(1) You can just directly loop over them to wait for them in the order they were submitted:
```
for future in futures:
    result = future.result()
    dostuff(result)
```

(2) If you need to wait for them all to be finished before doing any work, you can just call wait:
```
futures, _ = concurrent.futures.wait(futures)
for future in futures:
    result = future.result()
    dostuff(result)
```
(3) If you want to handle each one as soon as it’s ready, even if they come out of order, use `as_completed`:
```
for result in concurrent.futures.as_completed(futures):
    dostuff(result)
```
Notice that the examples that use this function in the docs provide some way to identify which task is finished. If you need that, it can be as simple as passing each one an index, then `return index, real_result`, and then you can `for index, result in …` for the loop.

(4) If you need more control, you can loop over waiting on whatever’s done so far:
```
while futures:
    done, futures = concurrent.futures.wait(concurrent.futures.FIRST_COMPLETED)
    for future in done:
        result = future.result()
        dostuff(result)
```
That example does the same thing as as_completed, but you can write minor variations on it to do different things, like waiting for everything to be done but canceling early if anything raises an exception.

For many simple cases, you can just use the map method of the executor to simplify the first option. This works just like the builtin map function, calling a function once for each value in the argument and then giving you something you can loop over to get the results in the same order, but it does it in parallel. So:
```
for result in executor.map(task, couple_ods):
    dostuff(result)
```
