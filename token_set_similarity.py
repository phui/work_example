# author : Pik-Mai Hui (huip@indiana.edu)
# This script is run on 16-core Linux with 40GB RAM, niced with -n 9
# This script produces 10 workers. Be ware of memory consumption since each worker
#   requires a standalone copy of word2vec model in memory
# This script is heavily CPU-bound
# This script relays on optimized numpy and scipy installations to support Gensim

# This script takes lines in the format
#       uid \t set([tokens...]) \n
#   in the files in the input directory and calculate average word similarity
#   among pairs of tokens in the set, deserialize by eval()

# Usage: python tokens_set_similarity.py -d input_dir
#   required: - input files in input_dir are assumed to be gzipped
#             - no other file is allowed to be in input_dir except input gzips

from __future__ import print_function


import os
import sys
import re
import gc
import gensim
import gzip
import threading
import numpy as np
from scipy import misc
from optparse import OptionParser
from multiprocessing import Pool
from nltk.tokenize import TweetTokenizer
from itertools import combinations



# settings
num_process = 10



def absoluteFilePaths(directory):
    ''' Iterator of absolute paths of files in a directory '''
    for dirpath,_,filenames in os.walk(directory):
        for f in filenames:
             yield os.path.abspath(os.path.join(dirpath, f))



def process_target(arguments):
    process_idx, file_lst = arguments

    # snippet for handling unicode issues in Gensim Word2Vec model during loading
    word2vec = gensim.models.Word2Vec
    def any2unicode(text, encoding='utf8', errors='strict'):
        """Convert a string (bytestring in `encoding` or unicode), to unicode."""
        if isinstance(text, unicode):
            return text
        return unicode(text.replace('\xc2\x85', '<newline>'), encoding, errors=errors)
    gensim.utils.to_unicode = any2unicode

    # read word2vec model as a global variable, accessible to all threads
    model = word2vec.load_word2vec_format('glove.twitter.27B.100d.txt',
            binary=False)

    for filename in file_lst:
        file_content = None
        try:
            f = gzip.open(filename, 'rb')
            # cache the whole file, it isn't that big (~10MB)
            file_content = f.read()
        except IOError as e:
            print('[Warning]: cannot open file: skip file %s' % filename, file=sys.stderr)
            continue
        if file_content is None or len(file_content) == 0:
            # check content read
            print('[Warning]: failed to read content: skip file %s' % filename, file=sys.stderr)
            continue

        file_content = file_content.split('\n')
        with open('%d.tsv' % process_idx, 'w', 10**6) as output: # ~1MB buffer output
            for line in file_content:
                # parse content of line into uid and list of posts
                uid, tokens = tuple(line.split('\t'))
                tokens = set(
                    token for token in eval(tokens) # posts by that user
                    if token in model
                )

                num_tokens = len(tokens)
                if num_tokens > 1:
                    # calculate average similarity of all pairs of tokens
                    num_pairs = misc.comb(num_tokens, 2)
                    ave_sim = sum(
                        model.similarity(w1, w2)
                        for w1, w2, in combinations(tokens, 2)
                    ) / num_pairs

                    print('%s\t%d\t%f' % (uid, num_tokens, ave_sim),
                            file=output)
                else:
                    # not enough tokens to be statistically significant
                    # print default -1.0
                    print('%s\t%d\t%f' % (uid, num_tokens, -1.0), file=output)

    return 1



# parse argv
parser = OptionParser()
parser.add_option("-d", "--dir", dest="dir",
    help="input directory DIR", metavar="DIR")
options, args = parser.parse_args()

# find all filepath in input directory
files = list(absoluteFilePaths(options.dir))
# partition files in a list of even-size sublists
file_lsts = enumerate(files[i::num_process] for i in range(num_process))

# create and run threads
pool = Pool(processes=num_process)
result = pool.map(process_target, file_lsts)
# wait for all processes to complete

# all completed, program ends

