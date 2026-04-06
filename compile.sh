#!/bin/bash

echo "Compiling the map with all the carrier points:D"

echo "installing deps (this part may ask you for your password)"

sudo apt install gdal-bin -y

echo "compiling..."

python3 compile.py

echo "making the bugger a kml and kmz"

ogr2ogr -f KML isp_layers_2025.kml merged_isp_2025.json

zip isp_layers_2025.kmz isp_layers_2025.kml

echo "all done, thanks for using Cooper DAndillys little program, go to dandilly.com.au for extra things"

