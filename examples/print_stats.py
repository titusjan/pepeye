import pstats

def main():
    
    stats = pstats.Stats("small.prof")
    stats.strip_dirs()
    stats.sort_stats('cumulative').print_stats(20)
    print "\n"
    stats.print_callers()
    #stats.print_callees()

if __name__ == "__main__":
    main()
    
    