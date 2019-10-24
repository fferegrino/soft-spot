def execute_scripts(ip_address, instance_configuration):
    account = instance_configuration["ACCOOUNT"]
    user = account.get("user")

    scripts = instance_configuration["SCRIPTS"]
    scripts = scripts.get("scropts")
