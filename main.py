from  geoexperiemnts import *

source_path = '/run/media/sayon/geo_services/downloader/PRODUCT/S2/A/2016/06/21'
unzip_source = '/home/sayon/workspace_eo/experiment_products/products/drought_india_product/test'
temp = '/home/sayon/workspace_eo/experiment_products/temporary/'
output_path='/home/sayon/workspace_eo/experiment_products/'

compute_distinct(source_path, temp, output_path)

generate_formats(source_path, temp, output_path)

insertNdviInHana(source_path, temp, output_path)

timeNdviComputation(source_path, temp, output_path)

select_statement("ESA_EXP", "NDVI_VECTOR", "NDVI_BLOB", "NDVI_VALUE", "METADATA_ID")

getTime_RetrieveNdviVectorAndBlobFromHana('10.68.88.71', 30015, 'System', 'Manager1', CSV_PATH)

ndvi_as_json(unzip_source, output_path)
ndvi_as_csv(source_path, temp, output_path)