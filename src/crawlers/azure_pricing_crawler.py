import json

with open("azure_pricing.json", "r") as f:
    data = json.load(f)

item_keys = [set(item.keys()) for item in data["Items"]]

common_keys = set.intersection(*item_keys)
all_keys = set.union(*item_keys)
non_common_keys = all_keys - common_keys

print("Non-common properties among all records:")
for key in non_common_keys:
    print(key)