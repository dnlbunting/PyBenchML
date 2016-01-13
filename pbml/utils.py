from hashlib import sha224

def filehash(file):
    hasher = sha224()
    with open(file, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return(hasher.hexdigest())
