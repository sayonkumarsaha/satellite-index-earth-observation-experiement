import base64
import codecs
import csv
import cv
import cv2
import glob
import h5py
import json
import numpy as np
import os
import shutil
import time
import zipfile
from datetime import datetime
from osgeo import gdal

import sql

os.environ["HDF5_DISABLE_VERSION_CHECK"] = "2"

from geoparsing.granule import Granule
from geoparsing.band import Band
from geoparsing.product import Product

from geoprocessing import *
from geopersistence import *
from sql import *
from geovisualizing import *


def quantize_value_array(array):
    origin_lower_bound = -1.0
    origin_upper_bound = 1.0
    origin_range = origin_upper_bound - origin_lower_bound

    dest_invalid_value = -32768
    dest_lower_bound = -32767
    dest_upper_bound = 32767
    dest_range = dest_upper_bound - dest_lower_bound
    factor = dest_range / origin_range

    return (((array - origin_lower_bound) * factor) + dest_lower_bound).astype(int)




def getTime_RetrieveNdviVectorAndBlobFromHana(SCHEME, VECTOR_DATA, BLOB_DATA, NDVI_COL_NAME, META_COL_NAME):

    vector_query = "SELECT " + NDVI_COL_NAME + "FROM " + SCHEME + "." + VECTOR_DATA + " WHERE " + META_COL_NAME + "= 1;"
    blob_query = "SELECT " + NDVI_COL_NAME + "FROM " + SCHEME + "." + BLOB_DATA + " WHERE " + META_COL_NAME + "= 1;"
    """
    # prepare a cursor object using cursor() method
    cursor = connection.cursor()
    # execute the SQL query using execute() method.
    cursor.execute("select name_first, name_last from address")
    # fetch all of the rows from the query
    data = cursor.fetchall()
    """
    t1 = time.time()
    exec_query(vector_query)
    t2 = time.time()
    print "Vector Query: %f milli-seconds" % ((t2 - t1) * 1000)

    t1 = time.time()
    exec_query(blob_query)
    t2 = time.time()
    print "BLOB Query: %f milli-seconds" % ((t2 - t1) * 1000)





def generate_formats(source_path, temp, output_path):
    count = 0
    slno = 4119
    os.mkdir(temp)

    with open(csv_path + "stat_301_315.csv", 'wb') as csvfile:
        stat_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        stat_writer.writerow(
            ['GranuleNumber', 'ProductNumber', 'Time_ProductUnzip', 'GranuleID', 'Time_NDVICompute', 'Format',
             'Time_Store',
             'Time_Load', 'Size_MB'])

        for subdir, dirs, files in os.walk(source_path):

            for file in files:
                count += 1

                if (count > 300):
                    print "Extracting Product %i .." % count
                    t1_ex = time.time()
                    file_path = os.path.join(subdir, file)
                    zfile = zipfile.ZipFile(file_path)
                    zfile.extractall(temp)
                    t2_ex = time.time()
                    t_ex = t2_ex - t1_ex
                    print "Product %s Time: %f s" % (count, (t2_ex - t1_ex))
                    product = Product(temp)
                    cnt = 0

                    for g_id in product.granules_ids:
                        filename = "Product_" + str(count) + "_Granule_" + str(g_id) + "_NDVI"

                        cnt = cnt + 1
                        slno = slno + 1
                        g = product.get_granule(g_id)

                        t1_ndvi = time.time()
                        ndvi = get_ndvi_as_array(g)
                        quantisized_ndvi = np.array(quantize_value_array(ndvi), dtype=np.uint16)
                        t2_ndvi = time.time()
                        t_ndvi = t2_ndvi - t1_ndvi

                        t_render_png = render_image(quantisized_ndvi, output_path + filename, ".png")
                        t_load_png = loading(output_path + filename, ".png")
                        size_png = get_size(output_path + filename, ".png")
                        stat_writer.writerow(
                            [slno, count, t_ex, g_id, t_ndvi, 'png', t_render_png, t_load_png, size_png])

                        t_render_tiff = render_image(quantisized_ndvi, output_path + filename, ".tiff")
                        t_load_tiff = loading(output_path + filename, ".tiff")
                        size_tiff = get_size(output_path + filename, ".tiff")
                        stat_writer.writerow(
                            [slno, count, t_ex, g_id, t_ndvi, 'tiff', t_render_tiff, t_load_tiff, size_tiff])

                        t_render_jp2 = render_image(quantisized_ndvi, output_path + filename, ".jp2")
                        t_load_jp2 = loading(output_path + filename, ".jp2")
                        size_jp2 = get_size(output_path + filename, ".jp2")
                        stat_writer.writerow(
                            [slno, count, t_ex, g_id, t_ndvi, 'jpeg2000', t_render_jp2, t_load_jp2, size_jp2])

                        t_render_h5 = render_image(quantisized_ndvi, output_path + filename, ".h5")
                        t_load_h5 = loading(output_path + filename, ".h5")
                        size_h5 = get_size(output_path + filename, ".h5")
                        stat_writer.writerow([slno, count, t_ex, g_id, t_ndvi, 'hdf5', t_render_h5, t_load_h5, size_h5])

                shutil.rmtree(temp)
                os.mkdir(temp)


def render_image(vector, file_path, extension):
    if extension == ".h5":
        t1 = time.time()
        with h5py.File(file_path + extension, 'w') as hf:
            hf.create_dataset('granule_ndvi', data=vector, compression="gzip", compression_opts=9)
        t2 = time.time()
    else:
        t1 = time.time()
        cv2.imwrite(file_path + extension, vector)
        t2 = time.time()
    # print extension+ " Render Time: %f s" % (t2 - t1)
    return (t2 - t1)


def get_size(file_path, extension):
    bytes = float(os.path.getsize(file_path + extension))
    mb = float(bytes / (pow(2, 20)))
    # print extension+ " Size: %f MB" % mb
    return mb


def loading(file_path, extension):
    if extension == ".h5":
        t1 = time.time()
        with h5py.File(file_path + extension, 'r') as hf:
            np_data = np.array(hf.get('granule_ndvi'))
        t2 = time.time()
        # print np_data
    else:
        t1 = time.time()
        np_data = cv2.imread(file_path + extension)
        t2 = time.time()
    # print extension+ " Load Time: %f s" % (t2 - t1)
    return (t2 - t1)


def insertNdviInHana(source_path, temp, output_path):
    count = 0
    sl_no = 0
    p_name = ""

    drop_tables()
    create_tables()

    with open(output_path + "vector_insertion_time.csv", 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GranuleNumber', 'Time_VectorInsert'])

        for subdir, dirs, files in os.walk(source_path):
            for file in files:
                count += 1
                print "Extracting Product %i .." % count
                file_path = os.path.join(subdir, file)
                zfile = zipfile.ZipFile(file_path)
                zfile.extractall(temp)
                p = Product(temp)

                for file in os.listdir(temp):
                    p_name = file

                sqlinsert_product_ndvi(p, p_name[:-5], writer, sl_no)
                shutil.rmtree(temp)

def create_tables():
    sql.create_meta_data()
    sql.create_product_data()
    sql.create_vector_data()
    sql.create_blob_data()

def drop_tables():
    sql.drop_meta_data()
    sql.drop_vector_data()
    sql.drop_blob_data()
    sql.drop_product_data()


def timeNdviComputation(source_path, temp, output_path):
    with open(csv_path + "ndvi_time.csv", 'wb') as csvfile:
        ndvi_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ndvi_writer.writerow(
            ['GranuleNumber', 'Time_Load_B4', 'Time_Load_B8', 'Time_ComputeNDVI', 'Time_QuantizeNDVI',
             'Time_TotalNDVI'])
        count = 0

        for subdir, dirs, files in os.walk(source_path):

            for file in files:
                count += 1
                print "Extracting Product %i .." % count
                file_path = os.path.join(subdir, file)
                zfile = zipfile.ZipFile(file_path)
                zfile.extractall(temp)
                product = Product(temp)
                c = 0

                for g_id in product.granules_ids:
                    c = c + 1
                    print "NDVI for Granule %i .." % c
                    g = product.get_granule(g_id)
                    get_ndvi_timer(c, g, ndvi_writer)

                shutil.rmtree(temp)


def sql_performance(SERVER_ADRESS, SERVER_PORT, USER_NAME, PASSWORD, CSV_PATH):

    conn = dbapi.connect(SERVER_ADRESS, SERVER_PORT, USER_NAME, PASSWORD)
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(\"METADATA_ID\") "
                   "FROM \"ESA_EXP\".\"PRODUCT_DATA\"; ")
    max = cursor.fetchone()[0]

    with open(csv_path + "vector_load_time.csv", 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GranuleNumber', 'Time_Load_Vector'])

        for i in range(1, max + 1):

            for i in range(1, 2):
                print loadtime_blob(i, temp)
                blob_writer.writerow([i, loadtime_blob(i, temp)])
                print "loadtime_vector(i) %i" % loadtime_vector(i)
                writer.writerow([i, loadtime_vector(i)])

    size = 40000
    low = 1
    ndvi = []
    limit = 10980 * 10980

    while low < limit:
        high = low + size

        t1 = time.time() * 1000
        cursor.execute("SELECT \"NDVI\" "
                       "FROM \"ESA_EXP\".\"NDVI_VECTOR\" "
                       "WHERE \"METADATA_ID\" = 1 AND \"PIXEL_INDEX\" >= " + str(
            low) + " AND \"PIXEL_INDEX\" <= " + str(high) + " ;")
        low = high + 1
        t2 = time.time() * 1000
        a = (t2 - t1)
        print "cursor.execute(SELECT %i values) %i milli-seconds" % (size, a)

        t1 = time.time() * 1000
        result = cursor.fetchall()
        t2 = time.time() * 1000
        b = (t2 - t1)
        print "cursor.fetchall(): %i milli-seconds" % b

        t1 = time.time() * 1000
        ndvi.extend(result)
        t2 = time.time() * 1000
        c = (t2 - t1)
        print "ndvi.extend(result) %i milli-seconds" % c

        print "total %i seconds" % (a + b + c)
        print " "

def loadtime_blob(meta_id, temp):
    os.mkdir(temp)
    filename = str(meta_id) + "_blob_load_test_.tiff"
    t1 = time.time()
    cursor.execute("SELECT \"NDVI\" "
                   "FROM \"ESA_EXP\".\"NDVI_BLOB\" "
                   "WHERE \"METADATA_ID\" = " + str(meta_id) + ";")
    open(temp + filename, 'wb').write(cursor.fetchone()[0])
    np_data = cv2.imread(temp + filename)
    t2 = time.time()
    shutil.rmtree(temp)
    return (t2 - t1)

def loadtime_vector(meta_id):
    t1 = time.time()
    cursor.execute("SELECT \"NDVI\" "
                   "FROM \"ESA_EXP\".\"NDVI_VECTOR\" "
                   "WHERE \"METADATA_ID\" = " + str(meta_id) + ";")
    t2 = time.time()
    select_t = (t2 - t1)
    print "select_t %i seconds" % select_t

    flat_ndvi = []
    t1 = time.time()
    for result in ResultIter(cursor):
        flat_ndvi.extend(result)
        if len(flat_ndvi) % 1000000 == 0:
            print len(flat_ndvi)
    t2 = time.time()
    fetch_t = (t2 - t1)
    print "fetch_1D_t %i" % fetch_t

    return (select_t + fetch_t)

def ResultIter(cursor, arraysize=1000000):
    'An iterator that uses fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result











def compute_distinct(source_path, temp, output_path):
    t_all1 = time.time()
    f = open(output_path + "distinct_exp.txt", 'w')
    distinct = []
    count = 0
    os.mkdir(temp)
    with open(csv_path + "distinct.csv", 'wb') as csvfile:
        distinct_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        distinct_writer.writerow(['GranuleNumber', 'DistinctValueStatus'])

        for subdir, dirs, files in os.walk(source_path):
            for file in files:
                count += 1
                print "Starting Product %i .." % count
                file_path = os.path.join(subdir, file)
                zfile = zipfile.ZipFile(file_path)
                zfile.extractall(temp)
                product = Product(temp)
                cnt = 0
                tp1 = time.time()

                for g_id in product.granules_ids:
                    cnt = cnt + 1
                    print "Working on Product %s Granule %s" % (count, cnt)
                    f.write("Working on Product %s Granule %s \n" % (count, cnt))
                    g = product.get_granule(g_id)
                    ndvi = get_ndvi_as_array(g)
                    quantisized_ndvi = quantize_value_array(ndvi)
                    unique_ndvi = set(quantisized_ndvi)
                    distinct.extend(unique_ndvi)
                    distinct = set(distinct)
                    distinct = list(distinct)
                    print "Current Distinct Length: %i " % len(distinct)
                    f.write("Current Distinct Length: %i \n" % len(distinct))

                tp2 = time.time()
                print "Product Time: %f seconds" % (tp2 - tp1)
                shutil.rmtree(temp)
                print "\n"
                f.write("\n")

    t_all2 = time.time()

    print "Final Distinct Length: %i " % len(distinct)
    print "Total Time: %f seconds" % (t_all2 - t_all1)
    f.write("Final Distinct Length: %i \n" % len(distinct))
    f.write("Total Time: %f seconds \n" % (t_all2 - t_all1))

    f.close()



def ndvi_as_json(unzip_source, output_path):

    dest_path = output_path+"test.json"
    product = Product(unzip_source)
    cnt = 1

    for g_id in product.granules_ids:
        g = product.get_granule(g_id)
        ndvi = get_ndvi_as_array(g)
        quantisized_ndvi = quantize_value_array(ndvi).flatten()

        t1 = time.time()
        l = quantisized_ndvi.tolist()
        t2 = time.time()
        print (t2 - t1)
        t1 = time.time()

        json.dump(l, codecs.open(dest_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)
        t2 = time.time()
        print (t2 - t1)
        t1 = time.time()

        np_data = np.array(json.loads(codecs.open(dest_path, 'r', encoding='utf-8').read()))
        t2 = time.time()
        print (t2 - t1)
        if cnt == 1:
            exit()



def ndvi_as_csv(source_path, csv_path):

    with open(csv_path + "b4_vector.csv", 'wb') as csvfile:
        b4_vector_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        b4_vector_writer.writerow(['Index', 'Value'])

        with open(csv_path + "b8_vector.csv", 'wb') as csvfile:
            b8_vector_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            b8_vector_writer.writerow(['Index', 'Value'])

            with open(csv_path + "ndvi_vector.csv", 'wb') as csvfile:
                ndvi_vector_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                ndvi_vector_writer.writerow(['Index', 'Value'])

                product = Product(source_path)
                C = 10980

                INVALID_NORMALZED_DIFFERENCE_VALUE = -2
                for g_id in product.granules_ids:
                    granule = product.get_granule(g_id)

                    band_4 = granule.get_band("B04").as_array(xsize=C, ysize=C).astype(float)
                    flat_band_4 = band_4.flatten()
                    print "doing band_4"
                    i = 0
                    for value in flat_band_4:
                        i = i + 1
                        b4_vector_writer.writerow([i, value])

                    band_8 = granule.get_band("B08").as_array(xsize=C, ysize=C).astype(float)
                    flat_band_8 = band_8.flatten()
                    print "doing band_8"
                    i = 0
                    for value in flat_band_8:
                        i = i + 1
                        b8_vector_writer.writerow([i, value])

                    band_difference = band_8 - band_4
                    band_sum = band_8 + band_4

                    mask = np.ones(band_8.shape, dtype=bool)
                    mask[band_sum == 0] = False

                    with np.errstate(divide='ignore', invalid='ignore'):
                        nd_array = np.divide(band_difference, band_sum)
                    nd_array[~mask] = INVALID_NORMALZED_DIFFERENCE_VALUE

                    ndvi = nd_array.flatten()

                    print "doing ndvi"
                    i = 0
                    for value in ndvi:
                        i = i + 1