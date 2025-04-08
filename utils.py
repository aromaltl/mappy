from geo import geo_split
import glob
import pandas as pd
from config import  rootpaths, extension, exclude, include 
import os
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
filterd_videos = get_videos()