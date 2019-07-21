import os
import re
import time
import zipfile
import subprocess

import config.config

all_cap_csv = re.compile(r'capture-[0-9]+\.(cap|csv)$')


def zip_and_delete(settings: config.config.Settings):
    os.makedirs(settings.zip_path, exist_ok=True)

    # find out the current container number
    # we dont't want to override anything in case of a restart
    zip_ctr = 0
    while True:
        filename = f'container-{zip_ctr}.zip'
        if not os.path.isfile(os.path.join(settings.zip_path, filename)):
            break
        zip_ctr += 1

    print(f"\tFirst Container: container-{zip_ctr}.zip")

    saved_files = set()

    while True:
        files = os.listdir(settings.capture_path)
        
        zip_list = list()
        candidates = list()

        # first we find all .cap and .csv file
        for f in files:
            if f not in saved_files:
                match = all_cap_csv.match(f)

                if match is not None:
                    candidates.append(match.group(0))


        candidates = sorted(candidates)
        zip_list = candidates[:-settings.zip_file_buffer]

        print(zip_list)
        
        # make sure we have enough files (at least MinGroupSize)
        if len(zip_list) >= int(settings.zip_group_size):
            filename = f'container-{zip_ctr}.zip'
            with zipfile.ZipFile(os.path.join(settings.zip_path, filename), 'w') as zipper:
                for f in zip_list:
                    zipper.write(os.path.join(settings.capture_path, f), f, compress_type=zipfile.ZIP_DEFLATED)
                    saved_files.add(f)
                    # because we have likely no permission to clear the file
                    # we need to sudo our way around it
                    subprocess.call("cat /dev/null | sudo tee {}".format(os.path.join(settings.capture_path, f)),
                                    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            zip_ctr += 1

        time.sleep(settings.zip_freq)
