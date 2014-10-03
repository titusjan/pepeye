import pstats
from objbrowser import browse

def main():
    
    prof = pstats.Stats("small.prof")
    prof.strip_dirs()
    prof.calc_callees()
    #browse(prof, "prof")
    browse(locals(), "locals")
    
    
if __name__ == "__main__":
    main()
    
    