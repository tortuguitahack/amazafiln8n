require 'google_search_results' 

params = {
  engine: "amazon",
  amazon_domain: "amazon.com",
  k: "oferts best ELECTRONICS",
  api_key: "70cc1e3917ff5c14fa2a3747ce2fdcc38f0d9b83cad079ff0585c963a62344d8"
}

search = GoogleSearch.new(params)
hash_results = search.get_hash
