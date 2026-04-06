import csv
import json
import os

def compile_and_merge():
    files = [
        ('mobile-sites-telstra-2025.csv', 'Telstra'),
        ('mobile-sites-optus-2025.csv', 'Optus'),
        ('mobile-sites-tpg-2025.csv', 'TPG'),
        ('mobile-sites-optus-tpg-mocn-2025.csv', 'MOCN_Shared')
    ]

    # This dictionary uses (lat, lon) as a key to group sites
    merged_sites = {}

    for filename, carrier in files:
        if not os.path.exists(filename):
            print(f"[-] Missing: {filename}")
            continue

        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            for row in reader:
                try:
                    lat_str, lon_str = row[3], row[4]
                    lat, lon = float(lat_str), float(lon_str)
                    
                    # Create a unique key for this exact physical location
                    location_key = (lat, lon)
                    
                    # Identify active bands
                    active_tech = [header[i] for i, val in enumerate(row) if val == '1']
                    
                    if location_key not in merged_sites:
                        # First time seeing this tower/location
                        merged_sites[location_key] = {
                            "carriers": {carrier},
                            "all_tech": set(active_tech),
                            "rfnsa_ids": {row[2]}
                        }
                    else:
                        # Add this carrier's data to the existing physical site
                        merged_sites[location_key]["carriers"].add(carrier)
                        merged_sites[location_key]["all_tech"].update(active_tech)
                        merged_sites[location_key]["rfnsa_ids"].add(row[2])

                except (ValueError, IndexError):
                    continue
        print(f"[+] Synced {carrier}")

    # Convert merged dictionary back into GeoJSON
    features = []
    for (lat, lon), data in merged_sites.items():
        carriers_list = sorted(list(data["carriers"]))
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "Title": " | ".join(carriers_list), # Shows as "Telstra | Optus"
                "Carriers": ", ".join(carriers_list),
                "Bands": ", ".join(sorted(list(data["all_tech"]))),
                "Site_IDs": ", ".join(sorted(list(data["rfnsa_ids"]))),
                "Is_Multi_Carrier": len(carriers_list) > 1
            }
        }
        features.append(feature)

    with open('merged_isp_2025.json', 'w') as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, indent=2)
    
    print(f"\nDone! Reduced points from ~35,000 to {len(features)} unique locations.")

if __name__ == "__main__":
    compile_and_merge()
