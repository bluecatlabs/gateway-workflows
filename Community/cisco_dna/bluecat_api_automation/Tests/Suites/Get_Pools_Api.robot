*** Settings ***
Resource  ../../Apis/GetPoolsApi.robot
Variables  ../Data/get_pools.yaml

Force Tags  api     get_pools

Suite Setup  Get Token And Set Header

*** Test Cases ***
Get Pool Under View
	[Tags]  get_pool_under_view
	When Get Pools  ${GET_POOL_UNDER_VIEW}
	Then Response Status Should Be 200

Get Pool Under View And Parent Pool
	[Tags]  get_pool_under_view_parent_pool
	When Get Pools  ${GET_POOL_UNDER_VIEW_PARENT_POOL.view}     ${GET_POOL_UNDER_VIEW_PARENT_POOL.ippoolcidr}
	Then Response Status Should Be 200

Get Pool Under View And SubPool
	[Tags]  get_pool_under_view_subpool
	When Get Pools  ${GET_POOL_UNDER_VIEW_SUBPOOL.view}     ${GET_POOL_UNDER_VIEW_SUBPOOL.ippoolcidr}
	Then Response Status Should Be 200