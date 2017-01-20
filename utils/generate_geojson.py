import json
import requests


def getData(url, headers={'X-App-Token': 'x1rsCW9GlEsXYZVRPLyU0yP6n'}):
    r = requests.get(url, headers=headers)
    return r.json()


def convertData(data, msymbol="restaurant", msize="medium"):
    data_dict = []
    for d in data:
        if d.get('latitude') and d.get('longitude'):
            if not any(item['properties'].get('name') == d.get('name') for item in data_dict):
                data_dict.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(d.get('latitude')),
                                        float(d.get('longitude'))]
                    },
                    "properties": {
                        "name": d.get("name", ""),
                        "marker-symbol": msymbol,
                        "marker-size": msize,
                        "marker-color": "#CC0033",
                        "address": d.get("address", "")
                    }
                })
    return data_dict


def writeToFile(data, filename="data.geojson"):
    template = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            },
        },
        "features": data}
    with open(filename, "w") as f:
        json.dump(template, f, indent=2)
    print "Geojson generated"


if __name__ == "__main__":
    data = getData("https://data.kingcounty.gov/resource/gkhn-e8mn.json")
    writeToFile(convertData(data[:350]), filename="trucks.geojson")
