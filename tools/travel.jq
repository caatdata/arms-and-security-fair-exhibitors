[
    .[]
    | select(.address and .exhibitor)
    | .address = (if .address | type == "array" then .address[0] else .address end)
    | select((.address | type == "object") and .address.iso2 == $iso2)
    | [
      {
        "eventName": .name,
        "eventLatLon": [.address.lat, .address.lon],
        "exhibitor": [
            .exhibitor[]
            | select(.address)
            | .address = (if .address | type == "array" then .address[0] else .address end)
            | select(.address | type == "object")
            | {
              "name": .name,
              "latLon": [.address.lat, .address.lon],
            }
        ]
      }
    ]
    | .[]
    | select(.exhibitor | length > 0)
]
