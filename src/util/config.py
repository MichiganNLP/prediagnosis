import configparser



LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

CONFIG_FILE = "config.txt"

# read some arguments from txt config file
cfg = configparser.ConfigParser()
cfg.read(CONFIG_FILE)
DIAGPATTERNS_POS = cfg["DATA_LOCATIONS"]['DIAGPATTERNS_POS']
DEPRESSION_WORDS = cfg["DATA_LOCATIONS"]['DEPRESSION_WORDS']
