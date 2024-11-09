import math
from PIL import Image
import os


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


def generate_tiles(image_path, top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon, min_zoom, max_zoom):
    img = Image.open(image_path)
    width, height = img.size

    for zoom in range(min_zoom, max_zoom + 1):
        tile_size = 256

        # 计算覆盖区域的瓦片范围
        left_tile_x, top_tile_y = deg2num(top_left_lat, top_left_lon, zoom)
        right_tile_x, bottom_tile_y = deg2num(bottom_right_lat, bottom_right_lon, zoom)

        for tile_y in range(top_tile_y, bottom_tile_y + 1):
            for tile_x in range(left_tile_x, right_tile_x + 1):
                # 计算瓦片在原图中的位置
                lat, lon = num2deg(tile_x, tile_y, zoom)
                x = int((lon - top_left_lon) / (bottom_right_lon - top_left_lon) * width)
                y = int((top_left_lat - lat) / (top_left_lat - bottom_right_lat) * height)

                # 裁剪瓦片
                tile = img.crop((x, y, x + tile_size, y + tile_size))

                # 创建目录并保存瓦片
                os.makedirs(f"tiles/{zoom}", exist_ok=True)
                tile.save(f"tiles/{zoom}/{tile_x}_{tile_y}.png")


# 使用示例
image_path = "baidu_map.png"
top_left_lat, top_left_lon = 33.5571149745214, 120.198916701233  # 纽约市的大致坐标
bottom_right_lat, bottom_right_lon = 33.3807822525195, 120.575219608545
min_zoom, max_zoom = 10, 13

generate_tiles(image_path, top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon, min_zoom, max_zoom)
