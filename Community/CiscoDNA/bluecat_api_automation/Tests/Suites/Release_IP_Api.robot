*** Settings ***
Resource  ../../Apis/ReleaseIPApi.robot
Variables  ../Data/release_ip.yaml

Force Tags  api     release_ip

Suite Setup  Get Token And Set Header

*** Test Cases ***
Release IP Is Successfully
	[Tags]  release_ip_succes
	When Release IP  ${IPs}
	Then Response Status Should Be 200

IP Is Not Released When View Not Exist
	[Tags]  ip_view_not_exit
	When Release IP  ${VIEW_NOT_EXIST}
	Then Response Status Should Be 400
	And Response Body Contains "View '${VIEW_NOT_EXIST.view}' does not exist"

IP Is Not Released When IP Invalid
	[Tags]  ip_invalid
	When Release IP  ${IP_INVALID}
	Then Response Status Should Be 400
	And Response Body Contains "address '${IP_INVALID.iplist}' is invalid"