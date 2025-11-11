
from geo import geo_split
from meta_data_safecam import get_gps
import glob
import pandas as pd
import os
import pickle

from config_loader import load_config
cfg = load_config()
from utils import compress_pos ,plotkmz
import folium      
from folium import plugins
import webbrowser

def filtervideos(videos,highlight):

    for x in videos:
        OLD =True
        for y in highlight:
            if y in x:
                OLD=False
        yield OLD, x

def getPos(x):
    position =None
    try:
        df,_ = get_gps(x)
        df = df[df["Position"]!='N0.00000E0.00000']
        df=df.drop_duplicates(subset=['Position'])
        df.reset_index(inplace=True)
        
        
        position=[(posi,fra,tim) for posi,fra,tim in zip(df["Position"],df["Frame"],df["Time"])]
        position=compress_pos(position)

    except Exception as ex:
        # if '[Errno 2]'  in str(ex):
        print(ex)
        return None
    return position





def main(videos):
    
    from uniquemapping import maps, distance
    segments=[]
    overlappings = set()
    seen = set()
    # with open("save_videolist.txt","r") as f:
    # videos= eval(f.read())

    print(len(videos),"total videos")
    videos.sort()
    m =None
    duplicate = 0
    ovrlapped = set()
    mm = maps(0.00013,0.60)
    videoss =set()
    ovlpseg = {}

    total = 0

    for old,x in filtervideos(videos,cfg.highlight):
        # print(old,x)
        base = os.path.basename(x)
        if base in seen:
            continue
        videoss.add(x)
        seen.add(base)
        ovlpseg[x]=[[]]

        # vid = x.replace(".MP4",".csv")
        position =getPos(x)

        if position is  None or len(position)==0:
            continue
        if m is None:
            m = folium.Map(location=geo_split(position[0][0]), zoom_start=8)
            lines = plotkmz(cfg.scope)
            for line in lines:
                folium.PolyLine(line, color="#3A6600").add_to(m)

        
        prev = 100,100
        for xx in range(len(position)-1):
            A=geo_split(position[xx][0])
            B=geo_split(position[xx+1][0])
            stfr =int(position[xx][1])
            endfr = int(position[xx+1][1])
            time = position[xx][2]
            if A == B:
                continue
            total +=distance(A[0],A[1],B[0],B[1])
            
            
            if old:
                folium.PolyLine(locations=[A,B],opacity=0.7,smooth_factor=0.5, color='blue').add_to(m)
                if abs(prev[0]-A[0])+abs(prev[1]-A[1]) > 0.04:
                    prev=A
                    folium.CircleMarker(A,popup=folium.Popup(f"{x}[{time},{stfr}]"),**{'radius':6,'fill':True,'opacity':1,'color' : 'blue'}).add_to(m)
                mm.forceaddline(A[0],A[1],B[0],B[1],x,stfr,endfr)

            else:      
                if not mm.addline(A[0],A[1],B[0],B[1],x,stfr,endfr):
                    duplicate+=distance(A[0],A[1],B[0],B[1])
                    folium.PolyLine(locations=[A,B],opacity=0.7,smooth_factor=0.5, color='red').add_to(m)
                    folium.CircleMarker(A,popup=folium.Popup(f"{x}[{time},{stfr}]"),**{'radius':2,'fill':True,'opacity':1,'color' : 'red'}).add_to(m)
                    if ovlpseg[x][-1]:
                        if stfr - lastfr ==0:
                            ovlpseg[x][-1][1] =f"{time}_{endfr}"
                        else:
                            ovlpseg[x].append([f"{time}_{stfr}",f"{time}_{endfr}"])
                    else:
                        
                        ovlpseg[x][-1] = [f"{time}_{stfr}",f"{time}_{endfr}"]
                    lastfr = endfr


                else:
                    folium.PolyLine(locations=[A,B],opacity=0.7,smooth_factor=0.5, color="#8327FC").add_to(m)
                    folium.CircleMarker(A,popup=folium.Popup(f"{x}[{time},{stfr}]"),**{'radius':2,'fill':True,'opacity':1,'color' : "#8327FC"}).add_to(m)
        folium.CircleMarker(geo_split(position[0][0]),popup=folium.Popup(f"{x}"),**{'radius':1,'fill':True,'opacity':1,'color' : 'white'}).add_to(m)
    title_html = f'<h3 align="center" style="font-size:12px"><b>Total KMs : {round(total,2)} , Duplicated KMs : {round(duplicate,2)}</b></h3>'
    m.get_root().html.add_child(folium.Element(title_html))

    overlap = set( x for x in mm.get())
    non_videoss = list(videoss- overlap)
    finaldf = pd.DataFrame({"videos":non_videoss+list(overlap),"overlap":["No"]*len(non_videoss)+["Yes"]*len(overlap)})
    finaldf["videos"]=finaldf["videos"].apply(os.path.basename)
    finaldf.to_csv(f"results/overlap_video.csv")


    # total_uniq+=dis_uniq
    # total_dupli+=dis_dupl
    import json
    with open("results/overlap.json", "w") as f:
        json.dump(ovlpseg, f, indent=4) # indent for pretty-printing
    with open(f"results/overlap.html","w") as f:
        f.write(str(m._repr_html_()))
    webbrowser.open("results/overlap.html")
    del mm

if __name__ == "__main__":

    main()


