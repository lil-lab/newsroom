import bz2    as _bz2
import gzip   as _gzip
import lzma   as _lzma
import os     as _os
import shlex  as _shlex
import shutil as _shutil
import ujson  as _json

_open = open

_has = {
    "zcat":  not not _shutil.which("zcat"),
    "bzcat": not not _shutil.which("bzcat"),
    "xzcat": not not _shutil.which("xzcat"),
}


class open(object):

    """

    Simple tool for manipulating compressed JSON line data files.
    Supports gzip, bzip2, xz/lzma and uncompressed JSON line input.
    Can be used as a standard object, or in a "with" context.

    Uses faster system tools for expanding files when available.

    This results in approximately:
        - 30x read speed increase for lzma
        - 20x read speed increase for gzip
        - 5x read speed increase for bzip2

    Arguments:

        path (str) - path of JSON lines file

    Keywords:

        fast (bool) - read with zcat, bzcat, or xzcat (default = True)
        gzip (bool) - encode and decode with gzip (default = False)
        bzip (bool) - encode and decode with bzip2 (default = False)
        xz (bool)   - encode and decode with xz/lzma (default = False)
        level (int) - compression level for gzip and bzip2 (default = 9)

    """

    def __init__(

            self,
            path,
            fast  = True,
            gzip  = False,
            bzip  = False,
            xz    = False,
            level = 9,

            ):

        self.path     = path

        self.fast     = fast

        self.use_gzip = gzip
        self.use_bzip = bzip
        self.use_xz   = xz

        self.level    = level

        self.is_read  = None
        self.file     = None

        # Allow only one compressor.

        assert sum([gzip, bzip, xz]) <= 1

        # Fast only if system supports it.

        self.fast &= (gzip and _has["zcat"]) \
            or (bzip and _has["bzcat"]) \
            or (xz and _has["xzcat"])


    def _readfile(self):

        if not self.is_read:

            self.close()

        self.is_read = True

        if self.use_gzip:

            if self.fast:

                quoted = _shlex.quote(self.path)
                self.file = _os.popen("zcat < " + quoted)

            else:

                self.file = _gzip.open(
                    self.path, mode = "rt",
                    compresslevel = self.level)

        elif self.use_bzip:

            if self.fast:

                quoted = _shlex.quote(self.path)
                self.file = _os.popen("bzcat < " + quoted)

            else:

                self.file = _bz2.open(
                    self.path, mode = "rt",
                    compresslevel = self.level)

        elif self.use_xz:

            if self.fast:

                quoted = _shlex.quote(self.path)
                self.file = _os.popen("xzcat < " + quoted)

            else:

                self.file = _lzma.open(
                    self.path, mode = "rt")

        else:

            self.file = _open(self.path, "r")

        return self.file


    def _writefile(self):

        if self.is_read is True:

            self.close()

        self.is_read = False

        if self.use_gzip:

            self.file = _gzip.open(
                self.path, mode = "at",
                compresslevel = self.level)

        elif self.use_bzip:

            self.file = _bz2.open(
                self.path, mode = "at",
                compresslevel = self.level)

        elif self.use_xz:

            self.file = _lzma.open(
                self.path, mode = "at")

        else:

            self.file = _open(self.path, "a+")

        return self.file


    def __del__(self):

        # Close file on cleanup.

        self.close()


    def __enter__(self):

        # Called when entering "with" context.

        return self


    def __exit__(self, *_):

        # Called when exiting "with" context.

        self.close()


    def __iter__(self):

        # Return the readlines generator.

        return self.readlines()


    def __len__(self):

        length = 0

        for line in self._readfile():

            length += 1

        return length


    def close(self):

        """

        Close the file.

        """

        if self.file:

            self.file.close()


    def delete(self):

        """

        Delete the file contents on disk.

        """

        if self.is_read is True:

            self.close()

        self.is_read = False

        if self.use_gzip:

            self.file = _gzip.open(
                self.path, mode = "wt",
                compresslevel = self.level)

        elif self.use_bzip:

            self.file = _bz2.open(
                self.path, mode = "wt",
                compresslevel = self.level)

        elif self.use_bzip:

            self.file = _lzma.open(
                self.path, mode = "wt")

        else:

            self.file = _open(self.path, "w")

        self.file.close()
        self.is_read = None


    def readlines(self, ignore_errors = False):

        """

        Read a sequence of lines (as a generator).

        Yields:

            individual JSON-decoded entries

        """

        if not ignore_errors:

            for line in self._readfile():

                yield _json.loads(line)

        else:

            for ln, line in enumerate(self._readfile()):

                try:

                    yield _json.loads(line)

                except:

                    print("Decoding error on line", ln)
                    continue


    def read(self):

        """

        Read the entire file into memory.

        Returns:

            list of JSON-decoded entries

        """

        return list(self.readlines())


    def appendline(self, entry):

        """

        Write a single line to the file.

        Arguments:

            entry (object) - JSON-encodable object

        """

        f = self._writefile()
        f.write(_json.dumps(entry) + "\n")


    def append(self, entries):

        """

        Append an entire list of lines to an existing file.

        Arguments:

            entry (iterable[object]) - iterable of JSON-encodable objects

        """


        for entry in entries:
            self.appendline(entry)


    def write(self, entries):

        """

        Write list of lines to file, overwriting the original data.

        Arguments:

            entry (iterable[object]) - iterable of JSON-encodable objects

        """

        self.delete()
        self.append(entries)


# Convenience functions.


def read(*args, **kwargs):

    """

    Read a full uncompressed JSON lines file into memory.

    """

    kwargs["bzip"] = False
    kwargs["gzip"] = False
    kwargs["xz"]   = False

    with open(*args, **kwargs) as f:

        return f.read()


def bzread(*args, **kwargs):

    """

    Read a full bzip2-compressed JSON lines file into memory.

    """

    kwargs["bzip"] = True
    kwargs["gzip"] = False
    kwargs["xz"]   = False

    with open(*args, **kwargs) as f:

        return f.read()


def gzread(*args, **kwargs):

    """

    Read a full gzip-compressed JSON lines file into memory.

    """

    kwargs["bzip"] = False
    kwargs["gzip"] = True
    kwargs["xz"]   = False

    with open(*args, **kwargs) as f:

        return f.read()


def xzread(*args, **kwargs):

    """

    Read a full xz/lzma-compressed JSON lines file into memory.

    """

    kwargs["bzip"] = False
    kwargs["gzip"] = False
    kwargs["xz"]   = True

    with open(*args, **kwargs) as f:

        return f.read()
