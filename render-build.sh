#!/usr/bin/env bash

# Update packages
sudo apt update

# Install required dependencies
sudo apt install -y ffmpeg texlive texlive-latex-extra ghostscript

# Upgrade pip
pip install --upgrade pip
