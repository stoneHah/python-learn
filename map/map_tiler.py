from PIL import Image
import math
import os


def lat_lon_to_tile_coords(lat, lon, zoom):
    n = 2.0 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n)
    return x_tile, y_tile


def slice_image_to_tiles(image_path, top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon, width_km,
                         height_km, zoom, output_dir):
    output_dir = os.path.join(output_dir, str(zoom))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    img = Image.open(image_path)
    img_width, img_height = img.size

    top_left_tile = lat_lon_to_tile_coords(top_left_lat, top_left_lon, zoom)
    bottom_right_tile = lat_lon_to_tile_coords(bottom_right_lat, bottom_right_lon, zoom)

    tile_size = 256  # 每个瓦片的像素大小

    x_tile_count = bottom_right_tile[0] - top_left_tile[0] + 1
    y_tile_count = bottom_right_tile[1] - top_left_tile[1] + 1

    tile_width_km = width_km / x_tile_count
    tile_height_km = height_km / y_tile_count

    for y in range(top_left_tile[1], bottom_right_tile[1] + 1):
        for x in range(top_left_tile[0], bottom_right_tile[0] + 1):
            left = (x - top_left_tile[0]) * tile_size
            upper = (y - top_left_tile[1]) * tile_size
            right = left + tile_size
            lower = upper + tile_size
            box = (left, upper, right, lower)
            tile = img.crop(box)
            tile_filename = f"{x}_{y}.png"
            tile.save(os.path.join(output_dir, tile_filename))


# 示例调用
# 输入参数：左上角经纬度、右下角经纬度、宽度（km）、高度（km）、瓦片缩放级别
top_left_lat = 39.92175042533688
top_left_lon = 116.385221201897
bottom_right_lat = 39.9101312551376
bottom_right_lon = 116.39628410339357
width_km = 0.944
height_km = 1.293

for level in range(10,20):

    slice_image_to_tiles("palace.png", top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon, width_km,
                         height_km, level, "output_tiles")
