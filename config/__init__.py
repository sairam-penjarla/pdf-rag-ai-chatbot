import yaml

def get_config():
    with open('config/config.yaml', 'r') as stream:
        config = yaml.safe_load(stream)
        class Config:
            def __init__(self, **entries):
                self.__dict__.update(entries)
    return Config(**config)