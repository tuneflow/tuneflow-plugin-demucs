from models.demucs_plugin import MusicSourceSeparatePlugin
from tuneflow_devkit import Debugger

if __name__ == "__main__":
    Debugger(plugin_class=MusicSourceSeparatePlugin).start()