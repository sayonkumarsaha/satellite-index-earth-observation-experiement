#source_path='/home/sayon/workspace_eo/experiment_products/folder'
#source_path='/mnt/sat1/downloader/PRODUCT/S2/A/2016/06/21'
source_path='/home/sayon/workspace_eo/experiment_products/max_min'
#source_path='/run/media/sayon/geo_services/downloader/PRODUCT/S2/A/2016/06/21'

temp='/home/sayon/workspace_eo/experiment_products/temporary'
info_file='/home/sayon/workspace_eo/experiment_products/info_file.txt'

> $info_file

count=0

# granule=0
# total_granule=0
# avg_granule=0
# max_granule=0
# min_granule=0

filesize_zip_size=0
total_zip_size=0
avg_zip_size=0
max_zip_size=0
min_zip_size=0

filesize_unzip_size=0
total_unzip_size=0
avg_unzip_size=0
max_unzip_size=0
min_unzip_size=0

filesize_noband_zip_size=0
total_noband_zip_size=0
avg_noband_zip_size=0
max_noband_zip_size=0
min_noband_zip_size=0

filesize_noband_unzip_size=0
total_noband_unzip_size=0
avg_noband_unzip_size=0
max_noband_unzip_size=0
min_noband_unzip_size=0

for f in $source_path/*.zip

do
  zip_name=${f#$source_path/}
  unzip_name=${zip_name/zip/SAFE}

  let count+=1
  echo  "Product $count " >> $info_file




  #zipped files

  filesize_zip_size=$(du -sb "$f" | cut -f1) #$(stat -c%s "$f")
  echo "zip_size = $filesize_zip_size bytes." >> $info_file
  let total_zip_size+=$filesize_zip_size

  if [ $count -eq 1 ]
  	then
  	max_zip_size=$filesize_zip_size
  	min_zip_size=$filesize_zip_size

  elif [  $max_zip_size < $filesize_zip_size]
  	then
  	max_zip_size=$filesize_zip_size

  elif [ $filesize_zip_size < $min_zip_size ]
  	then
  	min_zip_size=$filesize_zip_size
  fi

  #unzipped files

  unzip $f -d $temp/

  filesize_unzip_size=$(du -sb "$temp/$unzip_name" | cut -f1) #$(stat -c%s "$temp/$unzip_name")
  echo "unzip_size = $filesize_unzip_size bytes." >> $info_file
  let total_unzip_size+=$filesize_unzip_size

  if [ $count -eq 1 ]
  	then
  	max_unzip_size=$filesize_unzip_size
  	min_unzip_size=$filesize_unzip_size

  elif [  $max_unzip_size < $filesize_unzip_size]
  	then
  	max_unzip_size=$filesize_unzip_size

  elif [ $filesize_unzip_size < $min_unzip_size ]
  	then
  	min_unzip_size=$filesize_unzip_size
  fi

  #granules

  let total_granule+=find $temp/$unzip_name/GRANULE/ -mindepth 1 -maxdepth 1 -type d | wc -l

  #no bands unzipped files

  find $temp/$unzip_name -type f -name "*.jp2" -exec rm -f {} \;

  filesize_noband_unzip_size=$(du -sb "$temp/$unzip_name" | cut -f1) #$(stat -c%s "$temp/$unzip_name")
  echo "noband_unzip_size = $filesize_noband_unzip_size bytes." >> $info_file
  let total_noband_unzip_size+=$filesize_noband_unzip_size

  if [ $count -eq 1 ]
  	then
  	max_noband_unzip_size=$filesize_noband_unzip_size
  	min_noband_unzip_size=$filesize_noband_unzip_size

  elif [  $max_noband_unzip_size < $filesize_noband_unzip_size]
  	then
  	max_noband_unzip_size=$filesize_noband_unzip_size

  elif [ $filesize_noband_unzip_size < $min_noband_unzip_size ]
  	then
  	min_noband_unzip_size=$filesize_noband_unzip_size
  fi
 #no band zipped files

  zip -r  $temp/$zip_name $temp/$unzip_name

  filesize_noband_zip_size=$(du -sb "$temp/$zip_name" | cut -f1) #$(stat -c%s "$temp/$zip_name")
  echo "noband_zip_size= $filesize_noband_zip_size bytes." >> $info_file
  let total_noband_zip_size+=$filesize_noband_zip_size

  if [ $count -eq 1 ]
  	then
  	max_noband_zip_size=$filesize_noband_zip_size
  	min_noband_zip_size=$filesize_noband_zip_size

  elif [  $max_noband_zip_size < $filesize_noband_zip_size]
  	then
  	max_noband_zip_size=$filesize_noband_zip_size

  elif [ $filesize_noband_zip_size < $min_noband_zip_size ]
  	then
  	min_noband_zip_size=$filesize_noband_zip_size
  fi

  rm -rf $temp/*

  echo '-----------------------' >> $info_file
done

let avg_zip_size=$total_zip_size/$count
let avg_unzip_size=$total_unzip_size/$count
let avg_noband_unzip_size=$total_noband_unzip_size/$count
let avg_noband_zip_size=$total_noband_zip_size/$count
#let avg_granule=$total_granule/$count

echo "Number of Products= $count" >> $info_file
echo '-----------------------' >> $info_file

echo 'zip_size' >> $info_file
echo '-----------------------' >> $info_file
echo "total= $total_zip_size bytes" >> $info_file
echo "avg= $avg_zip_size bytes" >> $info_file
echo "max= $max_zip_size bytes" >> $info_file
echo "min= $min_zip_size bytes" >> $info_file
echo '-----------------------' >> $info_file
echo 'unzip_size' >> $info_file
echo '-----------------------' >> $info_file
echo "total= $total_unzip_size bytes" >> $info_file
echo "avg= $avg_unzip_size bytes" >> $info_file
echo "max= $max_unzip_size bytes" >> $info_file
echo "min= $min_unzip_size bytes" >> $info_file
echo '-----------------------' >> $info_file
echo 'noband_zip_size' >> $info_file
echo '-----------------------' >> $info_file
echo "total= $total_noband_zip_size bytes" >> $info_file
echo "avg= $avg_noband_zip_size bytes" >> $info_file
echo "max= $max_noband_zip_size bytes" >> $info_file
echo "min= $min_noband_zip_size bytes" >> $info_file
echo '-----------------------' >> $info_file
echo 'noband_unzip_size' >> $info_file
echo '-----------------------' >> $info_file
echo "total= $total_noband_unzip_size bytes" >> $info_file
echo "avg= $avg_noband_unzip_size bytes" >> $info_file
echo "max= $max_noband_unzip_size bytes" >> $info_file
echo "min= $min_noband_unzip_size bytes" >> $info_file

# echo 'granule' >> $info_file
# echo '-----------------------' >> $info_file
# echo "total= $total_granule" >> $info_file
# echo "avg= $avg_granule" >> $info_file
# echo "max= $max_granule" >> $info_file
# echo "min= $min_granule" >> $info_file
# echo '-----------------------' >> $info_file
