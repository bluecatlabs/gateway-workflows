*** Settings ***
Resource  ../../Apis/GetViewApi.robot

Force Tags  api     get_view

*** Test Cases ***
Can Not Get View When Authentication Is Failed
	[Tags]  view_authen
	Given Set Header To API     auth    abcxyz
	When Get View
	Then Response Status Should Be 401
	And Response Body Contains "Authentication is failed"

Get View With Default Value
	[Tags]  view_default_value
	[Setup]  Get Token And Set Header
	When Get View
	Then Response Status Should Be 200
	And Total View Should Be Lesser Or Equal "500"

Get View From 1 To 10
	[Tags]  get_view_1_10
	[Setup]  Get Token And Set Header
	When Get View   10   1
	Then Response Status Should Be 200
	And Total View Should Be Lesser Or Equal "10"
