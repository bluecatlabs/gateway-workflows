# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

from pysnmp.hlapi import *

mp_model = {
    'v1': 0,
    'v2c': 1
}
def send_status_notification(trap_servers, service_point, service, status):
    print('Issuing Traps %s status with <%s>.' % (service, status))
    
    for trap_server in trap_servers:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            sendNotification(
                SnmpEngine(),
                CommunityData(trap_server['comstr'], mpModel=mp_model[trap_server['snmpver']]),
                UdpTransportTarget((trap_server['ipaddress'], trap_server['port'])),
                ContextData(),
                'trap',
                NotificationType(
                    ObjectIdentity('1.3.6.1.4.1.13315.6.3.2.0.1')
                ).addVarBinds(
                    ('1.3.6.1.4.1.13315.6.3.2.1.1.0', OctetString(service_point['name'])),
                    ('1.3.6.1.4.1.13315.6.3.2.1.2.0', OctetString(service)),
                    ('1.3.6.1.4.1.13315.6.3.2.1.3.0', OctetString(status))
                )
            )
        )
        if errorIndication:
            print(errorIndication)
            
            
def send_pulling_stopped_notification(trap_servers, service_point, pulling_severity, last_pulling_time):
    print('Issuing Traps pulling with <%s>.' % pulling_severity)
    timestamp = last_pulling_time.strftime("%Y/%m/%d %H:%M:%S.%f UTC")
    condition = 'Clear'
    severity = 20
    if pulling_severity == 'WARNING':
        condition = 'Set'
        severity = 40
    elif pulling_severity == 'CRITICAL':
        condition = 'Set'
        severity = 60
        
    for trap_server in trap_servers:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            sendNotification(
                SnmpEngine(),
                CommunityData(trap_server['comstr'], mpModel=mp_model[trap_server['snmpver']]),
                UdpTransportTarget((trap_server['ipaddress'], trap_server['port'])),
                ContextData(),
                'trap',
                NotificationType(
                    ObjectIdentity('1.3.6.1.4.1.13315.6.3.2.0.2')
                ).addVarBinds(
                    ('1.3.6.1.4.1.13315.6.3.2.1.4.0', OctetString(condition)),
                    ('1.3.6.1.4.1.13315.6.3.2.1.1.0', OctetString(service_point['name'])),
                    ('1.3.6.1.4.1.13315.6.3.2.1.5.0', Integer(severity)),
                    ('1.3.6.1.4.1.13315.6.3.2.1.6.0', OctetString(timestamp)),
                )
            )
        )

        if errorIndication:
            print(errorIndication)
