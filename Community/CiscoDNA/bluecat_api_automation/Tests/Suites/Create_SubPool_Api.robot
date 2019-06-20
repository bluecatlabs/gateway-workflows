*** Settings ***
Resource  ../../Apis/CreateSubPoolApi.robot
Variables  ../Data/create_subpool.yaml

Force Tags      api     create_subpool

Suite Setup  Get Token And Set Header

*** Test Cases ***
SubPool Ipv4 Network Is Created Successfully
	[Tags]  create_subpool_ipv4_network_sucess
	When Create SubPool    ${IPV4_NETWORK}
	Then Response Status Should Be 200

SubPool Ipv6 Network Is Created Successfully
	[Tags]  create_subpool_ipv6_network_sucess
	When Create SubPool    ${IPV6_NETWORK}
	Then Response Status Should Be 200

SubPool Can Not Create Without View Parameter
	[Tags]  view_param_missing
	When Create SubPool    ${VIEW_MISSING}
	Then Response Status Should Be 400
	And Response Body Contains "Parameter 'view' is required"

SubPool Can Not Create Without SubpoolName Parameter
	[Tags]  poolname_param_missing
	When Create SubPool    ${POOLNAME_MISSING}
	Then Response Status Should Be 400
	And Response Body Contains "Parameter 'subpoolName' is required"

SubPool Can Not Create Without PoolCidr Parameter
	[Tags]  poolcidr_param_missing
	When Create SubPool    ${POOLCIDR_MISSING}
	Then Response Status Should Be 400
	And Response Body Contains "Parameter 'poolCidr' is required"

SubPool Can Not Create When Already Exist
	[Tags]  pool_aldready_exist
	When Create SubPool    ${SUBPOOL_EXIST}
	Then Response Status Should Be 405
	And Response Body Contains "pool '${SUBPOOL_EXIST.poolCidr}' already exists"

SubPool Can Not Create When Have Subpool
	[Tags]  pool_have_subpool
	When Create SubPool    ${CHILD_SUBPOOL_EXIST.POOL}
	Then Response Status Should Be 405
	And Response Body Contains "parent pool '${CHILD_SUBPOOL_EXIST.POOL.poolCidr}' has child pool '${CHILD_SUBPOOL_EXIST.CHILD.poolCidr}'"

SubPool Is Still Created When DHCPServerip Is Invalid
	[Tags]  create_subpool_dhcp_Invalid
	When Create SubPool    ${POOL_INVALID_DHCP_SERVER}
	Then Response Status Should Be 200

SubPool Is Still Created When DNSServerip Is Invalid
	[Tags]  create_subpool_dns_Invalid
	When Create SubPool    ${POOL_INVALID_DSN_SERVER}
	Then Response Status Should Be 200

SubPool Is Still Created When Client Option Is Invalid
	[Tags]  create_subpool_client_option_Invalid
	When Create SubPool    ${POOL_INVALID_CLIENT_OPTION}
	Then Response Status Should Be 200