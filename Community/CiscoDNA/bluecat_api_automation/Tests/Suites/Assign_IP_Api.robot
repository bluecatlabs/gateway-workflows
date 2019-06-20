*** Settings ***
Resource  ../../Apis/AssignIPApi.robot
Variables  ../Data/assign_ip.yaml

Force Tags  api     assign_ip

Suite Setup  Get Token And Set Header

*** Test Cases ***
IP Is Assigned Successfully
	[Tags]  assign_ip_succes
	When Assign IP  ${IPs}
	Then Response Status Should Be 200

IP Is Not Assigned When Missing View Param
	[Tags]  assign_missing_view_param
	When Assign IP  ${VIEW_MISSING}
	Then Response Status Should Be 400
	And Response Body Contains "Parameter 'view' is required"

IP Is Not Assigned When Missing IP List Param
	[Tags]  assign_missing_ip_list_param
	When Assign IP  ${IP_LIST_MISSING}
	Then Response Status Should Be 400
	And Response Body Contains "Parameter 'iplist' is required"

IP Is Not Assigned When View Not Exist
	[Tags]  assign_view_not_exit
	When Assign IP  ${VIEW_NOT_EXIST}
	And Response Body Contains "View '${VIEW_NOT_EXIST.view}' does not exist"

IP Is Not Assigned When IP Not Availabed
	[Tags]  ip_assign_not_availabed
	When Assign IP  ${IP_NOT_AVAILABLE}
	Then Response Status Should Be 405
	And Response Body Contains "${IP_NOT_AVAILABLE.iplist[0]} is not available"