  . as $data
  | [path(..) ]
  | map(select(length == 3 and .[0] == "exhibitor" and .[2] == "address"))
  | map($data.exhibitor[.[1]])
  | map(select(.address | type == "object"))
  | map({
    "type": "Feature",
    "properties": {
      "eventName": $data.name,
      "exhibitorName": .name,
    },
    "geometry": {
      "type": "Point",
      "coordinates": [
          .address.lon,
          .address.lat
      ]
    }
  })
  | .[]
