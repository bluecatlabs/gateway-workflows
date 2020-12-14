# Overview
Bulk Engine provides a general purpose processor for simple mass 
add/delete operations. This is intended to be used for general cases with 
the understanding that highly specialized cases may require a custom 
written loader. The intended use cases are 1) population of example 
data, 2) populating scaffold data, 3) mirroring third party data in BAM 
for visbility, 4) migration of bare bones data

The design is to provide a simple interface to pass in options and a 
pre-transformed data structure.

# Installation
Place bulk_engine into the gateway customizations folder

# Dependencies
BAM 8.1.1+
+ Configuration
+ View
+ Top Level Block

# Usage


### Supported types
+ networks
+ ip addresses
+ dns records


##### type options

_*denotes required_

_†denotes required if not declared as a global_

_˚denotes global that can be overriden_


###### global type options

+ action* (ADD or DEL)
+ configuration˚† (Name)
+ view˚† (Name)
+ on_fail˚ (skip or abort)


###### network type options
+ address*
+ cidr*
+ name


###### ip_addresses type options
+ address*


###### dns_records type options
+ type* (A or C)
+ record* 
+ zone*
+ linked_fqdn
+ address


#### Example

```python

from bluecat_portal.customizations.bulk_engine.loader import load
import pprint

data = {
    'networks':[
        {'action':'ADD', 'address':'51.0.8.0', 'cidr':'24'},
        {'action':'ADD', 'address': '51.0.6.0', 'cidr': '27', 'name':'my_Other_net'},
        {'action':'ADD', 'address': '52.0.0.0', 'cidr': '24', 'name':'my_net'},
        {'action':'ADD', 'address': '51.0.0.0', 'cidr': '16'}
    ],
    'ip_addresses':[
        {'action': 'ADD', 'address': '51.0.8.5'},
        {'action': 'ADD', 'address': '51.0.8.17'},
        {'action': 'ADD', 'address': '51.0.85.5'}
    ],
    'dns_records':[
        {'action': 'ADD', 'type':'A', 'address': '51.0.8.6', 'record': 'abc', 'zone':'example.com'},
        {'action': 'ADD', 'type': 'C', 'linked_fqdn': 'abc.example.com', 'record': 'yyz', 'zone': 'example.com'}
    ]
}
globals = {
    "configuration": "BlueCat",
    "view": "internal",
    "on_fail": "skip"
}

r = load(data, **globals)
pprint.pprint(r)

```
