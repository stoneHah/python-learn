import json
from xml.etree import ElementTree as ET

def kml_to_geojson(kml_file_path, geojson_file_path):
    # Parse the KML file
    tree = ET.parse(kml_file_path)
    root = tree.getroot()

    # Define KML namespace
    namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

    # Initialize GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    # Extract Placemark data
    for placemark in root.findall('.//kml:Placemark', namespaces):
        for coord_element in placemark.findall('.//kml:coordinates', namespaces):
            # Split coordinates and process them
            coords_text = coord_element.text.strip()
            coords_list = [
                [float(coord.split(',')[0]), float(coord.split(',')[1])]
                for coord in coords_text.split()
            ]

            # Create a GeoJSON feature
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon" if len(coords_list) > 1 else "Point",
                    "coordinates": coords_list if len(coords_list) > 1 else coords_list[0]
                },
                "properties": {}
            }
            geojson["features"].append(feature)

    # Save to GeoJSON file
    with open(geojson_file_path, 'w', encoding='utf-8') as geojson_file:
        json.dump(geojson, geojson_file, ensure_ascii=False, indent=2)

# Usage example
kml_file_path = 'gis/doc.kml'
geojson_file_path = 'gis/geojson/output.geojson'

kml_to_geojson(kml_file_path, geojson_file_path)
print(f"GeoJSON data has been saved to: {geojson_file_path}")
