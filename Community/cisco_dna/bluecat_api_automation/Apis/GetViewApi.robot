*** Settings ***
Resource   ../Common/APIs.robot

*** Keywords ***
Get View
	[Arguments]  @{args}
	${num}=  Get Length  ${args}
	${url}=     Set Variable If  ${num} > 1     ${IPAM_VIEW_ENDPOINT}?limit=@{args}[0]&offset=@{args}[1]    ${IPAM_VIEW_ENDPOINT}
    ${actual}=    Get Body Response    GET  ${url}
    Set Global Variable     ${actual}

Total View Should Be Lesser Or Equal "${count}"
	${lenght}=  Get Length  ${actual}
	${result}=  Set Variable If  ${lenght}<= ${count}   True    False
	Should Be True  ${result}