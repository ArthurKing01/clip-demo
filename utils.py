import time
import os

def findIndex(list: list, target_fn):
    for i in range(len(list)):
        if target_fn(list[i]):
            return i
    return -1

def getTime(t: int):
    m,s = divmod(t, 60)
    h, m = divmod(m, 60)
    t_str = "%02d:%02d:%02d" % (h, m, s)
    print (t_str)
    return t_str

def waitForFileExist(p: str):
    for i in range(15):
        if os.path.exists(p):
            return
        time.sleep(1)
    raise Exception("file exists timeout error: " + p)

def o(name: str):
    return f'output/{name}'