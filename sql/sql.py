import  numpy               as np
import dbapi
import  time
#arguments
import numpy as np, cv
import cv2


#SERVER_ADRESS='hdbspatial.wdf.sap.corp'
#SERVER_ADRESS='10.18.206.186'
SERVER_ADRESS='10.68.88.71'
SERVER_PORT=30015
USER_NAME='System'
#PASSWORD='iiThai5e'
PASSWORD='Manager1'

#connect to hana database
conn=dbapi.connect(SERVER_ADRESS,SERVER_PORT,USER_NAME,PASSWORD)
cursor=conn.cursor()

#SCHEME  = "ESA_VECTOR_TEST"
SCHEME  = "ESA_EXP"
#SCHEME  = "ESA_VECTOR_EXP_NEW"
VECTOR_DATA = "NDVI_VECTOR"
#META = "NDVI_META"
BLOB_DATA = "NDVI_BLOB"
PRODUCT_DATA = "PRODUCT_DATA"

def exec_query(query):
    # print query
    try:
        cursor.execute(query)
    except Exception,ex:
        print ex

# Reference to Product Details

def drop_product_data():
    query = \
    "DROP TABLE " + SCHEME + "." + PRODUCT_DATA + " CASCADE;"
    exec_query(query)

def create_product_data():
    query = \
        "CREATE COLUMN TABLE " + SCHEME + "." + PRODUCT_DATA + " (\n\t\
        METADATA_ID " + "bigint NOT NULL PRIMARY KEY GENERATED " \
        + "ALWAYS AS IDENTITY,\n\t\
        PRODUCT_NAME " + "varchar(80),\n\t\
        UTM_ZONE " + "varchar(6)\n\t\
        );\
        "

    exec_query(query)

def insert_product_data(p_name, utm):

    query = \
    "INSERT INTO "          + SCHEME + "." + PRODUCT_DATA + " (\n\t\
    PRODUCT_NAME,\n\t\
    UTM_ZONE\n\t\
    )"                      + " VALUES (\'%s\',\'%s\');" % (p_name, utm)
    exec_query(query)
    exec_query("(SELECT MAX(METADATA_ID) FROM %s.%s)" % (SCHEME, PRODUCT_DATA))
    m_id = cursor.fetchone()[0]
    return m_id

# BLOB Approach

def drop_blob_data():
    query = \
    "DROP TABLE " + SCHEME + "." + BLOB_DATA + " CASCADE;"
    exec_query(query)

def create_blob_data():
    query = \
    "CREATE COLUMN TABLE "  + SCHEME + "." + BLOB_DATA + " (\n\t\
    VALUE_ID "              + "bigint NOT NULL PRIMARY KEY GENERATED " \
                            + "ALWAYS AS IDENTITY,\n\t\
    METADATA_ID "           + "bigint REFERENCES " + SCHEME + "." + PRODUCT_DATA \
                            + "(METADATA_ID),\n\t\
    NDVI "            + "BLOB\n\
    );\
    "
    exec_query(query)

def insert_blob(data, m_id, g_id):

    temp = "/home/sayon/workspace_eo/experiment_products/temporary/"
    tiff_path=temp
    tiff_filename="granule_"+str(g_id)+".tiff"

    t1 = time.time()
    cv2.imwrite(tiff_path+tiff_filename, data)
    t2 = time.time()
    t_create= (t2 - t1)
    print "BLOB:- TIFF Creation Time: %f seconds" % t_create

    t1 = time.time()
    cursor.execute("\
                INSERT INTO " + SCHEME + "." + BLOB_DATA + "(\
                METADATA_ID, \
                NDVI) \
                VALUES (?,?)", [m_id, open(tiff_path+tiff_filename, 'rb').read()])
    t2 = time.time()
    t_insert = (t2 - t1)
    print "BLOB:- Insertion Time: %f seconds" % t_insert

    return [t_create, t_insert]

# Vectorization Approach

def drop_vector_data():
    query = \
    "DROP TABLE " + SCHEME + "." + VECTOR_DATA + " CASCADE;"
    exec_query(query)

#def create_vector_data():
#    query = \
#    "CREATE COLUMN TABLE "  + SCHEME + "." + VECTOR_DATA + " (\n\t\
#    VALUE_ID "              + "bigint NOT NULL PRIMARY KEY GENERATED " \
#                            + "ALWAYS AS IDENTITY,\n\t\
#    METADATA_ID "           + "bigint REFERENCES " + SCHEME + "." + PRODUCT_DATA \
#                            + "(METADATA_ID),\n\t\
#    NDVI "            + "smallint\n\
#    ) PARTITION BY HASH (VALUE_ID) PARTITIONS 32;\
#    "
#    exec_query(query)

def create_vector_data():
    query = \
    "CREATE COLUMN TABLE "  + SCHEME + "." + VECTOR_DATA + \
        "(METADATA_ID BIGINT REFERENCES " + SCHEME + "." + PRODUCT_DATA+ "(METADATA_ID), " \
        "PIXEL_INDEX BIGINT, " \
        "NDVI SMALLINT) " \
    "PARTITION BY RANGE (METADATA_ID) " \
        "(" \
            "PARTITION 1 <= VALUES < 10, " \
            "PARTITION 10 <= VALUES <  20, " \
            "PARTITION 20 <= VALUES <  30, " \
            "PARTITION 30 <= VALUES <  40, " \
            "PARTITION 40 <= VALUES <  50, " \
            "PARTITION 50 <= VALUES <  60, " \
            "PARTITION 60 <= VALUES <  70, " \
            "PARTITION 70 <= VALUES <  80, " \
            "PARTITION 80 <= VALUES <  90, " \
            "PARTITION 90 <= VALUES <  100 " \
        ");"
    exec_query(query)

def insert_vector(data, m_id):

    flatten_data = data.flatten()
    print "Inserting %i values .. wait.. :" % (10980 * 10980)

    t1 = time.time()
    batch_entry(flatten_data, m_id, SCHEME, VECTOR_DATA)
    t2 = time.time()
    print "%f seconds" % (t2 - t1)

def insert_vector_chunks(data, m_id):

    pos=1
    flatten_data=data.flatten()
    chunk_size = 100000
    last = 0.0
    count=0
    t=0
    #print "inserting NDVI (int16) and Metadata in chunk size of %i .." % chunk_size
    #print "Vectorization: Total chunks: %i:" % ((10980 * 10980) / chunk_size)
    print "Vectorization:- Inserting Values"


    #print pixel_index

    while last < len(flatten_data):

       count=count+1
       pixel_index = list(range(pos, pos+ chunk_size))
       chunk_ar = flatten_data[int(last):int(last + chunk_size)]

       data = zip([m_id]*len(pixel_index), pixel_index, chunk_ar)
       t1 = time.time()
       cursor.executemany("\
            INSERT INTO " + SCHEME  + "." + VECTOR_DATA + "(\
            METADATA_ID, \
            PIXEL_INDEX, \
            NDVI) \
            VALUES (?,?,?)", data)
       t2 = time.time()
       t=t+(t2-t1)

       #print "chunk %i inserted" % (count)
       last += chunk_size
       pos += chunk_size

    print "Vectorization:- Insertion Time: %f seconds" % t
    return t

#def batch_entry(arr, m_id, scheme, table):
    # insert data batch entry
#    data = [(m_id, value) for value in arr]
#    if len(data) != 0:
#        cursor.executemany("\
#            INSERT INTO " + scheme + "." + table + "(\
#            METADATA_ID, \
#            NDVI) \
#            VALUES (?,?)", data)
