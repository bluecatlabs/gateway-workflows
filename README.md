# BlueCat DNS Integrity Gateway Workflows
The BlueCat DNS Integrity™ Gateway is a Python-based web utility that leverages the BlueCat Address Manager™ (BAM) API to allow you to create custom workflows for common tasks in order to maximize efficiency of enterprise DNS operations.

The DNS Integrity Gateway consists of a set of Python classes forming an API to Address Manager and BlueCat DNS/DHCP Server (BDDS) along with a customized Python Flask web framework for building custom user interfaces and REST endpoints. It can run on most Linux variants with the correct packages installed.

## Installation
The workflows are ready to use; they just need to be placed into the `<bluecat_portal>/workflows` folder. The same can be done with the community examples.

This will copy over all of the Example workflows:

`cp -r <gateway-example-repo>/Examples/* <bluecat_portal>/workflows/Examples/.`

If only a specific set of workflows is required they can be copied into the workflows folder individually. However, ensure that there are `__init__.py` files present in your workflows folder structure leading up to the workflow itself. This is required by the Gateway in order to discover the workflow.

## Usage
Once the workflows have been either symlinked or copied over, just start the Gateway (portal). In order to use the added workflows the permissions have to be adjusted through the administrative permissions workflow. The workflows contained in the Examples folder are always up-to-date with the latest Gateway version. This is not the case for the community workflows. The contributing authors are required to specify the version of the Gateway for which the workflow was created or updated. While all community workflows will be reviewed, they are delivered "as is".

## Contributions
Contributing follows a review process: before a workflow is accepted it will be reviewed and then merged into the master branch. It will be the responsibility of the contributor to ensure that their workflow is supported for future releases of the Gateway.

#### Process
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Move your workflow into `Community/<your-workflow>`
4. Create `<your-workflow>/README.md` explaining what the workflow does. Use the Template below.
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

#### Community Template
When contributing a workflow ensure that it contains a `README.md` file with at least the following content:
```
Copyright YYYY BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

By: Your Name (youremail@domain.com)
Date: DD-MM-YYYY
Gateway Version: X.X.X
Description: Brief description of what the workflow does and the expected behavior
```

## Credits
The Gateway would be so much less without the following people. Thank you for contributing your time to making this project a success.

#### The Team:
- Vadim Farafontov
- Victor Fradkin
- Xiao Dong
- Nikhil Jangi
- David Cohen
- Delme Herbert
- Lana Litvak

#### Professional Services:
- Bill Morton
- Murtaza Haider
- Chris Storz

#### Special Thanks:
- Glenn McAllister
- Robert Barnhardt™
- Ekim Maurer

## License

Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
