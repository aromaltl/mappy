
from collections import defaultdict
from geo import geo_split
from meta_data_safecam import get_gps
import glob
import pandas as pd
import os
import folium 
from config import  rootpaths, extension, exclude, include , highlight
from folium import plugins

import webbrowser
from utils import compress_pos


def main(videos):
    from dirmap import maps
    segments=[]
    overlappings = set()
    seen = set()
    print("total videos",len(videos),)
    duplicate = 0
    ovrlapped = set()
    m = maps(0.00055,2.4)

    for x in videos:
        base = os.path.basename(x)
        if base in seen:
            continue
        seen.add(base)
        # print(x,"##")
        # if "2024_0613_140447" in x or  "2024_0627_122040" in x:
        #     print(x,"@#@#@#@#@#@#@#@#@#@#@------@#@#@#@#@#@#@#@#@#@")
        # vid = x.replace(".MP4",".csv")
        try:

            df,_ = get_gps(x)
            df = df[df["Position"]!='N0.00000E0.00000']
            df=df.drop_duplicates(subset=['Position'])
            df.reset_index(inplace=True)
            
            position=[(posi,fra) for posi,fra in zip(df["Position"],df["Frame"])]
            position=compress_pos(position)

        except Exception as ex:
            if '[Errno 2]'  in str(ex):
                continue

            print(ex)
            continue
        for xx in range(len(position)-1):
            A=geo_split(position[xx][0])
            B=geo_split(position[xx+1][0])
            stfr =int(position[xx][1])
            endfr = int(position[xx+1][1])
            # csvss["video"].append(x)
            # csvss["Position"].append(A)
            # break
            if A == B:
                continue
            # print(A,B)
            manhdis = abs(A[0]-B[0])+abs(A[1]-B[1])
            if manhdis > 0.006:
                continue
            m.addline(A[0],A[1],B[0],B[1],x,stfr,endfr)
    i=m.getall()

    # if len(i[0])==0:
    #     continue
    print("got all",len(i[0]),len(i[1]),i[0][0])
    counter ={}
    df = {"video":[],"lane":[],"remark":[]}

    m = folium.Map(location=i[0][0][0:2], zoom_start=8)
    seen_vid = set()
    for index,x in enumerate(i[0]):
        folium.PolyLine(locations=[x[0:2],x[2:4]],opacity=0.7,smooth_factor=0.5, color='blue').add_to(m)
        if x[4] not in counter:
            counter[x[4]]={"blue":0,"green":0}
        counter[x[4]]["blue"] +=1
        # if x[4] not in seen_vid or 1:
        seen_vid.add(x[4])

        folium.CircleMarker(x[0:2],popup=folium.Popup(str(x[4:-1])),**{'radius':2,'fill':True,'opacity':1,'color' : 'blue'}).add_to(m)
    for index,x in enumerate(i[1]):
        if x[4] not in counter:
            counter[x[4]]={"blue":0,"green":0}
        counter[x[4]]["green"] +=1
        # if x[4] not in seen_vid:

        folium.PolyLine(locations=[x[0:2],x[2:4]],opacity=0.7,smooth_factor=0.5, color='green').add_to(m)
        # else:
            # folium.PolyLine(locations=[x[0:2],x[2:4]],opacity=0.7,smooth_factor=0.5, color='#00FFFF').add_to(m)
        if index % 4 ==0:
            folium.CircleMarker(x[0:2],popup=folium.Popup(str(x[4:-1])),**{'radius':2,'fill':True,'opacity':1,'color' : 'green'}).add_to(m)

    for x in counter:
        df["video"].append(x.split("=")[-1])
        df["lane"].append("Blue" if counter[x]["blue"] > counter[x]["green"] else "Green")
        df["remark"].append(counter[x])

    with open(f"results/directional.html","w") as f:
        f.write(str(m._repr_html_()))
    webbrowser.open("results/directional.html")
    pd.DataFrame(df).to_csv("results/bluegreen_videos.csv")
