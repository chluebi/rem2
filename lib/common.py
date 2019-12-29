import json

def parse_config(name):
	with open(f'configs/{name}_config.json', 'r+') as f:
		data = json.load(f)
	return data