![alt text](logo.png "logo")

# BlueCat Cisco DNA IPAM Driver
The BlueCat Cisco DNA IPAM Driver consists of BlueCat Gateway Workflow which integrates with Cisco DNA Center
BlueCat Integration provides the ability to see network IP address scopes and determine the scopes that the enterprise owns directly within the DNA Center or the BlueCat Address Manager interface.

In SD-Access deployments, BlueCat integration provides:

- Access to existing IP address scopes, referred to as IP address pools in Cisco DNA Center. In BlueCat Address Manager DNAC global-pools are represented as network blocks and sub-pools as Networks (subnets)

- When configuring new IP address pools in Cisco DNA Center, the pools populate to the BlueCat Address Manager, reducing manual IP address management tasks.

# System Requirements

- BlueCat Address Manager
- BlueCat Gateway 18.10+
- Cisco DNA Center

## Installation

#### Installing the BlueCat DNA Center workflow into BlueCat Gateway™

    # sudo docker exec bluecat_gateway pip install netaddr --user 
    # sudo docker container restart bluecat_gateway

#### Prepare Cisco DNA Center™ 

## Usage

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

By: Brian Shorland (bshorland@bluecatnetworks.com)
Date: 03-05-2019
Gateway Version: 18.10
Description: Gateway workflow to be IPAM interface to integrate with Cisco DNA Centre


