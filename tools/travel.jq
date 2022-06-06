[
    .[]
    | select(.address and .exhibitor)
    | .address = (if .address | type == "array" then .address[0] else .address end)
    | select((.address | type == "object"))
    | select(($ARGS.named.iso2 | not) or ((.address.iso2 | ascii_downcase) == $ARGS.named.iso2))
    | [
      {
        "eventName": .name,
        "eventLatLon": [.address.lat, .address.lon],
        "exhibitor": [
            .exhibitor[]
            | select(.address)
            | .address = (if .address | type == "array" then .address[0] else .address end)
            | select(.address | type == "object")
            | select(($ARGS.named.name | not) or ((.name | ascii_downcase) | contains($ARGS.named.name)))
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
