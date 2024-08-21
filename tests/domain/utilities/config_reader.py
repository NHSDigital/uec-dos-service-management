import configparser


def read_config(section, key):
    config = configparser.ConfigParser()
    config.read("config/config_dev.ini")
    return config[section][key]
