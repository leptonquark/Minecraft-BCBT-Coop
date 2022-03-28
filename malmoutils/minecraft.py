import malmo.minecraftbootstrap

def run_minecraft():
    #Windows
    #malmo.minecraftbootstrap.malmo_install_dir = "C:\Malmo-0.37.0-Windows-64bit_withBoost_Python3.7"
    #Mac
    malmo.minecraftbootstrap.malmo_install_dir = "/Users/Netlight/minecraft/Malmo-0.37.0-Mac-64bit_withBoost_Python3.7"
    malmo.minecraftbootstrap.launch_minecraft()
