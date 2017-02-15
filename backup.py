import sys
import glob
import time
import os

from shutil import copyfile


def main(source, dest, wait=10):
    while True:
        os.chdir(source) 
        accfiles = sorted(glob.glob('*_acc.txt'))
        audfiles = sorted(glob.glob('*_aud.txt'))
        allfiles = sorted(glob.glob('*_all.txt'))
        
        files = allfiles[:-1]+accfiles[:-1]+audfiles[:-1]
        
        os.chdir('..') 
        
        for f in files:
            print source+f, dest+f
            copyfile(source+f, dest+f)
            os.remove(source+f)
            
        time.sleep(wait)

if __name__ == '__main__':
    source = sys.argv[1]
    dest = sys.argv[2]
    main(source,dest)