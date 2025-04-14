
from geo import geo_split
from meta_data_safecam import get_gps
import glob
import pandas as pd
import os
import pickle
from config import  rootpaths, extension, exclude, include , highlight
from utils import compress_pos
import folium      
from folium import plugins
import webbrowser



def main(videos):
    
    from uniquemapping import maps, distance
    segments=[]
    overlappings = set()
    seen = set()
    # with open("save_videolist.txt","r") as f:
    # videos= eval(f.read())

    print(len(videos),"total videos")
    videos.sort()
    duplicate = 0
    ovrlapped = set()
    mm = maps(0.00035,0.60)
    videoss =set()
    video_start = {}
    for x in videos:
        base = os.path.basename(x)
        if base in seen:
            continue
        videoss.add(x)
        seen.add(base)

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

            if A == B:
                continue
            # if (abs(A[0]-B[0])+abs(A[1]-B[1]) ) > 0.083:
            #     continue
            # print(A,B)
            if x not in video_start:
                video_start[x]=A

            mm.addline(A[0],A[1],B[0],B[1],x,stfr,endfr)
    i=mm.getall()

    if len(i[0])>0:
        
        print("got all",len(i[0]),len(i[1]),i[0][0])

        m = folium.Map(location=i[0][0][:2], zoom_start=8)
        seen_vid = set()
        dis_uniq = 0
        dis_dupl = 0

        # for lines in all_base[contractor]['lines']:
        #     lines.add_to(m)
        # for markrs in  all_base[contractor]['markers']:
        #     markrs.add_to(m)
        # red_seen = set()
        for x in i[1]:
            dis = distance(x[0],x[1],x[2],x[3])
            if dis > 0.5:
                continue
            dis_dupl+=dis
            if x[4] not in seen_vid:
                seen_vid.add(x[4])
                # folium.CircleMarker(x[0:2],popup=folium.Popup(str(x[4:])),**{'radius':7,'fill':True,'opacity':1,'color' : 'red'}).add_to(m)
                # red_seen.add(x[4])
            folium.PolyLine(locations=[x[0:2],x[2:4]],opacity=0.7,smooth_factor=0.5, color='red').add_to(m)
            folium.CircleMarker(x[0:2],popup=folium.Popup(str(x[4:])),**{'radius':6,'fill':True,'opacity':1,'color' : 'red'}).add_to(m)


            # m.get_root().html.add_child(folium.Element(title_html))
        seen_vid = set()
        for x in i[0]:
            folium.PolyLine(locations=[x[0:2],x[2:4]],opacity=0.7,smooth_factor=0.5, color='blue').add_to(m)
            dis = distance(x[0],x[1],x[2],x[3])
            if dis > 0.5:
                continue
            dis_uniq+=dis
        for x in video_start:

            folium.CircleMarker(video_start[x],popup=folium.Popup(x),**{'radius':2,'fill':True,'opacity':1,'color' : 'blue'}).add_to(m)
            # basename = os.path
            # if x[4] not in seen_vid:
            #     seen_vid.add(x[4])
            #     if x[4] in red_seen:
            #         pass
            #         # folium.CircleMarker(x[0:2],popup=folium.Popup(str(x[4:])),**{'radius':7,'fill':True,'opacity':1,'color' : 'red'}).add_to(m)
            #     else:
            #         folium.CircleMarker(x[0:2],popup=folium.Popup(str(x[4:])),**{'radius':3,'fill':True,'opacity':1,'color' : 'blue'}).add_to(m)



        title_html = f'<h3 align="center" style="font-size:12px"><b>Unique KMs : {round(dis_uniq,2)} , Duplicated KMs : {round(dis_dupl,2)}</b></h3>'
        m.get_root().html.add_child(folium.Element(title_html))

        overlap = set( x for x in mm.get())
        non_videoss = list(videoss- overlap)
        finaldf = pd.DataFrame({"videos":non_videoss+list(overlap),"overlap":["No"]*len(non_videoss)+["Yes"]*len(overlap)})
        finaldf["videos"]=finaldf["videos"].apply(os.path.basename)
        finaldf.to_csv(f"results/overlap_video.csv")


        # total_uniq+=dis_uniq
        # total_dupli+=dis_dupl
    with open(f"results/overlap.html","w") as f:
        f.write(str(m._repr_html_()))
    webbrowser.open("results/overlap.html")
    del mm


