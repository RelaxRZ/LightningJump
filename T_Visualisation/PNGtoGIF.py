import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from datetime import datetime, timedelta
from visualisation_func import spec_year, polygon_func, ICCG_Collect, plot_func
from PIL import Image
import glob

frames = []
imgs = glob.glob("2014-11-27_Visualisation/*.png")
imgs = sorted(imgs, key=lambda x: int(x.split('map_')[-1].split('.')[0]))

for i in imgs:
    print(i)
    new_frame = Image.open(i)
    frames.append(new_frame)

frames[0].save('test.gif', format = 'GIF', append_images = frames[1:], save_all = True, duration = 300, Loop = 0)