import requests
import json
import os

json_url = 'https://raw.githubusercontent.com/bogdanfazakas/datasets/refs/heads/main/data.json'
output_folder = '/data/outputs'
output_file = os.path.join(output_folder, 'results.json')

def compute_avg_price_by_filter(url, main_filter="roomsNo", filters=None):
    # Always include these fields in the output
    always_include = {"surface", "roomsNo", "createdOn"}
    try:
        response = requests.get(url)
        response.raise_for_status()
        properties = response.json()

        if not isinstance(properties, list):
            raise ValueError("Expected JSON to be a list")

        avg_prices_by_filter = {}

        for prop in properties:
            info = prop.get("info", {})
            price = info.get("price")
            filter_value = info.get(main_filter)

            if price is None or filter_value is None:
                continue

            if filter_value not in avg_prices_by_filter:
                avg_prices_by_filter[filter_value] = {
                    "totalPrice": 0,
                    "count": 0,
                    "properties": [],
                    "lowestPrice": price,
                    "highestPrice": price
                }

            avg_prices_by_filter[filter_value]["totalPrice"] += price
            avg_prices_by_filter[filter_value]["count"] += 1

            # Update lowest and highest price
            if price < avg_prices_by_filter[filter_value]["lowestPrice"]:
                avg_prices_by_filter[filter_value]["lowestPrice"] = price
            if price > avg_prices_by_filter[filter_value]["highestPrice"]:
                avg_prices_by_filter[filter_value]["highestPrice"] = price

            # Apply filters if provided, but always include the important fields
            if filters:
                fields = set(filters) | always_include
                filtered_info = {k: v for k, v in info.items() if k in fields}
            else:
                filtered_info = info

            avg_prices_by_filter[filter_value]["properties"].append(filtered_info)

        # Finalize average calculation
        for filter_value, stats in avg_prices_by_filter.items():
            avg = stats["totalPrice"] / stats["count"]
            avg_prices_by_filter[filter_value]["averagePrice"] = round(avg, 2)

        # Write to output file
        os.makedirs(output_folder, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(avg_prices_by_filter, f, indent=2)

        print("✅ Results written to:", output_file)
        print("📊 Avg Prices by Filter:", avg_prices_by_filter)

    except Exception as e:
        print(f"❌ Error: {str(e)}")

# --- Prompt user for main_filter and filters ---
def prompt_for_filters():
    print("Enter the main filter (e.g., roomsNo, type, zone):")
    main_filter = input("Main filter: ").strip()
    print("Enter other filters separated by commas (e.g., type,zone,surface,bathroomsNo,roomsNo,createdOn):")
    filters_input = input("Other filters: ").strip()
    filters = [f.strip() for f in filters_input.split(",") if f.strip()]
    return main_filter, filters

if __name__ == "__main__":
    main_filter, filters = prompt_for_filters()
    compute_avg_price_by_filter(json_url, main_filter, filters)