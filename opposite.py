
from collections import defaultdict
from geo import geo_split
from meta_data_safecam import get_gps
import glob
import pandas as pd
import os
import folium 
# from config import  rootpaths, extension, exclude, include , highlight
from config_loader import load_config
cfg = load_config()

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
    m = maps(0.001,2.4)
    startpos = []
    json_view = {}
    counter ={}
    mm=None
    df = {"video":[],"lane":[],"remark":[]}
    for x in videos:
        base = os.path.basename(x)
        if base in seen:
            continue
        seen.add(base)

        try:

            df,_ = get_gps(x)
            
            df = df[df["Position"]!='N0.00000E0.00000']
            df=df.drop_duplicates(subset=['Position'])
            df.reset_index(inplace=True)
            
            position=[(posi,fra,tim) for posi,fra,tim in zip(df["Position"],df["Frame"],df["Time"])]
            fr2time = {fra:tim for fra,tim in zip(df["Frame"],df["Time"])}
            position=compress_pos(position)
            
            startpos.append([geo_split(position[0][0]),x])
            json_view[x]=[[]]
            #counter[x] = {"blue":0,"green":0}
            


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
            time = position[xx][2]
            
            # csvss["video"].append(x)
            # csvss["Position"].append(A)
            # break
            if A == B:
                continue
            # print(A,B)
            manhdis = abs(A[0]-B[0])+abs(A[1]-B[1])
            if manhdis > 0.006:
                continue
            blue = m.addline(A[0],A[1],B[0],B[1],f"{x}",stfr,endfr)
            if mm is  None:
                mm = folium.Map(location=A, zoom_start=8)
            if blue:
                folium.PolyLine(locations=[A,B],opacity=0.7,smooth_factor=0.5, color='blue').add_to(mm)
                #counter[x]["blue"] +=1
                folium.CircleMarker(A,popup=folium.Popup(f"{x}[{time},{stfr}]"),**{'radius':2,'fill':True,'opacity':1,'color' : 'blue'}).add_to(mm)
            else:
                folium.PolyLine(locations=[A,B],opacity=0.7,smooth_factor=0.5, color='green').add_to(mm)
                #counter[x]["green"] +=1
                folium.CircleMarker(A,popup=folium.Popup(f"{x}[{time},{stfr}]"),**{'radius':2,'fill':True,'opacity':1,'color' : 'green'}).add_to(mm)

                if json_view[x][-1]:
                    # lastfr = json_view[x][-1][1]
                    if stfr -lastfr == 0:
                        json_view[x][-1][1] = f"{time}_{endfr}"
                    else:
                        json_view[x].append([f"{time}_{stfr}",f"{time}_{endfr}"])
                else:
                    json_view[x][-1]=[f"{time}_{stfr}",f"{time}_{endfr}"]
                lastfr =endfr

    for i in startpos:
        folium.CircleMarker(i[0],popup=folium.Popup(str(i[1])),**{'radius':1,'fill':True,'opacity':1,'color' : 'red'}).add_to(mm)

            
    # for x in counter:
    #     df["video"].append(x.split("=")[-1])
    #     df["lane"].append("Blue" if counter[x]["blue"] > counter[x]["green"] else "Green")
    #     df["remark"].append(counter[x])
    import json
    with open("results/directional.json", "w") as f:
        json.dump(json_view, f, indent=4) # indent for pretty-printing

    with open(f"results/directional.html","w") as f:
        f.write(str(mm._repr_html_()))
    webbrowser.open("results/directional.html")
    # pd.DataFrame(df).to_csv("results/bluegreen_videos.csv")

if __name__ == "__main__":
    import glob
    videos = list(glob.glob("/run/user/1000/gvfs/smb-share:server=anton.local,share=roadis_phase4/ml_support/Qatar oct-2025/Green Zone/GREEN Zone Main Roads ( 12 &13-Oct-2025)/**/*.MP4",recursive=True))
    main(videos)
    # i=m.getall()

    # # if len(i[0])==0:
    # #     continue
    # print("got all",len(i[0]),len(i[1]),i[0][0])
    # counter ={}
    # df = {"video":[],"lane":[],"remark":[]}

    # m = folium.Map(location=i[0][0][0:2], zoom_start=8)
    # seen_vid = set()
    # for index,x in enumerate(i[0]):
    #     folium.PolyLine(locations=[x[0:2],x[2:4]],opacity=0.7,smooth_factor=0.5, color='blue').add_to(m)

    #     counter[x[4]]["blue"] +=1
    #     # if x[4] not in seen_vid or 1:
    #     seen_vid.add(x[4])

    #     folium.CircleMarker(x[0:2],popup=folium.Popup(str(x[4:-1])),**{'radius':2,'fill':True,'opacity':1,'color' : 'blue'}).add_to(m)
    # for index,x in enumerate(i[1]):

    #     counter[x[4]]["green"] +=1

    #     folium.PolyLine(locations=[x[0:2],x[2:4]],opacity=0.7,smooth_factor=0.5, color='green').add_to(m)

    #     if index % 4 ==0:
    #         folium.CircleMarker(x[0:2],popup=folium.Popup(str(x[4:-1])),**{'radius':2,'fill':True,'opacity':1,'color' : 'green'}).add_to(m)
    #     if json_view[-1]:
    #         json_view
    # for i in startpos:
    #     folium.CircleMarker(i[0],popup=folium.Popup(str(i[1])),**{'radius':1,'fill':True,'opacity':1,'color' : 'red'}).add_to(m)
    # for x in counter:
    #     df["video"].append(x.split("=")[-1])
    #     df["lane"].append("Blue" if counter[x]["blue"] > counter[x]["green"] else "Green")
    #     df["remark"].append(counter[x])

    # with open(f"results/directional.html","w") as f:
    #     f.write(str(m._repr_html_()))
    # webbrowser.open("results/directional.html")
    # pd.DataFrame(df).to_csv("results/bluegreen_videos.csv")
