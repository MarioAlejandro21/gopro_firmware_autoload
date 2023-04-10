from shutil import copytree, rmtree
from os.path import exists, join, isfile
from os import getcwd, system, listdir, remove
from subprocess import run
from re import match
from sys import exit
from yaml import safe_load

# Globals
source_path = ""
sd_path = ""

def get_firmware_folder_with_sn_or_none(sn):
    lookup_model_info = [
        {
            'sn_pattern': "^C333(?:13|34|42)",
            'folder_name': "Hero8 Black"
        },
        {
            'sn_pattern': "^C34613B45",
            'folder_name': "Hero10 Bones"
        },
        {
            'sn_pattern': "^C344(?:13|34|42)",
            'folder_name': "Hero9 Black"
        },
        {
            'sn_pattern': "^C346(?:13|42)",
            'folder_name': "Hero10 Black"
        },
        {
            'sn_pattern': "^C349(?:11|42)",
            'folder_name': "Hero11 Pismo"
        },
        {
            'sn_pattern': "^C34713",
            'folder_name': "Hero11 Sultan"
        },
        {
            'sn_pattern': "^C335(?:13|34)",
            'folder_name': "MAX"
        },
    ]
    result = None
    for info in lookup_model_info:
        
        pattern = info["sn_pattern"]
        folder = info["folder_name"]

        if match(pattern=pattern, string=sn):
            result = folder
            break

    return result


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

    return [item for item in listdir(cwd) if "SD" in item]


def select_firmware_option(ops: list, main_folder_name):
    
    ops.insert(0, "Factory Reset")

    print("Available firmwares (type x for scanning other device):")

    for i, op in enumerate(ops):
        print(f"{i}. {op}")

    while True:

        res = input("Your selection: ").lower()

        if res == "x":
            break
        elif not res.isdigit() or int(res) >= len(ops):
            print("Invalid option, please try again.")
        else:
            index = int(res)
            selection = ops[index]
            firmware_path = join(source_path, main_folder_name, selection)
            format_sd_card()
            print("Saving files to SD card, please wait...")
            if selection == "Factory Reset":
                open(join(sd_path, "factory_reset.txt"), 'a').close()
            else:
                run(["robocopy", firmware_path, sd_path, "/s", "/nfl", "/ndl", "/np", "/njh", "/njs"], shell=True)
            break


def format_sd_card():
    dirs = listdir(sd_path)
    if len(dirs) == 0:
        return
    print("Formatting sd card...")
    for item in dirs:
        rm_path = join(sd_path, item)
        if isfile(rm_path):
            run(["del", "/q", rm_path], shell=True)
        else:
            run(["rmdir", "/q", "/s", rm_path], shell=True)



load_config_paths()

print('Welcome to auto firmware for GO PRO.')

while True:
    
    res = input("Scan serial number of the camera (or type x to exit): ").upper()
    firmware_folder_name = get_firmware_folder_with_sn_or_none(res)
    
    if res == "X":
        break

    elif not firmware_folder_name:
        print("Invalid serial number or model not supported.")
    
    else:
        system("cls")
        print(f"{firmware_folder_name} model selected.")
        firmware_options = get_available_folder_names(firmware_folder_name)
        assure_sd_card_available()
        select_firmware_option(firmware_options, firmware_folder_name)
