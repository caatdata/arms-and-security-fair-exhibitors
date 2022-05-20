 select(.address)
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
 