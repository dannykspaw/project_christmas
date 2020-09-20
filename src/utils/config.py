from os import getenv, path
import json


config = None

def __json_to_config(config):
    """
    Convert dictionary into instance allowing access to dictionary keys using
    dot notation (attributes).
    """
    class ConfigObject(dict):
        """
        Represents configuration options' group, works like a dict
        """
        def __init__(self, *args, **kwargs):
            dict.__init__(self, *args, **kwargs)
        def __getattr__(self, name):
            return self[name]
        def __setattr__(self, name, val):
            self[name] = val
    if isinstance(config, dict):
        result = ConfigObject()
        for key in config:
            result[key] = __json_to_config(config[key])
        return result
    else:
        return config


env = getenv('ENV', 'default')
base_config_path = getenv('CONFIG_PATH', './src/config/')
absolute_base_config_path = path.abspath(base_config_path)
config_path = '{}{}.json'.format(base_config_path, env)

print('loading {} config from {}'.format(env, absolute_base_config_path))
with open(config_path, 'r') as read_file:
    raw_json = json.load(read_file)
    config = __json_to_config(raw_json)