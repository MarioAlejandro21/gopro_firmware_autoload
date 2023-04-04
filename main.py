from shutil import copytree, rmtree
from os.path import exists, join, isdir
from os import getcwd, system, listdir
from re import match
from sys import exit
from yaml import safe_load

# Globals
source_path = ""
sd_path = ""

def get_firmware_folder_with_sn_or_none(sn):
    lookup_model_info = [
        {
            'sn_pattern': "^C333",
            'folder_name': "Hero8 Black"
        },
        {
            'sn_pattern': "^C344",
            'folder_name': "Hero9 Black"
        },
        {
            'sn_pattern': "^C34613B45",
            'folder_name': "Hero10 Bones"
        },
        {
            'sn_pattern': "^C346",
            'folder_name': "Hero10 Black"
        },
        {
            'sn_pattern': "^C349",
            'folder_name': "Hero11 Pismo"
        },
        {
            'sn_pattern': "^C347",
            'folder_name': "Hero11 Sultan"
        },
        {
            'sn_pattern': "^C335",
            'folder_name': "MAX"
        },
    ]

    for info in lookup_model_info:
        
        pattern = info["sn_pattern"]
        folder = info["folder_name"]

        if match(pattern=pattern, string=sn):
            return folder

    return None


def load_config_paths():
    
    config_filename = 'config.yml'

    if not exists(join(getcwd(), 'config.yml')):
        exit("Error: Configuration file missing or misplaced")

    with open(config_filename, 'r') as f:
        
        load = safe_load(f)

        global source_path, sd_path

        try:
            source_path = load['source_path']
            sd_path = load['sd_path']
        except:
            exit("Error: sintax issues in config file or missing parameters.")

        
def assure_sd_card_available():
    if not exists(sd_path):
        input("SD card unavailable, press enter to check again...")
        assure_sd_card_available()

def get_available_folder_names(model):
    
    cwd = join(source_path, model)

    return [item for item in listdir(cwd) if isdir(join(cwd, item)) and "SD" in item]

def select_firmware_option(ops: list):
    
    ops.insert(0, "Factory Reset")

    print("Available firmwares:")

    for i, op in ops:
        print(f"{i}. {op}")

    res = input("Your selection: ")
    return




load_config_paths()

assure_sd_card_available()

system('clear')

print('Automatic loader')

while True:
    res = input("Scan serial number of the camera (or type x to exit): ")
    firmware_folder_name = get_firmware_folder_with_sn_or_none(res)
    
    if res == "x":
        break

    elif not firmware_folder_name:
        print("Invalid serial number or model not supported.")
    
    else:
        firmware_options = get_available_folder_names(firmware_folder_name)
        select_firmware_option(firmware_options)
