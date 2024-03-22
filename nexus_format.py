"""This module contains functions to read CBF files"""
import glob
import logging
import os
import re
from typing import Any, Dict

import cbf
import numpy as np
import h5py

# dict keywords are in concordance with MX Nexus application definition
def get_experimental_metadata(cbf_path, hdf5_outpath, cbf_folder) :
    """
    Get experimental parameters from header
    :param cbf_path: The path to the cbf file
    :return: experimental params dictionary. The available keys are:
    detector_description
    x_pixel_size
    y_pixel_size
    sensor_thickness
    omega_increment
    beam_center_x
    beam_center_y
    frame_time
    frame_period
    detector_distance
    omega
    beam_flux
    countrate_correction_count_cutoff
    filter_transmission
    incident_wavelength
    """
    params_dict: Dict[str, Any] = {}

    meta_lines = []
    with open(cbf_path, "rb") as cbf_file:
        text = cbf_file.read().split(b"_array_data.header_contents")[1].split(b"_array_data.data")[0]
        text_lines = text.replace(b"\r", b"").replace(b"\\\n", b"").split(b"\n")
        for text_line in text_lines:
            if text_line.startswith(b"# "):
                # meta_lines.append(text_line.decode("utf-8"))
                meta_lines.append(str(text_line, "utf-8"))

    for line in meta_lines:
        if line.startswith("# Detector: "):
            params_dict["detector_description"] = line.split("# Detector: ")[1].split(",")[0].split()
        if line.startswith("# Pixel_size "):
            params_dict["x_pixel_size"] = float(line.split("# Pixel_size ")[1].split()[0])
            params_dict["y_pixel_size"] = float(line.split("# Pixel_size ")[1].split()[3])
        if line.startswith("# Silicon sensor, thickness "):
            params_dict["sensor_thickness"] = float(line.split("# Silicon sensor, thickness ")[1].split()[0])
        if line.startswith("# Angle_increment "):
            params_dict["omega_increment"] = float(line.split("# Angle_increment ")[1].split()[0])
        if line.startswith("# Beam_xy "):
            params_dict["beam_center_x"] = [
                float(item) for item in line.split("# Beam_xy ")[1].split(" pixels")[0][1:-1].split(",")
            ][0]
            params_dict["beam_center_y"] = [
                float(item) for item in line.split("# Beam_xy ")[1].split(" pixels")[0][1:-1].split(",")
            ][1]
        if line.startswith("# Exposure_time "):
            params_dict["frame_time"] = float(line.split("# Exposure_time ")[1].split()[0])
        if line.startswith("# Exposure_period "):
            params_dict["frame_period"] = float(line.split("# Exposure_period ")[1].split()[0])
        if line.startswith("# Detector_distance "):
            params_dict["detector_distance"] = float(line.split("# Detector_distance ")[1].split()[0])
        if line.startswith("# Start_angle "):
            params_dict["omega"] = float(line.split("# Start_angle ")[1].split()[0])
        if line.startswith("# Flux "):
            params_dict["beam_flux"] = float(line.split("# Flux ")[1])
        if line.startswith("# Count_cutoff "):
            params_dict["countrate_correction_count_cutoff"] = float(line.split("# Count_cutoff ")[1].split()[0])
        if line.startswith("# Filter_transmission "):
            params_dict["filter_transmission"] = float(line.split("# Filter_transmission ")[1])
        if line.startswith("# Wavelength "):
            params_dict["incident_wavelength"] = float(line.split("# Wavelength ")[1].split()[0])

    if None in params_dict.values():
        keys_not_found = [key for key, value in params_dict.items() if value is None]
        for key in keys_not_found:
            logging.warning("'%s' not found in CBF header", key)

    #return params_dict

    h5master_outfile = hdf5_outpath + ("/") + cbf_folder.split("/")[-1] + "_master.h5"
    with h5py.File(h5master_outfile, 'w') as f:
        # Create a group to store attributes (optional)
        attribute_group = f.create_group('attributes')
        # Save dictionary items as attributes
        for key, value in params_dict.items():
            attribute_group.attrs[key] = value


def get_image_metadata(cbf_path: str) -> dict:
    """
    Get metadata from data
    :param cbf_path: The path to the cbf file
    :return: metadata dictionary
    """
    content = cbf.read(cbf_path)

    return content.metadata


def get_data(cbf_path: str) -> np.ndarray:
    """
    Get data
    :param cbf_path: The path to the cbf file
    :return: numpy array with diffraction data
    """
    content = cbf.read(cbf_path)

    return content.data


def count_decimals(number):
    """
    Count the number of decimal places in a given number.
    :param number: The number to count decimal places for.
    :return: The number of decimal places in the given number. Returns 0 if the number has no decimal places.
    """

    cadena = str(number)
    if "." in cadena:
        return len(cadena.rsplit(".", maxsplit=1)[-1])
    else:
        return 0


def cbf_num_to_angle(cbf_inp_dir: str, cbf_out_dir: str) -> str:
    """Converts the image numbers in CBF filenames to corresponding angles and creates symbolic links.
    :param cbf_inp_dir: Input directory containing CBF files.
    :param cbf_out_dir: Output directory where symbolic links will be created.
    :return: output path
    """

    cbf_path_list = sorted(glob.glob(f"{cbf_inp_dir}/*.cbf"))

    img_num_list = []
    img_num_len_list = []
    omega_list = []
    omega_increment_list = []

    for cbf_file in cbf_path_list:
        match = re.search(r"/([^/]+)_(\d+).cbf$", cbf_file)
        if match:
            img_prefix = match.group(1) + "_"
            img_num_str = match.group(2)
            img_num_len_list.append(len(img_num_str))
            img_num_list.append(int(img_num_str))

        experimental_metadata = get_experimental_metadata(cbf_file)
        omega_list.append(experimental_metadata["omega"])
        omega_increment_list.append(experimental_metadata["omega_increment"])

    wedge_list = [0]
    for num, omega in enumerate(omega_list[:-1]):
        wedge_list.append(round(omega_list[num + 1] - omega, count_decimals(omega_increment_list[0])))

    for num, (wedge, img_num_len) in enumerate(zip(wedge_list, img_num_len_list)):
        img_num = int(1 + num * (wedge / omega_increment_list[num]))
        img_num_str = str(img_num).zfill(img_num_len)
        if not os.path.islink(f"{cbf_out_dir}/{img_prefix}{img_num_str}.cbf"):
            os.system(f"ln -s {cbf_path_list[num]} {cbf_out_dir}/{img_prefix}{img_num_str}.cbf")

    return f"{cbf_out_dir}/{img_prefix}?.cbf"
