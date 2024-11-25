import yaml

def load_config(env: str = 'dev') -> dict:
    """Load configuration based on the environment."""
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        if config and env in config:
            return config[env]
        else:
            raise KeyError(f"Environment '{env}' not found in configuration.")
    except yaml.YAMLError as e:
        raise ValueError("Error parsing config.yaml") from e
    except FileNotFoundError:
        raise FileNotFoundError("config.yaml file not found")
