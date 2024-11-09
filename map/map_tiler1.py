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


def tile_image(filename, top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon, min_zoom, max_zoom,
               tile_size=256):
    img = Image.open(filename)
    width, height = img.size

    for zoom in range(min_zoom, max_zoom + 1):
        print(f"Generating tiles for zoom level {zoom}")

        # 计算瓦片范围
        x_min, y_max = deg2num(top_left_lat, top_left_lon, zoom)
        x_max, y_min = deg2num(bottom_right_lat, bottom_right_lon, zoom)

        # 计算实际覆盖的经纬度范围
        actual_top_left_lat, actual_top_left_lon = num2deg(x_min, y_max, zoom)
        actual_bottom_right_lat, actual_bottom_right_lon = num2deg(x_max + 1, y_min + 1, zoom)

        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                # 计算当前瓦片的经纬度范围
                tile_top_left_lat, tile_top_left_lon = num2deg(x, y, zoom)
                tile_bottom_right_lat, tile_bottom_right_lon = num2deg(x + 1, y + 1, zoom)

                # 计算瓦片在原图中的位置
                px_min = int(
                    (tile_top_left_lon - actual_top_left_lon) / (actual_bottom_right_lon - actual_top_left_lon) * width)
                py_min = int((actual_top_left_lat - tile_top_left_lat) / (
                            actual_top_left_lat - actual_bottom_right_lat) * height)
                px_max = int((tile_bottom_right_lon - actual_top_left_lon) / (
                            actual_bottom_right_lon - actual_top_left_lon) * width)
                py_max = int((actual_top_left_lat - tile_bottom_right_lat) / (
                            actual_top_left_lat - actual_bottom_right_lat) * height)

                # 裁剪瓦片
                tile = img.crop((px_min, py_min, px_max, py_max))
                tile = tile.resize((tile_size, tile_size), Image.LANCZOS)

                # 保存瓦片
                os.makedirs(f"tiles/{zoom}/{x}", exist_ok=True)
                tile.save(f"tiles/{zoom}/{x}/{y}.png")

        print(f"Tiles generated for zoom level {zoom}")

    print("All tiles generated successfully")


# 使用示例
if __name__ == "__main__":
    tile_image("palace.png",
               top_left_lat=39.92175042533688,
               top_left_lon=116.385221201897,
               bottom_right_lat=39.9101312551376,
               bottom_right_lon=116.39628410339357,
               min_zoom=10,
               max_zoom=20)