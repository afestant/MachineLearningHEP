#############################################################################
##  © Copyright CERN 2018. All rights not expressly granted are reserved.  ##
##                 Author: Gian.Michele.Innocenti@cern.ch                  ##
## This program is free software: you can redistribute it and/or modify it ##
##  under the terms of the GNU General Public License as published by the  ##
## Free Software Foundation, either version 3 of the License, or (at your  ##
## option) any later version. This program is distributed in the hope that ##
##  it will be useful, but WITHOUT ANY WARRANTY; without even the implied  ##
##     warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    ##
##           See the GNU General Public License for more details.          ##
##    You should have received a copy of the GNU General Public License    ##
##   along with this program. if not, see <https://www.gnu.org/licenses/>. ##
#############################################################################

"""
Methods to: configure parameters
"""

import sys
import os.path
from pkg_resources import resource_stream
import yaml

def get_default_config():
    """
    Load the default ML parameters
    """
    stream = resource_stream("machine_learning_hep.data", "config_ml_parameters.yml")
    return yaml.safe_load(stream)

def assert_config(config: dict):
    """
    Validate and return the configuration
    Args:
        config: The configuration dictionary to be checked
    """
    # Get defaults
    parameters = get_default_config()

    # Check for unknown parameters and abort since running entire machinery with wrong
    # setting (e.g. 'dotaining' instead of 'dotraining' might happen just by accident)
    # could be just overhead.
    for k in config:
        if k not in parameters:
            print(f"ERROR: Unkown parameter {k} in config")
            sys.exit(1)
        elif config[k] is None:
            print(f"ERROR: Missing value for parameter {k} in config")
            sys.exit(1)

    # Merge with defaults
    # NOTE Could be done via #config = {**configDefeaults, **config}
    #      but we want to inform the user if a default was used.
    for k in parameters:
        if k not in config:
            config[k] = parameters[k]["default"]
            print(f"Use default value {parameters[k]['default']} for parameter {k}")
        # If parameter is already set, check if consistent
        elif "choices" in parameters[k]:
            if config[k] not in parameters[k]["choices"]:
                print(f"ERROR: Invalid value {config[k]} for parameter {k}")
                sys.exit(1)

    # Can so far only depend on one parameter, change to combination
    # of parameters. Do we need to check for circular dependencies?
    for k in parameters:
        # check whether key k depends on anything
        if "depends" in parameters[k]:
            # get the depending value in the current config and check the
            # value against the depending value and force resetting if
            # necessary
            if (config[parameters[k]["depends"]["parameter"]]
                    == parameters[k]["depends"]["value"]
                    and config[k] != parameters[k]["depends"]["set"]):
                config[k] = parameters[k]["depends"]["set"]
                print("INFO: Parameter %s = %s enforced since it is required for %s == %s"
                      % (k, parameters[k]["depends"]["set"],
                         parameters[k]["depends"]["parameter"],
                         parameters[k]["depends"]["value"]))

    return config

def dump_default_config(path):
    """
    Write default configuration
    Args:
        path: full or relative path to where the config should be dumped
    """

    path = os.path.expanduser(path)
    parameters = get_default_config()
    config = {k: parameters[k]["default"] for k in parameters}

    with open(path, "w") as stream:
        yaml.safe_dump(config, stream, default_flow_style=False, allow_unicode=False)
