# File: jsonutils
# Description: Rewrites some json functions to make it comments-friendly.
#              Supports comments starting with '//'.
import json, re

pat = re.compile('(//.*\n)')

def loads(s, encoding=None, cls=None, object_hook=None, parse_float=None, parse_int=None,
          parse_constant=None):
    s = re.sub(pat, '', s)
    return json.loads(s, encoding, cls, object_hook, parse_float,
                      parse_int, parse_constant)

def load(fp, encoding=None, cls=None, object_hook=None, parse_float=None, parse_int=None,
         parse_constant=None):
    txt = fp.read()
    fp.close()
    return loads(txt, encoding, cls, object_hook, parse_float, parse_int, parse_constant)

if __name__ == '__main__':
    jsontest = '''
    {
        // This is a comment
        "hello": 1,
        "world": 2    // This is another comment
    }
    '''
    print loads(jsontest)
