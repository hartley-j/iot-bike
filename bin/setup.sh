#!/bin/bash

working_dir=$(pwd)

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Conda is not installed on this device. Installing Conda."

    wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
    
    # Check if wget succeeded
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download Miniforge installer."
        exit 1
    fi

    bash Miniforge3-$(uname)-$(uname -m).sh
fi

eval "$(conda shell.bash hook)"
# source ~/anaconda3/etc/profile.d/conda.sh

# Specify the conda environment name
conda_env_name="tracos"

# Check if the environment YAML file exists
if [ ! -f "tracos_raspi.yml" ]; then
    echo "Error: Environment setup file 'tracos_raspi.yml' not found."
    exit 1
fi

# Check if the conda environment exists
if ! conda env list | grep -w -q "$conda_env_name"; then
    echo "Creating conda environment '$conda_env_name' from tracos_raspi.yml..."
    # Create conda environment from environment_setup.yaml
    conda env create -f tracos_raspi.yml

    if [ $? -ne 0 ]; then
        echo "Error: Failed to create conda environment."
        exit 1
    fi
fi

# Activate the conda environment
echo "Activating conda environment '$conda_env_name'..."                                                                                                                                                                                                                                                                                                            

# Activate environment
conda activate "$conda_env_name"

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate conda environment."
    exit 1
fi

echo "Conda environment '$conda_env_name' is now activated."

echo "Checking that resources directory exists..."
if [ ! -d "$working_dir/camsystem/resources/" ]; then
  echo "Resources directory does not exist, please download the config files."
else
  echo "Resources directory exists."
fi

echo "Finished setup!"

