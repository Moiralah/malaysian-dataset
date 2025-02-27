# !pip3 install ujson

from tqdm import tqdm
import malaya
import re
import pickle
import ujson as json
import os
import sys

filename = sys.argv[1]
try:
    device = sys.argv[2]
except:
    device = ''

os.environ['CUDA_VISIBLE_DEVICES'] = device

transformer = malaya.translation.en_ms.transformer(check_gpu=False)


def cleaning(string):
    return re.sub(r'[ ]+', ' ', string).strip()


class Pointer:
    def __init__(self, filename):
        self.filename = filename
        self.index = 0

    def _save(self):
        with open(self.filename, 'wb') as fopen:
            pickle.dump(self.index, fopen)

    def increment(self):
        self.index += 1
        self._save()

    def load(self):
        if not os.path.exists(self.filename):
            return
        with open(self.filename, 'rb') as fopen:
            self.index = pickle.load(fopen)


pointer = Pointer(f'{filename}.pickle')
pointer.load()
index = 0

file = open(f'{filename}.translated', 'a')

with open(filename) as fopen:
    dataset = json.load(fopen)

for l in tqdm(dataset):
    if index >= pointer.index:
        left, right = l['left'], l['right']
        ms = transformer.greedy_decoder([left, right])
        l.update({'ms_left': ms[0], 'ms_right': ms[1]})
        d = json.dumps(l)
        file.write(f'{d}\n')
        file.flush()

        pointer.increment()
    index += 1

file.close()
