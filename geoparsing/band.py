
import  os
import  numpy       as      np
from    osgeo       import  gdal

# used for output on terminal:
_CHUNK = "\n#################################################################\n"

class Band():
    """
    Band contains method for getting it as array. Extent of array can
    be initialized with subsize of whole band with parameters xsize, ysize.
    """

    def __init__(self, granule, band_id):
        """ Initialize a band with a granule instance."""

        if band_id not in granule.band_ids:
            print "Band ID not found."
            return -1
        self._granule           = granule
        self._path              = granule.bands_paths[band_id]
        self._ds                = gdal.Open(self._path)
        self._file_identifier   = self._path[self._path.rfind("/")+1:]

    def as_array(self, xsize = None, ysize = None):
        if xsize and ysize is not None:
            band = self._ds.GetRasterBand(1)
            return band.ReadAsArray(win_xsize=xsize, win_ysize=ysize).astype(np.float)
        else:
            return band.ReadAsArray().astype(np.float)

    def print_summary(self):
        """ Print meta data with gdalinfo as terminal output. """

        print _CHUNK,
        x = os.system("gdalinfo " + self._path)

    def get_meta_data(self):
        """
        Return meta information.

        Returns
        -------
        band_width:         integer
            width of band (pixels counted), e.g. 10980
        band_height:        integer
            height of band (pixels counted), e.g. 10980
        pixel size_x:       integer
            size of one pixel in meters such as 10 m/pxl or 20 m/pxl
        projection_name:    string
            name of projection such as WGS84
        upleft_coord_x:     float
            containing upper left x coordinate, e.g. 600000.0
        upleft_coord_y:     float
            containing upper left y coordinate
        creation_date:      string
            creation date with format described in underlying function
        """

        gt              = self._ds.GetGeoTransform()
        band_width      = self._get_band_size()[0]
        band_height     = self._get_band_size()[1]
        pixelsize       = self._get_pixelsize(gt)
        projection_name = self._get_prj_name(self._ds)
        upleft_coord_x  = self._get_upperleft_coordinate(gt)[0]
        upleft_coord_y  = self._get_upperleft_coordinate(gt)[1]
        creation_date   = self._get_creation_date()
        return band_width, band_height, pixelsize, projection_name, upleft_coord_x,\
            upleft_coord_y, creation_date

    def _get_band_size(self):
        """ Return band size as tuple with height y and width x. """
        x = self._ds.RasterXSize
        y = self._ds.RasterYSize
        return (x, y)

    def _get_creation_date(self):
        """
        Return creation date as string with format set by ESA (files).

        Returns
        -------
        creation_date:  string
            sensing start time and the sensing stop time of the first
            line of granule in date UTC time format with the date (YYYYMMDD) and
            time (HHMMSS) separated by a 'T' such as 20141104T134012.
        """

        f_id = self._file_identifier
        f_id_params = f_id.split("_")
        creation_date = None
        for param in f_id_params:
            if len(param) == 15 and param[8] == "T":
                creation_date = param
                return creation_date
        if creation_date == None:
            print("No creation date was found. Check if the format of the "
                "band file is set according to the user guide for S-2 data.")
            return -1

    def _get_pixelsize(self, gt):
        """
        Return the size of the pixels as int value, e.g. 20m, 30m, ...
        per pixel.

        Parameters
        ----------
        gt: list of size 6
            upper left coordinates and pixelsize/-direction

        Returns
        -------
        pixelsize: integer
            size of one pixel in meters such as 20 m/pxl or 40 m/pxl
        """

        w = abs(gt[1])
        h = abs(gt[5])

        if abs(w != h):
            print("Geometry of pixels might be non-quadratic. Read width as %i "
                "meters and height as %i meters") % (w, h)
            return -1
        else:
            pixelsize= abs(w)
            return pixelsize

    def _get_prj_name(self, ds):
        """
        Return the projection name of the granule file as string.

        Parameters
        ----------
        ds: datastream of a granule file, opened with gdal.Open("<PATH>")

        Returns
        -------
        name of projection such as WGS84
        """

        projection = ds.GetProjection()
        # get list in case more attributes - such as projection name - are needed
        projection_list = projection.split(",")
        substring = lambda s: s[s.find("\"")+1:s.rfind("\"")]

        if projection_list[0].find("PROJCS") == -1:
            print("Error: Either the projection information is missing in the meta"
                "data or the structure of the meta data is not as expected.")
            return -1
        elif projection.find("UNIT[\"metre") == -1:
            print ("Error: Expected metre as unit, but either no information about "
            "unit given or unit is not metre.")
            return -1
        else:
            return substring(projection_list[0])

    def _get_upperleft_coordinate(self, gt):
        """
        Return the upper left coordinate as 2-tupel.

        Parameters
        ----------
        gt: list of size 6
            upper left coordinates and pixelsize/-direction

        Returns
        -------
        upleft_coord:       integer 2-tupel
            containing upper left x and y coordinate
        """

        x = gt[0]
        y = gt[3]
        upleft_coord = (x, y)
        return upleft_coord
