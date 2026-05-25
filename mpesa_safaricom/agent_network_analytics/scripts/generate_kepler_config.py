"""
generate_kepler_config.py

Generates a sample Kepler.gl config JSON that loads agents.geojson and wards.geojson layers.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'maps' / 'kepler_generated_config.json'
AGENTS = '../data/kepler/agents.geojson'
WARDS = '../data/kepler/wards.geojson'


def generate():
    config = {
        'version': 'v1',
        'config': {
            'visState': {},
            'mapState': {'longitude': 37.9062, 'latitude': 0.0236, 'zoom': 6},
            'datasets': [
                {'label': 'agents', 'url': AGENTS},
                {'label': 'wards', 'url': WARDS}
            ]
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as fh:
        json.dump(config, fh, indent=2)
    print('Wrote kepler config to', OUT)

if __name__ == '__main__':
    generate()
