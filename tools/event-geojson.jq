 select(.address)
 | .address = (if .address | type == "array" then .address[0] else .address end)
 | {
    "type": "Feature",
    "properties": {
      "eventName": .name
    },
    "geometry": {
      "type": "Point",
      "coordinates": [
          .address.lon,
          .address.lat
      ]
    }
  }
 