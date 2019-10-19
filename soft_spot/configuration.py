import configparser


def get_account_info(account_info_file):
    if account_info_file:
        config = configparser.ConfigParser()
        config.read(account_info_file)
        return config["DEFAULT"]
    return {}
