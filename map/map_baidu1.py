import math
import os
from PIL import Image
from pyproj import Transformer, CRS


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


def get_tiles_info(top_left, bottom_right, width_km, height_km, zoom):
    # Convert lat/lon to tile numbers
    x1, y1 = deg2num(top_left[0], top_left[1], zoom)
    x2, y2 = deg2num(bottom_right[0], bottom_right[1], zoom)

    # Ensure x1 < x2 and y1 < y2
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)

    return x1, y1, x2, y2


def create_tiles(image_path, output_dir, top_left, bottom_right, width_km, height_km, min_zoom, max_zoom):
    # Open the image
    img = Image.open(image_path)

    # Create a transformer for converting between lat/lon and Mercator coordinates
    transformer = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(3857), always_xy=True)

    for zoom in range(min_zoom, max_zoom + 1):
        x1, y1, x2, y2 = get_tiles_info(top_left, bottom_right, width_km, height_km, zoom)

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                # Calculate the bounds of the current tile in lat/lon
                north, west = num2deg(x, y, zoom)
                south, east = num2deg(x + 1, y + 1, zoom)

                # Convert bounds to Mercator coordinates
                west, north = transformer.transform(west, north)
                east, south = transformer.transform(east, south)

                # Calculate the pixel coordinates in the original image
                img_width, img_height = img.size
                px1 = int((west - top_left[1]) / (bottom_right[1] - top_left[1]) * img_width)
                py1 = int((north - top_left[0]) / (bottom_right[0] - top_left[0]) * img_height)
                px2 = int((east - top_left[1]) / (bottom_right[1] - top_left[1]) * img_width)
                py2 = int((south - top_left[0]) / (bottom_right[0] - top_left[0]) * img_height)

                # Crop the image to the current tile
                tile = img.crop((px1, py1, px2, py2))

                # Resize the tile to 256x256
                tile = tile.resize((256, 256), Image.LANCZOS)

                # Save the tile
                tile_dir = os.path.join(output_dir, str(zoom))
                os.makedirs(tile_dir, exist_ok=True)
                tile_path = os.path.join(tile_dir, f"{x}_{y}.png")
                tile.save(tile_path)


if __name__ == "__main__":
    # Example usage
    image_path = "baidu_map.png"
    output_dir = "tiles"
    top_left = (33.5571149745214, 120.198916701233)  # New York City (roughly)
    bottom_right = (33.3807822525195, 120.575219608545)
    width_km = 34.908
    height_km = 19.629
    min_zoom = 10
    max_zoom = 11

    create_tiles(image_path, output_dir, top_left, bottom_right, width_km, height_km, min_zoom, max_zoom)