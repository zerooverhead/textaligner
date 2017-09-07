
import subprocess
import os.path
from tempfile import NamedTemporaryFile
import re

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

re_pair = re.compile(
   """^\s*
        (\d+)   # left index
             \s+
        (\d+)       # right index
            \s+
        (-?\d+(:?\.\d+)) # align precision
       \s*$
   """,
   re.X | re.S)


def align_indexes(left_lang, left_text, right_lang, right_text):
    this_dir = os.path.dirname(__file__)
    dict_file_name = os.path.join(this_dir, 'dictionary', '{}-{}.dic'.format(left_lang, right_lang))
    if not os.path.exists(dict_file_name):
        raise RuntimeError('No dictionary for languages {}/{}'.format(left_lang, right_lang))

    left_file = NamedTemporaryFile(delete=False)
    left_file.write(left_text.encode(encoding='utf-8'))
    left_file.close()

    right_file = NamedTemporaryFile(delete=False)
    right_file.write(right_text.encode(encoding='utf-8'))
    right_file.close()

    exe_name = os.path.join(this_dir, 'hunalign', 'hunalign.exe')

    process = subprocess.Popen([exe_name, '-utf', dict_file_name, left_file.name, right_file.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    if process.returncode != 0:
        raise RuntimeError('Hunalign exited with error ' + str(process.returncode))
    process_stdout = process.communicate()[0]
    contents = process_stdout.decode('utf8').strip()
    for line in contents.split('\n'):
        m = re_pair.match(line)
        if m:
            left_index, right_index, quality = int(m.group(1)), int(m.group(2)), float(m.group(3))
            yield left_index, right_index, quality


def align(left_lang, left_text, right_lang, right_text):
    iterator = align_indexes(left_lang, left_text, right_lang, right_text)
    for start, end in pairwise(chain(iterator, [len()]))


def test():
    with open('1jp.txt', encoding='utf-8') as left, \
         open('1ru.txt', encoding='utf-8') as right:
         align('ja', left.read(), 'ru', right.read())

if __name__ == "__main__":
    test()


