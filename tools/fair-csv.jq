if . == null then (
  [
    "Slug",
    "Name",
    "Alias",
    "Series",
    "Edition",
    "Start date",
    "End date",
    "Address",
    "Country",
    "ISO2",
    "Latitude",
    "Longitude",
    "Online",
    "Website",
    "Exhibitor list URL",
    "Delegation list URL"
  ]
) else (
    .
    | .slug = (input_filename | sub("^.*/(?<slug>[a-z0-9-]*)\\.json$"; "\(.slug)"))
    | .alias = (if .alias | type == "array" then .alias | join(";") else .alias end)
    | .address = (if .address | type == "array" then .address[0] else .address end)
    | .address = (if .address | type == "string" then {"text": .} else .address end)
    | .country = (if .country | type == "array" then .country[0] else .country end)
    | .country = (if .country | type == "string" then {"text": .} else .country end)
    | .iso2 = (if .address.iso2? | type == "string" then .address.iso2 else .country.iso2? end)
    | .website = (if .website | type == "array" then .website | join(";") else .website end)
    | .exhibitorListUrl = (if .exhibitorListUrl | type == "array" then .exhibitorListUrl | join(";") else .exhibitorListUrl end)
    | .delegationListUrl = (if .delegationListUrl | type == "array" then .delegationListUrl | join(";") else .delegationListUrl end)
    | [
        .slug,
        .name,
        .alias,
        .series,
        .edition,
        .startDate,
        .endDate,
      (.address.text | (if . | type == "string" then . | sub("\n"; "\\n"; "g") else . end)),
        .country.text,
        .iso2,
        .address.lat,
        .address.lon,
        .online,
        .website,
        .exhibitorListUrl,
        .delegationListUrl
    ]
) end
  | @csv
