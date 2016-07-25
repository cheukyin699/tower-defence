# File: jsonutils
# Description: Rewrites some json functions to make it comments-friendly.
#              Supports comments starting with '//'.
import json, re

pat = re.compile('(//.*\n)')

def loads(s):
    s = re.sub(pat, '', s)
    return json.loads(s)

def load(fp):
    txt = fp.read()
    fp.close()
    return loads(txt)

if __name__ == '__main__':
    jsontest = '''
    {
        // This is a comment
        "hello": 1,
        "world": 2    // This is another comment
    }
    '''
    print(loads(jsontest))
