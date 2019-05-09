*** Settings ***
Resource   ../Common/APIs.robot

*** Keywords ***
Create Pool
	[Arguments]  ${payload}
	Log Many    ${payload}
    ${actual}=    Get Body Response    POST  ${IPAM_POOL_ENDPOINT}    ${payload}
    Set Global Variable     ${actual}
