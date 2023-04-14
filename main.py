from shutil import rmtree
from os.path import exists, join, isfile, getmtime
from os import getcwd, system, listdir, walk, remove, chmod
from subprocess import run
from re import match
from sys import exit
from yaml import safe_load
from stat import S_IRWXU

# Globals
SOURCE_PATH = ""
SD_PATH = ""
TEMP_FILES_PATH = ""


def get_model_with_sn_or_x(sn):
    lookup_model_info = [
        {"sn_pattern": "^C333(?:13|34|42)", "folder_name": "Hero8 Black"},
        {"sn_pattern": "^C34613B45", "folder_name": "Hero10 Bones"},
        {"sn_pattern": "^C344(?:13|34|42)", "folder_name": "Hero9 Black"},
        {"sn_pattern": "^C346(?:13|42)", "folder_name": "Hero10 Black"},
        {"sn_pattern": "^C349(?:11|42)", "folder_name": "Hero11 Pismo"},
        {"sn_pattern": "^C34713", "folder_name": "Hero11 Sultan"},
        {"sn_pattern": "^C335(?:13|34)", "folder_name": "MAX"},
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
    config_filename = "config.yml"

    if not exists(join(getcwd(), "config.yml")):
        exit("Error: Configuration file missing or misplaced")

    with open(config_filename, "r") as f:
        load = safe_load(f)

        global SOURCE_PATH, SD_PATH, TEMP_FILES_PATH

        try:
            SOURCE_PATH = load["source_path"]
            SD_PATH = load["sd_path"]
            TEMP_FILES_PATH = load["temp_files_path"]
        except:
            exit("Error: sintax issues in config file or missing parameters.")


def assure_sd_card_available():
    if not exists(SD_PATH):
        input("SD card unavailable, press enter to check again...")
        assure_sd_card_available()

def isdir(path):
    if match(".+\..+", path):
        return False
    else:
        return True

def get_available_folder_names(model):
    cwd = join(SOURCE_PATH, model)

    return [item for item in listdir(cwd) if isdir(join(cwd, item))]



def format_sd_card():
    dirs = listdir(SD_PATH)
    if len(dirs) == 0:
        return
    print("Formatting sd card...")
    for item in dirs:
        rm_path = join(SD_PATH, item)
        if isfile(rm_path):
            try:
                remove(rm_path)
            except:
                chmod(rm_path, S_IRWXU)
                remove(rm_path)
        else:
            rmtree(rm_path)


def get_firmware_selection_or_x(model_name):
    folder_names = get_available_folder_names(model_name)


    print("Available firmwares (type x for scanning other device):")

    for i, op in enumerate(folder_names):
        print(f"{i}. {op}")

    while True:
        user_response = input("Your selection: ").upper()

        if user_response == "X":
            return user_response
        elif not user_response.isdigit() or int(user_response) >= len(folder_names):
            print("Invalid option, please try again.")
        else:
            index = int(user_response)
            selection = folder_names[index]

            return selection
            


def update_firmware_to_temp_files(model, firmware_option):
    print("Updating local copy, this may take longer, please wait...")
    dest_path = join(TEMP_FILES_PATH, model, firmware_option)
    src_path = join(SOURCE_PATH, model, firmware_option)

    if exists(dest_path):
        rmtree(dest_path)

    run(
        ["robocopy", src_path, dest_path, "/s", "/nfl", "/ndl", "/np", "/njh", "/njs"],
        shell=True,
        check=False,
    )


def has_firmware_been_updated(model, firmware_option):
    local_root = join(TEMP_FILES_PATH, model, firmware_option)

    remote_root = join(SOURCE_PATH, model, firmware_option)

    last_modification_time_remote = max(
        [getmtime(root) for root, _, _ in walk(remote_root)]
    )

    last_modification_time_local = max(
        [getmtime(root) for root, _, _ in walk(local_root)]
    )

    return last_modification_time_local != last_modification_time_remote


def save_firmware_files_to_sd_card(model, firmware_option):
    firmware_path = join(TEMP_FILES_PATH, model, firmware_option)
    print("Saving files to sd card...")
    run(
        [
            "robocopy",
            firmware_path,
            SD_PATH,
            "/s",
            "/nfl",
            "/ndl",
            "/np",
            "/njh",
            "/njs",
        ],
        shell=True,
        check=False,
    )


load_config_paths()

print("Welcome to auto firmware for GO PRO.")

while True:
    sn = input("Scan serial number of the camera (or type x to exit): ").upper()
    model = get_model_with_sn_or_x(sn)
    if sn == "X":
        break

    elif not model:
        print("Invalid serial number or model not supported.")

    else:
        system("cls")
        print(f"{model} model selected.")
        firmware_selection = get_firmware_selection_or_x(model)
        if firmware_selection == "X":
            system("cls")
            continue

        local_firmware_path = join(TEMP_FILES_PATH, model, firmware_selection)

        if not exists(local_firmware_path) or has_firmware_been_updated(
            model, firmware_selection
        ):
            update_firmware_to_temp_files(model, firmware_selection)
        assure_sd_card_available()
        format_sd_card()
        save_firmware_files_to_sd_card(model, firmware_selection)
