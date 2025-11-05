import importlib.util
import os

class Config:
    def __init__(self, **entries):
        self.__dict__.update(entries)

def load_config():
    import importlib.util, os, config_default as default
    config = {k: getattr(default, k) for k in dir(default) if not k.startswith("__")}
    local_path = os.path.join(os.path.dirname(__file__), "config.py")
    if os.path.exists(local_path):
        spec = importlib.util.spec_from_file_location("config", local_path)
        local = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local)
        for k in dir(local):
            if not k.startswith("__"):
                config[k] = getattr(local, k)
    return Config(**config)


# Example usage
if __name__ == "__main__":
    cfg = load_config()
    # print(cfg.highlight)


