# clean output folder
import os
import shutil


async def cleaner(output_folder):
    shutil.rmtree(output_folder, ignore_errors=True)
    try:
        os.remove(output_folder+'.zip')
    except:
        pass
