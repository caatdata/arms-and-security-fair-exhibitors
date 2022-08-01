[
    .[]
    | select(.exhibitor)
    | [
        .endDate,
        .name,
      (
        [
            .exhibitor[]
            | (
                .
                | .address = (if .address | type == "null" then [] else .address end)
                | .address = (if .address | type == "array" then .address[] else .address end)
                | .address
            ) ] | length
      ),
      (
        [
            .exhibitor[]
            | (
                .
                | .country = (if .country | type == "null" then [] else .country end)
                | .country = (if .country | type == "array" then .country[] else .country end)
                | .country
            ) ] | length
      )

    ] | @csv
] | sort | .[]
