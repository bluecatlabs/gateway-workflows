*** Settings ***
Resource   ../Common/APIs.robot

*** Keywords ***
Get Pools
	[Arguments]  ${view}    @{args}
	${num}=  Get Length  ${args}
	${url}=     Set Variable If  ${num} > 0     ${IPAM_GET_POOL_ENDPOINT}/${view}?ippoolcidr=@{args}[0]    ${IPAM_GET_POOL_ENDPOINT}/${view}
	Log Many    ${url}
	${actual}=    Get Body Response    GET  ${url}
    Set Global Variable     ${actual}