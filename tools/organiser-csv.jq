if . == null then (
  [
    "Slug",
    "Name",
    "Alias",
    "Address",
    "Country",
    "ISO2",
    "Latitude",
    "Longitude",
    "Website"
  ]
) else (
    .
    | select(.organiser)
    | .slug = (input_filename | sub("^.*/(?<slug>[a-z0-9-]*)\\.json$"; "\(.slug)"))
    | . as $fair
    | (.organiser | if . | type == "array" then .[] else . end)
    | .alias = (.alias | if . | type == "array" then . | join(";") else . end)
    | .address = (.address | if . | type == "array" then .[0] else . end)
    | .address = (.address | if . | type == "string" then {"text": .} else . end)
    | .country = (.country | if . | type == "array" then .[0] else . end)
    | .country = (.country | if . | type == "string" then {"text": .} else . end)
    | .iso2 = (if .address.iso2? | type == "string" then .address.iso2 else .country.iso2? end)
    | .website = (.website | if . | type == "array" then . | join(";") else . end)
    | [
      $fair.slug,
        .name,
        .alias,
      (.address.text | (if . | type == "string" then . | sub("\n"; "\\n"; "g") else . end)),
        .country.text,
        .iso2,
        .address.lat,
        .address.lon,
        .website
    ]
) end
  | @csv
