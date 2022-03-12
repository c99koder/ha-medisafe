#  Copyright (C) 2022 Sam Steele
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# Base component constants
NAME = "Medisafe"
DOMAIN = "medisafe"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.2"

ATTRIBUTION = "Data provided by https://medisafe.com/"
ISSUE_URL = "https://github.com/c99koder/ha-medisafe/issues"

# Platforms
PLATFORMS = ["sensor"]

# Configuration and options
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
