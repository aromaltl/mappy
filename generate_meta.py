
import pandas as pd
from geo import geo_split
from meta_data_safecam import get_gps
import glob
import pandas as pd
import os
from utils import compress_pos, filterd_videos
import json

from config_loader import load_config

videos = filterd_videos
meta = {}
seen = set()
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
        position=[[geo_split(posi)] for posi in df["Position"]]
        position=compress_pos(position)
        # position=[geo_split(i[0]) for i in position]
    except Exception as ex:
        print(ex)
        continue
    meta[base.replace(".MP4","")] = [x[0] for x in position ]

with open("results/metadata.json","w") as f:
    json.dump(meta, f, indent=4)


spcl = {"video_names": [x for x in meta]}

with open("results/special_videos.json","w")  as f:
    json.dump(spcl, f, indent=4)


    
    
    
    