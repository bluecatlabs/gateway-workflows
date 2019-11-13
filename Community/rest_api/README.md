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

  By: Xiao Dong, Anshul Sharma, Chris Storz (cstorz@bluecatnetworks.com)
  Date: 06-09-2018  
  Gateway Version: 19.8.1  
  Description: This workflow will provide access to a REST-based API for BlueCat Gateway.
               Once imported and permissioned, documentation for the various available endpoints can
               be viewed by navigating to /api/v1/. 


How to contribute:

1. Identify a use case that is currently not covered by existing endpoints. The use case should be general and not overly specific to your implementation.
2. Review the code in dns_page.py and ip_space_page.py to get a general understanding of the constructs involved. Generally there are the following elements involved in a set of endpoints:
    1. Namespaces (where the endpoints are located)
    2. Models (for ingestion of JSON)
    3. Parser (for parsing to the model)
    4. Routes & methods (actual location, actions and logic)
3. Design your endpoints to follow [REST best practices](https://www.moesif.com/blog/api-guide/api-design-guidelines/ "REST best practices")
4. Implement and test your endpoints
5. Create a pull request and outline your use case and test cases for review

Example contribution:

Use case: Get next IP in a network. This is a commonly utilized API that isn't available at the time of writing.

Design: 
