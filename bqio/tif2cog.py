from shutil import which
from typing import List
from pathlib import Path
import tempfile
from run_command import run_command


def tif2cog(input_paths: List[Path], output_cog_path: Path, type: str) -> None:

    if (len(input_paths) > 1):
        temp_vrt_path = (Path(tempfile.gettempdir()) / next(tempfile._get_candidate_names())).with_suffix(".vrt")
        vrt_command = ["gdalbuildvrt", "-separate", temp_vrt_path, *input_paths]
        run_command(vrt_command)
    else:
        temp_vrt_path = input_paths[0]
    
    if (type=='raw'): 
        cog_command = ['gdalwarp', '-of', 'COG', '-co', 'COMPRESS=DEFLATE', '-co', 'OVERVIEWS=IGNORE_EXISTING','-wo','NUM_THREADS=4', '-co', 'NUM_THREADS=ALL_CPUS','-multi', temp_vrt_path, output_cog_path]
    elif (type=='display'):
        cog_command = ['gdalwarp', '-of', 'COG', '-co', 'TILING_SCHEME=GoogleMapsCompatible', '-co', 'COMPRESS=DEFLATE', '-co', 'NUM_THREADS=ALL_CPUS','-co', 'OVERVIEWS=IGNORE_EXISTING', '-wo','NUM_THREADS=4','-multi', temp_vrt_path, output_cog_path]

    run_command(cog_command)

    if not output_cog_path.exists():
        raise FileNotFoundError("The COG was not created, see the full logs for more details.")

