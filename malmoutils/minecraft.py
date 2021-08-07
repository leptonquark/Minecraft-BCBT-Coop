import malmo.minecraftbootstrap

#TODO: Remove Hardcoded line and move to a config file
def run_minecraft():
    malmo.minecraftbootstrap.malmo_install_dir = "C:\Malmo-0.37.0-Windows-64bit_withBoost_Python3.7"
    malmo.minecraftbootstrap.launch_minecraft()
