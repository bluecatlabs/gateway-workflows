*** Settings ***
Resource  ../../Apis/ReleasePoolApi.robot
Variables  ../Data/release_pool.yaml

Force Tags  api     release_pool

Suite Setup  Get Token And Set Header

*** Test Cases ***
Release Pool Is Successfully
	[Tags]  release_pool_succes
	When Release Pool  ${POOL}
	Then Response Status Should Be 200

Pool Is Not Released When View Not Exist
	[Tags]  pool_view_not_exit
	When Release Pool  ${VIEW_NOT_EXIST}
	Then Response Status Should Be 400
	And Response Body Contains "View '${VIEW_NOT_EXIST.view}' does not exist"

Pool Is Not Released When PoolCidr Not Exist
	[Tags]  pool_not_exit
	When Release Pool  ${POOL_NOT_EXIST}
	Then Response Status Should Be 400