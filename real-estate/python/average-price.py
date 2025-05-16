import requests
import json
import os

json_url = 'https://raw.githubusercontent.com/bogdanfazakas/datasets/refs/heads/main/data.json'
output_folder = '/data/outputs'
output_file = os.path.join(output_folder, 'results.json')

def compute_avg_price_by_property(url, main_property="roomsNo", filters=None):
    # Always include these fields in the output
    always_include = {"surface", "roomsNo", "createdOn"}
    try:
        response = requests.get(url)
        response.raise_for_status()
        properties = response.json()

        if not isinstance(properties, list):
            raise ValueError("Expected JSON to be a list")

        avg_prices_by_property = {}

        for prop in properties:
            info = prop.get("info", {})
            price = info.get("price")
            property_value = info.get(main_property)

            if price is None or property_value is None:
                continue

            if property_value not in avg_prices_by_property:
                avg_prices_by_property[property_value] = {
                    "totalPrice": 0,
                    "count": 0,
                    "properties": [],
                    "lowestPrice": price,
                    "highestPrice": price
                }

            avg_prices_by_property[property_value]["totalPrice"] += price
            avg_prices_by_property[property_value]["count"] += 1

            # Update lowest and highest price
            if price < avg_prices_by_property[property_value]["lowestPrice"]:
                avg_prices_by_property[property_value]["lowestPrice"] = price
            if price > avg_prices_by_property[property_value]["highestPrice"]:
                avg_prices_by_property[property_value]["highestPrice"] = price

            # Apply filters if provided, but always include the important fields
            if filters:
                fields = set(filters) | always_include
                filtered_info = {k: v for k, v in info.items() if k in fields}
            else:
                filtered_info = info

            avg_prices_by_property[property_value]["properties"].append(filtered_info)

        # Finalize average calculation
        for property_value, stats in avg_prices_by_property.items():
            avg = stats["totalPrice"] / stats["count"]
            avg_prices_by_property[property_value]["averagePrice"] = round(avg, 2)

        # Write to output file
        os.makedirs(output_folder, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(avg_prices_by_property, f, indent=2)

        print("✅ Results written to:", output_file)
        print("📊 Avg Prices by Property:", avg_prices_by_property)

    except Exception as e:
        print(f"❌ Error: {str(e)}")

# --- Prompt user for main_property and filters ---
def prompt_for_filters():
    print("Enter the main property to compute by (e.g., roomsNo, type, zone):")
    main_property = input("Main property: ").strip()
    print("Enter other filters separated by commas (e.g., type,zone,surface,bathroomsNo,roomsNo,createdOn):")
    filters_input = input("Other filters: ").strip()
    filters = [f.strip() for f in filters_input.split(",") if f.strip()]
    return main_property, filters

if __name__ == "__main__":
    main_property, filters = prompt_for_filters()
    compute_avg_price_by_property(json_url, main_property, filters)