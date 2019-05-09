*** Settings ***
Resource   ../Common/APIs.robot

*** Keywords ***
Release SubPool
	[Arguments]  ${parameters}
	Log Many    ${parameters}
    ${actual}=    Get Body Response    DELETE  ${IPAM_SUBPOOL_ENDPOINT}/${parameters.view}/${parameters.poolCidr}
    Set Global Variable     ${actual}
