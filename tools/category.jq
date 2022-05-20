  .[]
  | select(.exhibitor)
  | .exhibitor[]
  | select(.category)
  | .category
  | if . | type == "string" then . else .[] end
  | ascii_upcase
