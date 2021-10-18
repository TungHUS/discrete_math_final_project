from functools import reduce
import random, requests, io, time, threading, math, os
from PIL import Image
from os import listdir, getcwd, remove
from os.path import isfile, join

path = getcwd()

def getXY(lat,lng,zoom):
    tile_size = 256
    numTiles = 1 << zoom
    point_x = (tile_size / 2 + lng * tile_size / 360.0) * numTiles // tile_size
    sin_y = math.sin(lat * (math.pi / 180.0))
    point_y = ((tile_size / 2) + 0.5 * math.log((1 + sin_y) / (1 - sin_y)) * -(
    tile_size / (2 * math.pi))) * numTiles // tile_size
    return int(point_x), int(point_y)

def get_param(lat, lng, zoom, radius):
    x0 = lat + radius
    x1 = lat - radius
    y0 = lng - radius
    y1 = lng + radius
    a = getXY(x0, y0, zoom)
    b = getXY(x1, y1, zoom)
    return a[0], a[1], b[0] - a[0], b[1] - a[1]

def surf(start_x, x, start_y, y, zoom):
    s = random.choice([0,1,2,3])
    url = f'https://mt{s}.google.com/vt?lyrs=s&x=' + str(start_x + x) + '&y=' + str(start_y + y) + '&z=' + str(zoom)
    try:
        r = requests.get(url, timeout = 1)
        img = io.BytesIO(r.content)
        img = Image.open(img)
        print(f'suscessful load tile {x}-{y} from server {s}')
        return img
    except:
        print(f'fail to load tile {x}-{y} from server {s}')
        surf(start_x, x, start_y, y, zoom)

def load_img(start_x,start_y,sub_list,zoom):
    while len(sub_list) != 0:
        x,y = sub_list.pop(0)
        img = surf(start_x, x, start_y, y, zoom)
        try:
            map_img = Image.new('RGB', (256, 256))
            map_img.paste(img, (256, 256))
            del map_img
            img.save(path + f"/temporary fragment tiles/{start_x + x}-{start_y + y}.png")
        except:
            print(f'invalid image at position {x}-{y}')
            sub_list.append((x,y))
    print("This thread is done!")

def threading_load(start_x, start_y, tile_width, tile_height, zoom, thread_count = 30):
    tile_coors = reduce(lambda a,b: a + b , [[(i,j) for i in range(tile_width)] for j in range(tile_height)])
    random.shuffle(tile_coors)
    image_count = len(tile_coors)
    thread_list = []
    
    for i in range(thread_count):
        start = math.floor(i * image_count / thread_count) + 1
        end = math.floor((i + 1) * image_count / thread_count) + 1
        thread_list.append(threading.Thread(target=load_img, args= (start_x, start_y,tile_coors[start:end],zoom)))
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()
    del thread_list
    print("All done!")
    
def generateImage(object_name, tile_width, tile_height):
    file_names = [f for f in listdir(path + '/temporary fragment tiles') if isfile(join(path + '/temporary fragment tiles', f))]
    file_names = [x.replace(".png","").split("-") for x in file_names]
    map_img = Image.new('RGB', (256 * tile_width, 256 * tile_height))
    for index in file_names:
        img = Image.open(path + f'/temporary fragment tiles/{index[0]}-{index[1]}.png')
        map_img.paste(img,((int(index[0])-start_x)*256, (int(index[1])-start_y)*256))
        os.remove(path + f'/temporary fragment tiles/{index[0]}-{index[1]}.png')
    map_img.save(path + F"/data2/{object_name}.png")
    print("image generated!")

    
zoom = 20
start_x, start_y, tile_width, tile_height = get_param(21.11531221461225, 105.77236541678188, zoom, 0.015)
img = threading_load(start_x, start_y, tile_width, tile_height, zoom)
generateImage("test1", tile_width, tile_height)

