import math
import os
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # Disable DecompressionBombError


def lat_lon_to_pixels(lat, lon, zoom):
    """Convert latitude and longitude to pixel coordinates at a given zoom level."""
    n = 2.0 ** zoom
    x = ((lon + 180.0) / 360.0) * n * 256
    y = (1.0 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n * 256
    return x, y


def pixels_to_tile(px, py):
    """Convert pixel coordinates to tile coordinates."""
    return int(px / 256), int(py / 256)


def process_tile(img, x1, y1, x2, y2, output_path):
    """Process and save a single tile."""
    tile = img.crop((x1, y1, x2, y2))
    if tile.size != (256, 256):
        tile = tile.resize((256, 256), Image.LANCZOS)
    tile.save(output_path)


def cut_map_into_tiles(input_image_path, output_folder, left_lon, top_lat, right_lon, bottom_lat, min_zoom, max_zoom):
    # Get image dimensions without loading the entire image into memory
    with Image.open(input_image_path) as img:
        img_width, img_height = img.size

    for zoom in range(min_zoom, max_zoom + 1):
        # Calculate pixel coordinates for the current zoom level
        left_px, top_py = lat_lon_to_pixels(top_lat, left_lon, zoom)
        right_px, bottom_py = lat_lon_to_pixels(bottom_lat, right_lon, zoom)

        # Calculate tile coordinates
        left_tile_x, top_tile_y = pixels_to_tile(left_px, top_py)
        right_tile_x, bottom_tile_y = pixels_to_tile(right_px, bottom_py)

        # Process tiles in chunks
        chunk_size = 10  # Adjust this value based on your system's memory capacity
        for chunk_y in range(top_tile_y, bottom_tile_y + 1, chunk_size):
            chunk_bottom = min(chunk_y + chunk_size, bottom_tile_y + 1)

            # Calculate the region to load
            y1 = max(0, (chunk_y * 256 - top_py) * img_height / (bottom_py - top_py))
            y2 = min(img_height, (chunk_bottom * 256 - top_py) * img_height / (bottom_py - top_py))

            # Load only the necessary part of the image
            with Image.open(input_image_path) as img:
                img_chunk = img.crop((0, y1, img_width, y2))

            for tile_y in range(chunk_y, chunk_bottom):
                for tile_x in range(left_tile_x, right_tile_x + 1):
                    # Calculate pixel coordinates for this tile in the original image
                    x1 = max(0, (tile_x * 256 - left_px) * img_width / (right_px - left_px))
                    y1 = max(0, (tile_y * 256 - top_py) * img_height / (bottom_py - top_py) - y1)
                    x2 = min(img_width, ((tile_x + 1) * 256 - left_px) * img_width / (right_px - left_px))
                    y2 = min(img_chunk.height, ((tile_y + 1) * 256 - top_py) * img_height / (bottom_py - top_py) - y1)

                    # Ensure the directory exists
                    os.makedirs(f"{output_folder}/{zoom}", exist_ok=True)

                    # Process and save the tile
                    tile_path = f"{output_folder}/{zoom}/{tile_x}_{tile_y}.png"
                    process_tile(img_chunk, x1, y1, x2, y2, tile_path)

        print(f"Finished generating tiles for zoom level {zoom}")


# Example usage
input_image = "baidu_map.png"  # Replace with your input image path
output_folder = "tiles"  # Replace with your desired output folder

# Parameters from the second image
left_lon, top_lat = 120.198916701233, 33.5571149745214
right_lon, bottom_lat = 120.575219608545, 33.3807822525195

33.5571149745214, 120.198916701233
33.3807822525195, 120.575219608545

# Additional parameters
min_zoom = 10
max_zoom = 13

cut_map_into_tiles(input_image, output_folder, left_lon, top_lat, right_lon, bottom_lat, min_zoom, max_zoom)