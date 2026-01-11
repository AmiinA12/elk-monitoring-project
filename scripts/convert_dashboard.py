import json
import os

input_file = 'docs/kibana-dashboard-template.json'
output_file = 'docs/dashboard_import.ndjson'

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    objects = data.get('objects', [])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for obj in objects:
            # Ensure each object is written as a single line
            json.dump(obj, f)
            f.write('\n')
            
    print(f"Successfully converted {len(objects)} objects to {output_file}")

except Exception as e:
    print(f"Error converting file: {e}")
    exit(1)
