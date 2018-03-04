
# module for saving data into daTabase

import  numpy               as np
from    geoprocessing import get_ndvi_as_array
import  time
import  sql


def sqlinsert_product_ndvi(product, p_name, writer, sl_no):
    INVALID_NORMALZED_DIFFERENCE_VALUE = -100000000.0
    count = 0
    total_ndvi=[]

    for g_id in product.granules_ids:

        count = count + 1
        sl_no = sl_no + 1
        print "Granule %s:" % count
        g = product.get_granule(g_id)
        ndvi = get_ndvi_as_array(g)
        m_id = sql.insert_product_data(p_name, str(g_id))

        #meta_data = g.get_band("B04").get_meta_data()
        #m_id= sql.insert_meta(meta_data)

        #t_blob= sql.insert_blob(np.array(quantize_value_array(ndvi), dtype=np.uint16), m_id, g_id)
        t_vector= sql.insert_vector_chunks(quantize_value_array(ndvi), m_id)

        #stat_writer.writerow([sl_no, t_blob[0], t_blob[1], t_vector])
        writer.writerow([sl_no, t_vector])

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
        result = ((((array - origin_lower_bound) *dest_range) / origin_range) + dest_lower_bound).astype(
    int)
        #print result

        return result