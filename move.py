import sys
import glob
import time
import os

from shutil import copyfile

def main(source, dest, wait=10):
    while True:
        os.chdir(source) 
        allfiles = sorted(glob.glob('*.gz'))
        os.chdir('..') 
        
        for f in allfiles[:-1]:
            print source+f, dest+f
            copyfile(source+f, dest+f)
            os.remove(source+f)
            
        time.sleep(wait)

if __name__ == '__main__':
    source = sys.argv[1]
    dest = sys.argv[2]
    main(source,dest)