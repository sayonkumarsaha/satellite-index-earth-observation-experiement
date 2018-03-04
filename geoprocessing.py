
import  numpy               as np
import time
# from    geoparsing.granule  import Granule
# from    geoparsing.band     import Band
#from    geoparsing.mask  import GranuleMask

# Allow division by zero
# np.seterr(divide='ignore', invalid='ignore')

C = 10980# for testing smaller sizes of granules 10980


#INVALID_NORMALZED_DIFFERENCE_VALUE = -100000000.0
#origin_invalid_value = INVALID_NORMALZED_DIFFERENCE_VALUE
#origin_lower_bound = -1.0
#origin_upper_bound = 1.0
#origin_range = origin_upper_bound - origin_lower_bound

#dest_invalid_value = -32768
#dest_lower_bound = -32767
#dest_upper_bound = 32767
#dest_range = dest_upper_bound - dest_lower_bound

#result=dest_invalid_value

#x= ((((result - dest_lower_bound))*origin_range)/dest_range)+origin_lower_bound
#print x

#INVALID_NORMALZED_DIFFERENCE_VALUE = -100000000.0
INVALID_NORMALZED_DIFFERENCE_VALUE = -1.00003051851

def print_array_status_percentage(counter, array_range):
    parts = 10.
    if counter % (array_range / parts) == 0:
        print "Processed %.02f %% of Data." % (counter / (array_range / 100. ) + parts)

def get_ndvi_as_array(granule, status_update = False):
    """ Return a 2-D array with NDVI values ranged from -1 to +1 and specific single """

    band_4 = granule.get_band("B04").as_array(xsize = C, ysize = C).astype(float)
    band_8 = granule.get_band("B08").as_array(xsize=C, ysize=C).astype(float)

    band_difference = band_8 - band_4
    band_sum = band_8 + band_4

    mask = np.ones(band_8.shape, dtype=bool)
    mask[band_sum == 0] = False

    with np.errstate(divide='ignore', invalid='ignore'):
        nd_array = np.divide(band_difference, band_sum)
    nd_array[~mask] = INVALID_NORMALZED_DIFFERENCE_VALUE

    return nd_array

def get_ndvi_timer(c, granule, ndvi_writer):
        """ Return a 2-D array with NDVI values ranged from -1 to +1 and specific single """

        t1_band_4 = time.time()
        band_4 = granule.get_band("B04").as_array(xsize=C, ysize=C).astype(float)
        t2_band_4 = time.time()
        t_band_4 = t2_band_4 - t1_band_4

        t1_band_8 = time.time()
        band_8 = granule.get_band("B08").as_array(xsize=C, ysize=C).astype(float)
        t2_band_8 = time.time()
        t_band_8 = t2_band_8 - t1_band_8


        t1_ndvi_compute = time.time()

        band_difference = band_8 - band_4
        band_sum = band_8 + band_4

        mask = np.ones(band_8.shape, dtype=bool)
        mask[band_sum == 0] = False

        with np.errstate(divide='ignore', invalid='ignore'):
            nd_array = np.divide(band_difference, band_sum)
        nd_array[~mask] = INVALID_NORMALZED_DIFFERENCE_VALUE

        t2_ndvi_compute = time.time()
        t_ndvi_compute = t2_ndvi_compute - t1_ndvi_compute

        t1_quant = time.time()
        quantisized_ndvi = np.array(quantize_value_array(nd_array), dtype=np.uint16)
        t2_quant = time.time()
        t_quant = t2_quant - t1_quant

        t_total= t_band_4 + t_band_8 + t_ndvi_compute + t_quant

        ndvi_writer.writerow([c, t_band_4, t_band_8, t_ndvi_compute, t_quant, t_total])
        #exit()

def quantize_value_array(array):

        #INVALID_NORMALZED_DIFFERENCE_VALUE = -100000000.0
        #origin_invalid_value = INVALID_NORMALZED_DIFFERENCE_VALUE
        origin_lower_bound = -1.0
        origin_upper_bound = 1.0
        origin_range = origin_upper_bound - origin_lower_bound

        dest_invalid_value = -32768
        dest_lower_bound = -32767
        dest_upper_bound = 32767
        dest_range = dest_upper_bound - dest_lower_bound

        result = np.full(array.shape, dest_invalid_value, int)
        #print result
        #result = ((((array[
                         #array != INVALID_NORMALZED_DIFFERENCE_VALUE] - origin_lower_bound) * dest_range) / origin_range) + dest_lower_bound).astype(
            #int)
        factor = dest_range / origin_range
        result = (((array - origin_lower_bound) * factor) + dest_lower_bound).astype(int)
        #print result

        return result




