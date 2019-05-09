*** Settings ***
Documentation  This file contains some basic kws for tests
Library     ExtendedRESTLibrary
Library     Collections
Resource   ../Apis/GetTokenApi.robot
Variables  ../config.yaml

*** Variables ***
#ENDPOINT
${IPAM_TOKEN_ENDPOINT}   ${GATEWAY_URL}/ipam/token
${IPAM_VIEW_ENDPOINT}   ${GATEWAY_URL}/ipam/view
${IPAM_POOL_ENDPOINT}   ${GATEWAY_URL}/ipam/pool
${IPAM_SUBPOOL_ENDPOINT}   ${GATEWAY_URL}/ipam/subpool
${IPAM_GET_POOL_ENDPOINT}   ${GATEWAY_URL}/ipam/ippool
${IPAM_RELEASE_IP_ENDPOINT}   ${GATEWAY_URL}/ipam/releaseip
${IPAM_ASSIGN_IP_ENDPOINT}   ${GATEWAY_URL}/ipam/assignip

*** Keywords ***
Response Status Should Be ${status}
    Integer   response status   ${status}

Response Body Contains "${content}"
	${actual}=  Convert To String   ${actual}
	Should Contain     ${actual}   ${content}

Set Header To API
	[Arguments]  ${tokenkey}    ${tokenvalue}
	${token}=   Create Dictionary  ${tokenkey}=${tokenvalue}
	Set Headers   ${token}

Get Token And Set Header
	${actual}=    Get Token   ${USER}
	Log Many    ${actual}
	${tokenkey}=   Get From Dictionary  ${actual}     tokenkey
	${tokenvalue}=   Get From Dictionary  ${actual}     tokenvalue
	Set Header To API  ${tokenkey}  ${tokenvalue}