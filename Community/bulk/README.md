Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

By: Chris Storz (cstorz@bluecatnetworks.com)  
  Date: 03-11-2019  
  Gateway Version: 18.12.1  
  Description: This workflow provides a basic framework for building out bulk uploads in Gateway. The default behavior is to output to logs. Included are examples of how to do hosts or networks. 


Directions:
1. Add a csv example file at file_repository/downloads/template.csv
2. Copy tools.py and tools.json and tools.py to <gateway>/customizations/
3. Optionally uncomment "view" in your form file if that is a needed input
4. Write your code in the handlers in bulk_action.py
