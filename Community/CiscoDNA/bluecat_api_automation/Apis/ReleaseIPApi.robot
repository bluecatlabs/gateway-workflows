*** Settings ***
Resource   ../Common/APIs.robot

*** Keywords ***
Release IP
	[Arguments]  ${parameters}
	Log Many    ${parameters}
    ${actual}=    Get Body Response    DELETE  ${IPAM_RELEASE_IP_ENDPOINT}/${parameters.view}?iplist=${parameters.iplist}
    Set Global Variable     ${actual}
