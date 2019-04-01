Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

By: Chris Storz (cstorz@bluecatnetworks.com)
Date: 03-19-2019
Gateway Version: 18.12.1
Description: This workflow provides slimmed down API interfaces for host record creation

Directions:

##################################################
LOGIN

REQUEST
curl -X POST \
  http://<gateway>/rest_login \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{
"username":"portal",
"password":"portal",
"bam_url":"http://bam.bluecatnetworks.com/Services/API?wsdl"
}'

RESPONSE

{
    "access_token": "bftRZDUZslsH6v/p8h7svrubC/TfJv0Hv4MwhV8+cSr30jP02vtYm0UYa6ze0NsIKOztgu7dWF3PdvqByrfuuA=="
}

##################################################
GET BC DATA

REQUEST

curl -X GET \
  http://<gateway>/itsm_api/get_bc_data \
  -H 'cache-control: no-cache' \
  -H 'auth: Basic  <token>'


RESPONSE

{
    "data": {
        "Config1": {
            "id": 383814,
            "views": [
                "internal",
                "external"
            ]
        },
        "Main": {
            "id": 100880,
            "views": [
                "internal",
                "external"
            ]
        },
        "Test": {
            "id": 378894,
            "views": [
                "default",
                "special"
            ]
        },
        "Training": {
            "id": 387805,
            "views": []
        }
    }
}

##################################################
GET ZONES

REQUEST

curl -X POST \
  http://<gateway>/itsm_api/get_zones \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{"configuration":"100880", "view":"internal", "zone":"blue"}'


RESPONSE

{
    "data": {
        "autocomplete_field": [
            "bluecat.com",
            "bluecat.net",
            "bluecatx.com"
        ],
        "select_field": [
            {
                "id": 100896,
                "txt": "bluecat.com"
            },
            {
                "id": 101427,
                "txt": "bluecat.net"
            },
            {
                "id": 112495,
                "txt": "bluecatx.com"
            }
        ]
    },
    "message": "",
    "status": "SUCCESS"
}

FAIL RESPONSE

{
    "data": {},
    "message": "No zones found for view: internal and hint: blue!",
    "status": "FAIL"
}
