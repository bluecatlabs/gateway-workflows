*** Settings ***
Resource   ../Common/APIs.robot

*** Keywords ***
Release Pool
	[Arguments]  ${parameters}
	Log Many    ${parameters}
    ${actual}=    Get Body Response    DELETE  ${IPAM_POOL_ENDPOINT}/${parameters.view}/${parameters.poolCidr}
    Set Global Variable     ${actual}
