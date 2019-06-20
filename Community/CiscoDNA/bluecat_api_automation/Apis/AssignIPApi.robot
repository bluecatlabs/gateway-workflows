*** Settings ***
Resource   ../Common/APIs.robot

*** Keywords ***
Assign IP
	[Arguments]  ${payload}
	Log Many    ${payload}
    ${actual}=    Get Body Response    POST  ${IPAM_ASSIGN_IP_ENDPOINT}    ${payload}
    Set Global Variable     ${actual}
