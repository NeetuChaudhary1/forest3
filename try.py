import numpy as np
import cv2
from PIL import Image
import urllib.parse
import urllib.request
import io
from math import log, exp, tan, atan, pi, ceil
from place_lookup import find_coordinates

EARTH_RADIUS = 6378137
EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0

def latlontopixels(lat, lon, zoom):
    mx = (lon * ORIGIN_SHIFT) / 180.0
    my = log(tan((90 + lat) * pi / 360.0)) / (pi / 180.0)
    my = (my * ORIGIN_SHIFT) / 180.0
    res = INITIAL_RESOLUTION / (2 ** zoom)
    px = (mx + ORIGIN_SHIFT) / res
    py = (my + ORIGIN_SHIFT) / res
    return px, py

def pixelstolatlon(px, py, zoom):
    res = INITIAL_RESOLUTION / (2 ** zoom)
    mx = px * res - ORIGIN_SHIFT
    my = py * res - ORIGIN_SHIFT
    lat = (my / ORIGIN_SHIFT) * 180.0
    lat = 180 / pi * (2 * atan(exp(lat * pi / 180.0)) - pi / 2.0)
    lon = (mx / ORIGIN_SHIFT) * 180.0
    return lat, lon


def calculate_area(res):

    img = cv2.imread('map.png') 
    shifted = cv2.pyrMeanShiftFiltering(img, 7, 30) 
    gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY) 
    ret, thresh = cv2.threshold( 
        gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
    hsv = cv2.cvtColor(shifted, cv2.COLOR_BGR2HSV) 

    lower_trees = np.array([10, 0, 10]) 
    higher_trees = np.array([180, 180, 75]) 

    lower_houses = np.array([90, 10, 100]) 
    higher_houses = np.array([255, 255, 255]) 

    lower_roads = np.array([90, 10, 100]) 
    higher_roads = np.array([100, 100, 100]) 

    lower_feilds = np.array([0, 20, 100]) 
    higher_feilds = np.array([50, 255, 255]) 

    lower_feilds_blue = np.array([0, 80, 100]) 
    higher_feilds_blue = np.array([255, 250, 255]) 

    masktree = cv2.inRange(hsv, lower_trees, higher_trees) 
    maskhouses = cv2.inRange(hsv, lower_houses, higher_houses) 
    maskroads = cv2.inRange(hsv, lower_roads, higher_roads) 
    maskfeilds_houses = cv2.inRange(hsv, lower_feilds, higher_feilds) 
    blue_limiter = cv2.inRange(hsv, lower_feilds_blue, higher_feilds_blue) 
    maskfeilds = maskfeilds_houses 
    res = cv2.bitwise_and(img, img, mask=maskfeilds) 

    print(res.shape) # (640, 622, 3) 
    print(np.count_nonzero(res)) # 679089 

    print("number of pixels", res.size//3) 
    tot_pixels = res.size//3
    # print("number of pixels: row x col", res.) 

    no_of_non_zero_pixels_rgb = np.count_nonzero(res) 
    row, col, channels = res.shape # 152886 
    print("percentage of free land : ", (no_of_non_zero_pixels_rgb /
                                        (row*col*channels))) # 0.5686369573954984 
    percentage_of_land = no_of_non_zero_pixels_rgb/(row*col*channels) 

    # https://www.unitconverters.net/typography/centimeter-to-pixel-x.htm 
    # says 1 cm = 37.795275591 pixels 
    cm_2_pixel = 37.795275591
    print("row in cm ", row/cm_2_pixel) 
    print("col in cm ", col/cm_2_pixel) 

    row_cm = row/cm_2_pixel 
    col_cm = col/cm_2_pixel 
    tot_area_cm = tot_pixels/(row_cm*col_cm) 
    tot_area_cm_land = tot_area_cm*percentage_of_land 

    print("Total area in cm^2 : ", tot_area_cm_land) 

    # in google maps 2.2cm = 50m => 1cm = 22.727272727272727m 
    # in real life at zoom 18 1cm^2 = (22.727272727272727m)^2 
    # = 516.5289256198347 m^2 
    print("Total area in m^2 : ", tot_area_cm_land*(516.5289256198347)) 
    tot_area_m_actual_land = tot_area_cm_land*(516.5289256198347) 

    # 1 m^2 = 0.000247105 acres :: source Google 
    tot_area_acre_land = tot_area_m_actual_land*0.000247105
    print("Total area in acres : ", tot_area_acre_land) 

    # https://www.treeplantation.com/tree-spacing-calculator.html 
    # says if you have 2 ft between rows, and 2ft between 
    # trees will can take 10890 trees per acre. 
    number_of_trees = tot_area_acre_land*10890
    print(f"{round(number_of_trees)} number of trees can be planted in {tot_area_acre_land} acres.")
    return tot_area_acre_land, round(number_of_trees)

def air_pollution_core(ullat, ullon, lrlat, lrlon):
    
    zoom = 18
    scale = 1
    maxsize = 640
    ulx, uly = latlontopixels(ullat, ullon, zoom)
    lrx, lry = latlontopixels(lrlat, lrlon, zoom)
    dx, dy = lrx - ulx, uly - lry
    cols, rows = int(ceil(dx / maxsize)), int(ceil(dy / maxsize))
    bottom = 120
    largura = int(ceil(dx / cols))
    altura = int(ceil(dy / rows))
    alturaplus = altura + bottom
    final = Image.new("RGB", (int(dx), int(dy)))
    total_acres_place, total_trees = 0. ,0.
    total_tile_results = dict()
    for x in range(cols):
        for y in range(rows):
            dxn = largura * (0.5 + x)
            dyn = altura * (0.5 + y)
            latn, lonn = pixelstolatlon(ulx + dxn, uly - dyn - bottom / 2, zoom)
            position = ','.join((str(latn), str(lonn)))
            # print(x, y, position)
            urlparams = urllib.parse.urlencode({'center': position,
                                    'zoom': str(zoom),
                                    'size': '%dx%d' % (largura, alturaplus),
                                    'maptype': 'satellite',
                                    'sensor': 'false',
                                    'scale': scale,
                                    'key': 'sk.eyJ1IjoibmVldHUtMSIsImEiOiJjbHcxNTIwaTkwOG50MmpwZHJhY2VsM3o5In0.MlHkPll7gv_NHyvaEQnUlQ'})  

    url = 'https://docs.mapbox.com/api/maps/raster-tiles/?location=New+York&api_key=sk.eyJ1IjoibmVldHUtMSIsImEiOiJjbHcxNTIwaTkwOG50MmpwZHJhY2VsM3o5In0.MlHkPll7gv_NHyvaEQnUlQ' + urlparams

    f = urllib.request.urlopen(url)
    image = io.BytesIO(f.read())
    im = Image.open(image)
    im.save("map_{}{}{}.png".format(x, y, position))
    img = cv2.imread("map_{}{}{}.png".format(x, y, position))
    shifted = cv2.pyrMeanShiftFiltering(img,7,30)
    gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    hsv = cv2.cvtColor(shifted,cv2.COLOR_BGR2HSV)
    lower_trees = np.array([10,0,10])
    higher_trees = np.array([180,180,75])
    lower_houses = np.array([90,10,100])
    higher_houses = np.array([255,255,255])
    lower_roads = np.array([90,10,100])
    higher_roads = np.array([100,100,100])
    lower_feilds = np.array([0,20,100])
    higher_feilds = np.array([50,255,255])
    lower_feilds_blue = np.array([0,80,100])
    higher_feilds_blue = np.array([255,250,255])
    masktree = cv2.inRange(hsv,lower_trees,higher_trees)
    maskhouses = cv2.inRange(hsv,lower_houses,higher_houses)
    maskroads = cv2.inRange(hsv,lower_roads,higher_roads)
    maskfeilds_houses = cv2.inRange(hsv,lower_feilds,higher_feilds)
    blue_limiter = cv2.inRange(hsv,lower_feilds_blue,higher_feilds_blue)
    maskfeilds = maskfeilds_houses
    res = cv2.bitwise_and(img,img,mask=maskfeilds)
    area_in_acres, number_of_trees = calculate_area(res)
    total_acres_place +=area_in_acres
    total_trees += number_of_trees
            # print(f"area: {area_in_acres}, no of trees: {number_of_trees}")
    tile_results = {
                "name_of_tile_image": "map_{}{}{}.png".format(x, y, position),
                "area_acres": area_in_acres,
                "number_of_trees": number_of_trees
            }
            # print(tile_results)
    total_tile_results["{}{}{}".format(x, y, position)] = tile_results
            
    cv2.imshow('res',res)
    cv2.imshow('img', img)
    cv2.waitKey(delay=2000)
    cv2.destroyAllWindows()
    # print(total_tile_results)
    ''' results["total_tile_results"] = total_tile_results
    results["total_acres_of_land"] = total_acres_place
    results["total_number_of_trees"] = total_trees
    return results'''
    return total_acres_place, total_trees

def location_based_estimation(place):
    
    results = find_coordinates(place)
    print("after find coordinates")
    if results is not None and 'upper_left' in results:
        ullat, ullon = results['upper_left']
        lrlat, lrlon = results['lower_right']
        total_acres_place, total_trees = air_pollution_core(ullat, ullon, lrlat, lrlon)
        return total_acres_place, total_trees
    else:
        print("Failed to find the name of the place or its coordinates.")
        return None, None


def coordinates_based_estimation(ullat, ullon, lrlat, lrlon):
    
    total_acres_place, total_trees = air_pollution_core(ullat, ullon, lrlat, lrlon)
    return total_acres_place, total_trees

def main():
    place = input("Enter the name of the place: ")
    total_acres, total_trees = location_based_estimation(place)
    print("after input area")
    print("Total acres of land in the specified area:", total_acres)
    print("Total number of trees that can be planted:", total_trees)

if __name__ == "__main__":
    main()