# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 2019-07-01
# Gateway Version: 19.5.1
# Description: Community Gateway workflow

# Your GitLab URL
gitlab_url = 'https://gitlab.company-name.net/api/v4/'

# Your personal token you created
# See https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

# Your default GitLab group
default_group = 'Professional Services'

# Base dir
workflow_dir = 'bluecat_portal'

# This is the folder to import from gitlab.
# If your root is not workflows, you'll need to enter in all the folders or workflows names
# Suggest using workflows in your GitLab structure
gitlab_import_directory = 'workflows'

# If not using a utils file leave blank
# GITLAB_IMPORT_UTILS_DIRECTORY=''
gitlab_import_utils_directory = 'ps'

# This is where the util dir lives on the gateway server
gw_utils_directory = 'ps'

# Folder where zip files will be when workflows and utils are downloaded
backups_folder = 'customer_backups'

# Path to secret file
secret_file = 'workflows/GitLab Management/gitlab_import/.secret'

# Do not change
gitlab_import_config_file = 'gitlab_import_config.py'
