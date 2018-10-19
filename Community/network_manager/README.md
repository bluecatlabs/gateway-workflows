Copyright 2018 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

By: Chris Storz (cstorz@bluecatnetworks.com) Date: 10-18-2018 Gateway Version: 18.6.1 Description: This workflow will allow a user to add networks to a block owned by their group.

Required Configuration:
User group(s) (example "IT") and a block with a corresponding name. Users in that group will be able to create networks in that block only. This does not support multiple groups.

Optional Configuration:
The file rules.json will allow you to modify regex and messages for the naming convention required.