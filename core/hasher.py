import hashlib
import os
import tempfile


def hash_file(path):
    sha1 = hashlib.sha1()

    with open(path, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def atomic_copy(src, dst):
    """Copy file atomically using temp file + rename."""
    dst_dir = os.path.dirname(dst)
    fd, tmp = tempfile.mkstemp(dir=dst_dir)
    try:
        with open(src, "rb") as fsrc:
            with os.fdopen(fd, "wb") as fdst:
                while True:
                    chunk = fsrc.read(65536)
                    if not chunk:
                        break
                    fdst.write(chunk)
        os.replace(tmp, dst)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
