from __future__ import print_function

from time import sleep


def myfun1():
    print ("  myfun1")
    sleep(0.25)
    myfun3()
    
def myfun2():
    print ("  myfun2")
    sleep(0.15)
    myfun3()
    
def myfun3():
    print ("    myfun3")
    sleep(0.05)
    

def main():
    print ("main")
    for i in range(10):
        myfun1()
        
    for i in range(15):
        myfun2()

if __name__ == "__main__":
    main()
    