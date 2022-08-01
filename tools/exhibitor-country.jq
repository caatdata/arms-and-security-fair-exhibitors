([
  $countryGeoCsv
    | split("\n")
    | .[]
    | select((. | length) > 0)
    | split(",")
    | {
      "key": .[0],
      "value": {
        "lat": .[1],
        "lon": .[2]
      }
    }
] | from_entries) as $countryGeoObj
| [
    .[]
    | select(.address and .exhibitor)
    | .address = (if .address | type == "array" then .address[0] else .address end)
    | select((.address | type == "object"))
    | [
      {
        "eventName": .name,
        "eventLatLon": [.address.lat, .address.lon],
        "exhibitor": [
            .exhibitor[]
            | .country = (if .country | type == "array" then .country[0] else .country end)
            | .country = (if .country | type == "object" then .country.iso2 else .country end)
            | .address = (if .address | type == "array" then .address[0] else .address end)
            | .address = (if .address | type == "object" then .address.iso2 else .address end)
            | .iso2 = (if .address then .address else .country end)
            | select(.iso2)
            | {
              "name": .name,
              "latLon": ($countryGeoObj[.iso2] | [.lat, .lon])
            }
        ]
      }
    ]
    | .[]
    | select(.exhibitor | length > 0)
]
