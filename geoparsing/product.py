
from    os.path     import  os, join
from    granule     import  Granule
import  time

def _substr(s, n, split_string):
    """ Recursively get string between n-th and (n+1)-th occurence. Useful
        for getting band information (bandinf) such as polarisation VV, VH, ...
    """
    if n == 0:
        return s[:s.find(split_string)]
    else:
        return _substr(s[s.find(split_string)+1:], n-1, split_string)

class Product():
    """ Get a product, which is initialized with paths to granules. """

    def __init__(self, path):

        # file name of product, select only files which contain .SAFE and are n
        p_fname = [f for f in os.listdir(path)][0]

        # set path of product
        self._path     = join(path, p_fname)

        # path to granules
        self._granules_path = path + "/" + p_fname + "/GRANULE"

        # file names of granules in granules path
        granules_fnames = [g for g in os.listdir(self._granules_path) if g.find(".xml") == -1]

        # paths to granules
        self._granules_paths = {_substr(g_fname, 9, "_"): os.path.join(\
        self._granules_path, g_fname) for g_fname in granules_fnames}

        self._granules = {}

    @property
    def id(self):
        return self._id

    @property
    def path(self):
        return self._path

    @property
    def granules_ids(self):
        return self._granules_paths.keys()

    @property
    def granules_paths(self):
        return self._granules_paths

    def get_granule(self, granule_id):
        return Granule(self, granule_id)
