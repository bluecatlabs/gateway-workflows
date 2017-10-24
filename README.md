# BlueCat DNS Gateway Workflows

The BlueCat DNS Integrity™ Gateway is a Python-based web utility that leverages the BlueCat Address Manager™ (BAM) API
to allow you to create custom workflows for common tasks in order to maximize efficiency of enterprise DNS operations.

The DNS Integrity Gateway consists of a set of Python classes forming an API to Address Manager and BlueCat DNS/DHCP Server (BDDS) along with
a customized Python Flask web framework for building custom user interfaces and REST endpoints. It can
run on most Linux variants with the correct packages installed.


## Installation

The workflows are ready to use, they need to be placed into the <bluecat_portal>/workflows/Examples folder.

There are two ways to do this:
1. Symbolic Link:
    ```bash
    ln -s <gateway-example-repo>/Examples <bluecat_portal>/workflows/.
    ```
    This will create a symlink to the repo without actually copying the files over. Any changes done to the workflwos will be reflected in the <gateway-example-repo> location

2. Copy
    ```bash
    cp -r <gatewat-example-repo>/Examples <bluecat_portal>/wofkows/.
    ```
    This will copy over all of the Example workflows

## Usage

Once the workflows have been either symlinked or copied over; just start the portal. You might have to adjust the
workflow permissions through the administrative workflow to make some of the UI Workflows visible in the navbar.


## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## History

TODO: Write history

## Credits

The Team:
---------
- Vadim Farafontov
- Viktor Fradkin
- Xiao Dong
- Evgeny Misotchnick
- Nikhil Jangi

Professional Services:
----------------------
- Bill Morton
- Murtaza Haider
- Chris Storz


## License

Copyright 2017 BlueCat Networks, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

