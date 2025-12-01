#!/usr/bin/env python3
import subprocess
import os

config = input("Config file (e.g., data/config.sumocfg): ").strip()
subprocess.run(["sumo-gui", "-c", "data/"+config, "--start"])