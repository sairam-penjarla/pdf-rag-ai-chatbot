import yaml

def get_config():
    with open('config/config.yaml', 'r') as stream:
        config = yaml.safe_load(stream)
    return config