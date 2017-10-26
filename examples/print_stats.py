import pstats, sys

def main(fileName):
    
    stats = pstats.Stats(fileName)
    stats.strip_dirs()
    stats.sort_stats('cumulative')#.print_stats(20)
    #print "\n"
    stats.print_callers(1000)
    #stats.print_callees()

if __name__ == "__main__":
    fileName = sys.argv[1] if len(sys.argv) == 2 else "small.prof"
    main(fileName)
    
    