
from    os.path import join, os
from    band    import Band
#from    mask    import GranuleMask

# sorting list entries regardless of upper or lower case:
_sort_alphabetically = lambda x,y: cmp(x.lower(), y.lower())

# used for output on terminal:
_CHUNK = "\n#################################################################\n"

class Granule():
    """
    Granule is used for selecting several Granules, e.g. depending on time to show
    a dynamic overview over a specific region.

    Parameters
    ----------
    mission_id:    string
        sentinel identifier such as S1
    path_main:      string
        path to folder with sentinel data sets
    sentinel_nr:    integer
        selected entry number in folder of .SAFE files
    granule_id:     string
        selected identifier in GRANULES/IMG_DATA (for S2 such as
        "T31UGT") or in measurement folder (for S1 such as "IW1")
        (see below "Select path to Granule data" for details)
    """

    def __init__(self, product, granule_id):

        self._bands_path    = None
        self._bands_paths   = {}
        self._product       = product

        # select granule with chosen granule id
        self._path = product.granules_paths[granule_id]

        # set granule id of instance
        self._granule_id = granule_id

        # paths to bands accessible with granule id
        path_bands = join(self._path, "IMG_DATA")
        bands_fnames = [b for b in os.listdir(path_bands) if b.find(".xml") == -1]
        bands_ids = [b[-7:-4] for b in bands_fnames]
        self._bands_paths   = {bid: join(path_bands, bfn) for bid, bfn in \
        zip(bands_ids, bands_fnames)}

    @property
    def xml_path(self):
        """ Return path to xml file in granule folder."""
        fname = [f for f in os.listdir(self._path) if ".xml" in f][0]
        return join(self._path, fname)

    @property
    def bands_paths(self):
        return self._bands_paths

    @property
    def band_ids(self):
        return self._bands_paths.keys()

    def get_band(self, band_id):
        return Band(self, band_id)
