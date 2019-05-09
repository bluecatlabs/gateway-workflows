*** Settings ***
Resource  ../../Apis/GetTokenApi.robot
Variables  ../../Tests/Data/get_token.yaml

Force Tags  api     get_token

*** Test Cases ***
Get Token Is Sucessfully
	[Tags]  get_token_sucessful
	When Get Token  ${VALID_ACCOUNT}
	Then Response Status Should Be 200
	And Response Body Contains "tokenkey"
	And Response Body Contains "tokenvalue"

Get Token Is Not Succesfully With Invalid Account
	[Tags]  get_token_fail
	When Get Token  ${INVALID_ACCOUNT}
	Then Response Status Should Be 401
	And Response Body Contains "Invalid username or password"