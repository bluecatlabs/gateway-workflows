*** Settings ***
Resource  ../../Apis/ReleaseSubPoolApi.robot
Variables  ../Data/release_subpool.yaml

Force Tags  api     release_subpool

Suite Setup  Get Token And Set Header

*** Test Cases ***
Release SubPool Is Successfully
	[Tags]  release_subpool_succes
	When Release SubPool  ${SUBPOOL}
	Then Response Status Should Be 200

SubPool Is Not Released When View Not Exist
	[Tags]  subpool_view_not_exit
	When Release SubPool  ${VIEW_NOT_EXIST}
	Then Response Status Should Be 400
	And Response Body Contains "View '${VIEW_NOT_EXIST.view}' does not exist"

SubPool Is Not Released When PoolCidr Not Exist
	[Tags]  subpool_not_exit
	When Release SubPool  ${SUBPOOL_NOT_EXIST}
	Then Response Status Should Be 400