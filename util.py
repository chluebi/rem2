import json

def parse_config():
	with open('basic_config.json', 'r+') as f:
		data = json.load(f)
	return data

def parse_db_config():
	with open('database_config.json', 'r+') as f:
		data = json.load(f)
	return data

config = parse_config()

def parse_message(content):
	l = len(config['prefix'])
	if content[:l] != config['prefix']:
		return None

	content = content[l:]
	if len(content) < 1:
		return None
	if content[0] == ' ':
		content = content[1:]

	msg = ['']
	quotes = False
	for letter in content:
		if not quotes:
			if letter == ' ':
				msg.append('')
			elif letter in ['`', '“', '\"', '„', '\'']:
				quotes = letter
				if len(msg[-1]) > 0:
					msg.append('')
			else:
				msg[-1] += letter
		else:
			if (quotes == '“' and letter == '”') \
				or (quotes == '„' and letter == '“') \
				or (quotes == letter and letter in '`\"\''):
				quotes = False
			else:
				msg[-1] += letter

	return msg