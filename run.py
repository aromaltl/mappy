import highlight
import overlaps
import opposite
import multiprocessing
import os
from utils import filterd_videos
os.makedirs("results",exist_ok=True)

print("videos filtered")


p1 = multiprocessing.Process(target=opposite.main, args=(filterd_videos,))
p2 = multiprocessing.Process(target=overlaps.main, args=(filterd_videos,))
p3 = multiprocessing.Process(target=highlight.main, args=(filterd_videos,))
# opposite.main(filterd_videos[:])
# overlaps.main(filterd_videos[:])
# highlight.main(filterd_videos[:])
p1.start()
p2.start()
p3.start()
p1.join()
p2.join()
p3.join()
