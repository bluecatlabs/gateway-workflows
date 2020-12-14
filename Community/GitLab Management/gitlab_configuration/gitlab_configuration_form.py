# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField, CustomSubmitField
from ..gitlab_import import gitlab_import_config


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'gitlab_configuration'
    workflow_permission = 'gitlab_configuration_page'
    gitlab_url = CustomStringField(
        label='GitLab URL',
        default=gitlab_import_config.gitlab_url,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )

    default_group = CustomStringField(
        label='Default GitLab Group',
        default=gitlab_import_config.default_group,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    gitlab_import_directory = CustomStringField(
        label='GitLab Workflow Directory',
        default=gitlab_import_config.gitlab_import_directory,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    gitlab_import_utils_directory = CustomStringField(
        label='GitLab Util Directory',
        default=gitlab_import_config.gitlab_import_utils_directory,
        is_disabled_on_start=False,
        is_disabled_on_error=False
    )

    gw_utils_directory = CustomStringField(
        label='Gateway Util Directory',
        default=gitlab_import_config.gw_utils_directory,
        is_disabled_on_start=False,
        is_disabled_on_error=False
    )

    backups_folder = CustomStringField(
        label='Gateway Backup Folder',
        default=gitlab_import_config.backups_folder,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    secret_file = CustomStringField(
        label='Gateway Secret file and path',
        default=gitlab_import_config.secret_file,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    submit = CustomSubmitField(
        label='Save',
        is_disabled_on_start=False,
        is_disabled_on_error=False
    )

