# **Community GitLab Integration Workflow**
This workflow applies to BlueCat customers who use GitLab internally for their repository management and want to promote code from a development environment to GitLab, to Production.

___

### Requirements
**BlueCat Gateway version:** 19.5.1 and greater <br/>
**GitLab API version:** v4 <br/>
**Python 3rd party libraries:** io, os, re, shutil, sys, zipfile, datetime</br>

___

### Description/Example Usage
This GitLab Import workflow allows you to import all your workflow's and util file in a single click. 

Before importing, this will automatically backup your workflow's and util file to a defined folder on the Gateway server. Atfer completing the backup, Gateway will download the archive.zip file for the project selected. Below is the logic:

<div align="center">
<p align="center">
  <img width="75%" height="75%" src="img/workflow_logic.png">
</p>
</div>


___

### Prerequisites

1.  Create backup folder on the Gateway server. This is where all the zip files will be moved to. Below is the backup format: 

<p align="left">
  <img width="25%" height="25%" src="img/backups.png">
</p>


2.  Create a personal token in GitLab. To do this, at the top left select your username and select "Settings". Then, on the left side menu, select "Access Tokens"

<p align="left">
  <img width="50%" height="50%" src="img/gitlab_settings.png">
</p>




*  Enter the following data:

    * Token Name
    * Expire Date
    * Select the following Scopes
        * API
        * read_user
        * read_repository
        * read_registry



*  Click "Create personal access token"

<p align="left">
  <img width="40%" height="40%" src="img/gitlab_add_personal_token.png">
</p>

   * The next window will show your token. Copy this and paste it in the cuctom.py file (personal_token)

<p align="left">
  <img width="55%" height="55%" src="img/personal_token.png">
</p>

___

### Workflow Configuration

1.  Edit gitlab_import_config.py and update the following:
    * **url** - This is the IP Address for your GitLab instance. 
    * **personal_token** - This is the personal token used to authenticate with GitLab
    * **default_group** - This will be the parent where your projects and subgroups are under
    * **workflow_dir** - This is the base directory
    * **gitlab_import_directory** - This is the folder where your workflow's are that you wish to import from GitLab
    * **gitlab_import_utils_directory** - This is the folder where your util file is in GitLab. If you dont have a util file, leave blank
    * **gw_utils_directory** - This is where the util dir lives on the Gateway server
    * **backups_folder** - Folder where zip files will be when workflows and utils are downloaded



___

### Example of GitLab setup:
<div align="center">
<p align="center">
  <img width="75%" height="75%" src="img/gitlab_structure.png">
</p>
</div>

The above image, in this workflow in Gateway, we would select "professional-services/ps-poc/Testing Integrations".

The gitlab_import_config.py file would have the following:

*  default_group = 'Professional Services'
*  gitlab_import_directory = 'workflows'
*  gitlab_import_utils_directory = 'ps'
*  gw_utils_directory = 'bluecat_portal/ps'

The following would import the below into Gateway:

*  ps/util.py
*  workflow/Alias Record
*  workflow/Certified 
*  workflow/Deployment
*  workflow/Host Record
*  workflow/IPv4 Address

<!--
### Youtube Tutorial

<a href="http://www.youtube.com/watch?feature=player_embedded&v=YOUTUBE_VIDEO_ID_HERE" target="_blank">
 <img src="http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg" alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" />
</a>
-->

___

### Known Errors and Bugs: 

1)  If you put workflow's in the folder Admin or Administration, the import/backups will not work properly. Please refrain from using these directories.

___

©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved.
This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted.
Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.