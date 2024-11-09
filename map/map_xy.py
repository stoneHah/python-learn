import math

EARTH_RADIUS = 6378137  # 地球半径，单位米


def latlng_to_pixels(lat, lng, zoom):
    """将经纬度转换为像素坐标"""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x = ((lng + 180.0) / 360.0) * n
    y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return x, y


def pixels_to_tile(px, py):
    """将像素坐标转换为瓦片坐标"""
    return int(math.floor(px)), int(math.floor(py))


def latlng_to_tile(lat, lng, zoom):
    """将经纬度转换为百度瓦片坐标"""
    px, py = latlng_to_pixels(lat, lng, zoom)
    tx, ty = pixels_to_tile(px, py)

    # 调整为百度瓦片坐标系统
    n = 2 ** (zoom - 1)  # 最低级别的瓦片数量为2x2
    tx = tx - n
    ty = n - 1 - ty

    return tx, ty


def get_tile_range(lat1, lng1, lat2, lng2, zoom):
    """
    计算矩形区域在指定缩放级别下的瓦片范围
    lat1, lng1: 左上角坐标
    lat2, lng2: 右下角坐标
    zoom: 缩放级别
    """
    x1, y1 = latlng_to_tile(lat1, lng1, zoom)
    x2, y2 = latlng_to_tile(lat2, lng2, zoom)

    # 确保 x1 <= x2 且 y1 <= y2
    minx = min(x1, x2)
    maxx = max(x1, x2)
    miny = min(y1, y2)
    maxy = max(y1, y2)

    return minx, miny, maxx, maxy


# 测试代码
if __name__ == "__main__":
    # 测试矩形区域（以北京为中心的一个区域为例）
    lat1, lng1 = 33.5571149745214, 120.198916701233  # 左上角
    lat2, lng2 = 33.3807822525195, 120.575219608545  # 右下角
    zoom = 10  # 缩放级别

    minx, miny, maxx, maxy = get_tile_range(lat1, lng1, lat2, lng2, zoom)
    print(f"矩形区域 (左上角: {lat1},{lng1}, 右下角: {lat2},{lng2}) 在缩放级别 {zoom} 下的瓦片范围：")
    print(f"X: {minx} 到 {maxx}")
    print(f"Y: {miny} 到 {maxy}")
    print(f"瓦片数量: {(maxx - minx + 1) * (maxy - miny + 1)}")
