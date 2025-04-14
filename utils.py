from geo import geo_split
import glob
import pandas as pd
from config import  rootpaths, extension, exclude, include 
import os
from xml.etree import ElementTree as ET
def compress_pos(x):
    n =[ x[0]]
    ratio = None
    for i in range(1,len(x)-1):
        la1,ln1 = geo_split(n[-1][0])
        la2,ln2 = geo_split(x[i][0])
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
    for rootpath in rootpaths:
        for ext in extension:
            videos += list(glob.glob(os.path.join(rootpath,"**",f"*{ext}"),recursive=True))
    
    videos=filter_videos(videos,include,exclude)
    videos.sort()
    return videos


def plotkmz(kmz_files ):
    import zipfile
    import simplekml
    lines = []
    for kmz_file in kmz_files:
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
    return lines






filterd_videos = get_videos()
