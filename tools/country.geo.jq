[
  .[]
  | (
     (
       select(.country)
         | . = (if .country | type == "array" then .country[] else .country end)
     ),
     (
       select(.exhibitor)
         | .exhibitor[]
         | select(.country)
         | . = (if .country | type == "array" then .country[] else .country end)
     )
  )
  | . = (if . | type == "object" then .text else . end)
  | sub("^.*\n"; ""; "g")
]
 | sort
 | unique
 | .[]
