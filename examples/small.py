from __future__ import print_function

from time import sleep


def myfun1():
    print ("  myfun1")
    sleep(0.25)
    myfun3()
    
def myfun2(n):
    print ("  myfun2")
    sleep(0.15)
    if n == 0:
        return
    else:
        myfun3()
        myfun2(n-1)
    
def myfun3():
    print ("    myfun3")
    sleep(0.05)
    myfun4()
    
    
def myfun4():
    print ("      myfun4")
    sleep(0.003)
    

def main():
    print ("main")
    for i in range(10):
        myfun1()
        
    myfun2(15)

if __name__ == "__main__":
    main()
    