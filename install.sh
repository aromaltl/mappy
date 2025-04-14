wget takeleap.in/ml-gui/Image-ExifTool-12.22.zip
unzip Image-ExifTool-12.22.zip
chmod -R 777 .
c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) dirmap.cpp -o dirmap$(python3-config --extension-suffix)
c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) uniquemapping.cpp -o uniquemapping$(python3-config --extension-suffix)
