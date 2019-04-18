import sys

from lib.graph import Graph


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == '--help':
        print("Run this file with site root url like:")
        print("python3 %s https://mysite.com/" % sys.argv[0])
        sys.exit(0)
    
