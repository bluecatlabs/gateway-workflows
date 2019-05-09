*** Settings ***
Resource   ../Common/APIs.robot

*** Keywords ***
Create SubPool
	[Arguments]  ${payload}
	Log Many    ${payload}
    ${actual}=    Get Body Response    POST  ${IPAM_SUBPOOL_ENDPOINT}    ${payload}
    Set Global Variable     ${actual}
