import hashlib


def hash_md5(filepath):
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as file:
        for chunk in iter(lambda: file.read(128 * md5_hash.block_size), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
