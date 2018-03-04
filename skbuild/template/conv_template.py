import sys
import os

from numpy.distutils.conv_template import process_file

if __name__ == "__main__":
    fin, fout = sys.argv[1:3]

    try:
        os.makedirs(os.path.dirname(fout))
    except OSError:
        pass
    with open(fout, 'w+') as f:
        f.write(process_file(fin))
