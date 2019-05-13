*** Settings ***
Resource   ../Common/APIs.robot

*** Keywords ***
Get Token
    [Arguments]   ${payload}
    ${actual}=  Get Body Response    POST  ${IPAM_TOKEN_ENDPOINT}  ${payload}
    Set Global Variable     ${actual}
    [Return]  ${actual}
