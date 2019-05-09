*** Settings ***
Resource  ../../Apis/CreatePoolApi.robot
Variables  ../Data/create_pool.yaml

Force Tags  api     create_pool

Suite Setup  Get Token And Set Header

*** Test Cases ***
Ipv4 Pool Is Created Successfully
	[Tags]  create_ipv4_pool_sucess
	When Create Pool    ${IPV4}
	Then Response Status Should Be 200

Ipv6 Pool Is Created Successfully
	[Tags]  create_ipv6_pool_sucess
	When Create Pool    ${IPV6}
	Then Response Status Should Be 200

Pool Can Not Create Without View Parameter
	[Tags]  view_param_missing
	When Create Pool    ${VIEW_MISSING}
	Then Response Status Should Be 400
	And Response Body Contains "Parameter 'view' is required"

Pool Can Not Create Without PoolName Parameter
	[Tags]  poolname_param_missing
	When Create Pool    ${POOLNAME_MISSING}
	Then Response Status Should Be 400
	And Response Body Contains "Parameter 'poolName' is required"

Pool Can Not Create Without PoolCidr Parameter
	[Tags]  poolcidr_param_missing
	When Create Pool    ${POOLCIDR_MISSING}
	Then Response Status Should Be 400
	And Response Body Contains "Parameter 'poolCidr' is required"

Pool Can Not Create When Already Exist
	[Tags]  pool_aldready_exist
	When Create Pool    ${POOL_EXIST}
	Then Response Status Should Be 405
	And Response Body Contains "pool '${POOL_EXIST.poolCidr}' already exists"

Pool Can Not Create When Have Subpool
	[Tags]  pool_have_subpool
	When Create Pool    ${SUBPOOL_EXIST}
	Then Response Status Should Be 405
	And Response Body Contains "pool '${SUBPOOL_EXIST.poolCidr}' already exists"

Pool Is Still Create When DHCPServerip Is Invalid
	[Tags]  create_pool_dhcp_Invalid
	When Create Pool    ${POOL_INVALID_DHCP_SERVER}
	Then Response Status Should Be 200
	And Response Body Contains "Note: DHCP Server '${POOL_INVALID_DHCP_SERVER.DHCPServerip[0]}' is not exist under view '${POOL_INVALID_DHCP_SERVER.view}'"

Pool Is Still Create When DNSServerip Is Invalid
	[Tags]  create_pool_dns_Invalid
	When Create Pool    ${POOL_INVALID_DSN_SERVER}
	Then Response Status Should Be 200
	And Response Body Contains "Note: DHCP Server '${POOL_INVALID_DSN_SERVER.DHCPServerip[0]}' is not exist under view '${POOL_INVALID_DSN_SERVER.view}'"

Pool Is Still Create When Client Option Is Invalid
	[Tags]  create_pool_client_option_Invalid
	When Create Pool    ${POOL_INVALID_CLIENT_OPTION}
	Then Response Status Should Be 200