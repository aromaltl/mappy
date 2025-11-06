from geo import geo_split
import glob
import pandas as pd
from config import  rootpaths, extension, exclude, include 
import os
from xml.etree import ElementTree as ET
import json
from config_loader import load_config
cfg = load_config()
# def find_common_start(str1, str2, index =None):
#     if None
#     for i in range(min(len(str1), len(str2))):
#         if str1[i] == str2[i]:
#             j=i
#         else:
#             # Mismatch found, stop appending characters.
#             break
#     return j



def compress_pos(x):
    def _split(x):
        if type(x) is str:
            return geo_split(x)
        else:
            return x
    n =[ x[0]]
    ratio = None
    for i in range(1,len(x)-1):
        
        la1,ln1 = _split(n[-1][0])
        la2,ln2 = _split(x[i][0])


        dla = la1-la2
        dln = ln1-ln2
        diff = abs(dla) + abs(dln) 
        if diff < 0.0003 or diff > 0.05 :
            continue
        dln = 0.000001 if dln==0 else dln
        if ratio is None or ((diff  > 0.0032) or abs(ratio - (dla/dln)) > 0.05):
            ratio = dla/dln
            n.append(x[i])
    n.append(x[-1])
    return n

def filter_videos(videos,include,exclude):
    new = []  
    for ii in videos:
        cont =False
        for ex in exclude:
            if ex in ii:
                cont=True
                break
        if cont:
            continue
        for inc in include:
            if inc in ii:
                new.append(ii)
                break
    return new
    
def get_videos():
    videos = []
    seen =set()
    
    for rootpath in cfg.rootpaths:
        for ext in extension:
            videos += list(glob.glob(os.path.join(rootpath,"**",f"*{ext}"),recursive=True))
    
    videos=filter_videos(videos,cfg.include,cfg.exclude)
    videos.sort()
    return videos


def plotkmz(kmz_files ):
    import zipfile
    import simplekml
    lines = []
    for kmz_file in kmz_files:
        if ".kmz" in kmz_file:
            with zipfile.ZipFile(kmz_file, 'r') as z:
                kml_filename = [f for f in z.namelist() if f.endswith('.kml')][0]
                kml_data = z.read(kml_filename)
                root = ET.fromstring(kml_data)

                # KML namespace hack to work with default namespace
                ns = {'kml': 'http://www.opengis.net/kml/2.2'}

                # Step 3: Extract LineString coordinates
                
                for linestring in root.findall(".//kml:LineString", ns):
                    coords_text = linestring.find("kml:coordinates", ns).text.strip()
                    coords = []
                    for coord in coords_text.split():
                        lon, lat, *_ = map(float, coord.split(","))
                        coords.append((lat, lon))  # folium uses (lat, lon)
                    lines.append(coords)
        if ".json" in kmz_file:
            with open(kmz_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, value in data.items():
                    for v in value:
                        lines.append([(round(x[0],5),round(x[1],5)) for x in v])
    return lines
    

filterd_videos = get_videos()



