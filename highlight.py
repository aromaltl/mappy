
from collections import defaultdict
from geo import geo_split
import glob
import pandas as pd
import os
import folium 
from config import  rootpaths, extension, exclude, include ,scope , highlight
from folium import plugins
from meta_data_safecam import get_gps
from utils import compress_pos, plotkmz

import webbrowser


def main(videos):


    segments=[]
    seen = set()
    print("total videos",len(videos))
    duplicate = 0
    m = None 
    for x in videos:
        base = os.path.basename(x)
        if base in seen:
            continue
        seen.add(base)
        # vid = x.replace(".MP4",".csv")
        try:

            df,_ = get_gps(x)
            df = df[df["Position"]!='N0.00000E0.00000']
            df = df.drop_duplicates(subset=['Position'])
            df.reset_index(inplace=True)

            position = [(posi,fra) for posi,fra in zip(df["Position"],df["Frame"] )]
            position = compress_pos(position)

        except Exception as ex:
            if '[Errno 2]'  in str(ex):
                continue

            print(ex)
            continue
        color = '#009BFF'
        rad =2
        for light in highlight:
            if light in x:
                color = '#FF25De'
                rad =3

        
        for xx in range(len(position)-1):
            A=geo_split(position[xx][0])
            B=geo_split(position[xx+1][0])
            stfr =int(position[xx][1])
            endfr = int(position[xx+1][1])


            
            if m is None:
                m = folium.Map(location=A, zoom_start=8)

            if xx==0:
                folium.CircleMarker(A,popup=folium.Popup(str(x)),**{'radius':rad,'fill':True,'opacity':1,'color' : color}).add_to(m)
            if A == B:
                continue

            if abs(A[0]-B[0])+abs(A[1]-B[1]) > 0.06:
                continue
            folium.PolyLine(locations=[A,B],opacity=0.7,smooth_factor=0.5, color=color).add_to(m)
    if m is not None:
        lines = plotkmz(scope)
        for line in lines:
            folium.PolyLine(line, color='green').add_to(m)
        with open("results/highlight.html","w") as f:
            f.write(str(m._repr_html_()))
        webbrowser.open("results/highlight.html")
