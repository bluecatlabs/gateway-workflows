# Copyright 2019 BlueCat Networks. All rights reserved.
""" Cloud Discovery for AWS form - B.Shorland 2019 """

import os
from configparser import ConfigParser
from boto3.session import Session
from wtforms import SubmitField
from wtforms.validators import DataRequired
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import *
RELEASE_VERSION = "1.0.7"

# Creates a select choice for VPC regions based on boto3 sessions
S = Session()
REGIONS = S.get_available_regions('ec2')
X = [REGIONS[i//2] for i in range(len(REGIONS)*2)]
VPC_REGIONS = list(zip(X[::2], X[1::2]))

def module_path():
    """ Return module_path dir """
    return os.path.dirname(os.path.abspath(__file__))

def raw_synctable_data(*args, **kwargs):
    """Returns table formatted data for display in the Sync table """
    # pylint: disable=unused-argument
    return {
        "columns": [
            {"title": "Visiblity Start Time"},
            {"title": "AWS Region"},
            {"title": "BlueCat Configuration"},
            {"title": "State Changes"},
        ],
        "data": [
            ["", "", "", ""],
        ]
    }

def raw_synctable_data2(*args, **kwargs):
    """Returns table formatted data for display in the Sync table """
    # pylint: disable=unused-argument
    return {
        "columns": [
            {"title": "Visibility Time"},
            {"title": "AWS Region"},
            {"title": "Action"},
            {"title": "Instance"},
        ],
        "data": [
            ["", "", "", ""],
        ]
    }


def raw_discovery_data(*args, **kwargs):
    """Returns table formatted data for display in the Discovery table """
    # pylint: disable=unused-argument
    return {
        "order": [[1,"desc"]],
        "columns": [
            {"title": "Discovery Time"},
            {"title": "AWS Region"},
            {"title": "AWS Infrastructure"},
            {"title": "Count"},
        ],
        "data": [
            ["", "", "", ""],
        ]
    }


# Disable Pylint line to long rule due to embedded html
# pylint: disable=C0301
# Disable Pylint undefined variable rule due to lazy loading
# pylint: disable=E0602
class GenericFormTemplate(GatewayForm): # pylint: disable=too-few-public-methods
    """
    Cloud Atlas
    Note:
    When updating the form, remember to make the corresponding changes to the workflow pages
    """

    workflow_name = 'AWS'
    workflow_permission = 'aws_page'

    break_out = PlainHTML('</div></div>')
    status = PlainHTML('<div id="status" class="status disable-select"></div>')

    logo = "<div class='mytitle disable-select'>Discovery & Visibility - AWS</div><div id='exit' class='exit'><i class='material-icons'>clear</i></div>"
    title = PlainHTML(logo)

    panelstart_aws = PlainHTML('<button type="button" class="collapsible disable-select">AWS Credentials</button><div class="content disable-select">')
    aws_1 = PlainHTML('<br><b class="subtitle">Basic AWS Parameters</b><br>')
    aws_info = PlainHTML('<p>Basic required AWS parameters, API access key and API secret access key</p><br/>')

    para1 = PlainHTML("<div class='parallel'")
    aws_access_key_id = CustomStringField(
        label='AWS Access Key ID',
        required=True,
        default="",
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )
    para2= PlainHTML("</div>")
    para3 = PlainHTML("<div class='parallel'")
    aws_secret_access_key = CustomStringField(
        label='AWS Secret Access Key',
        required=True,
        default="",
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )
    para4 = PlainHTML("</div>")
    aws_info2 = PlainHTML('<br><b class="subtitle">Advanced AWS Parameters</b><p>Enable AWS MultiFactor Authentication or AWS Role Assumption, both options require an Amazon Resource Number (ARN)</p><br>')
    parab1 = PlainHTML("<div class='parallel'")
    mfa = CustomBooleanField(
        label='Enable AWS Multifactor Authentication',
        on_checked=['enable_mfa_token'],
        on_unchecked=['disable_mfa_token'],
        is_disabled_on_start=False,
        default=False,
    )

    parab1a = PlainHTML("</div>")
    parab1b = PlainHTML("<div class='parallel'")
    role_assume = CustomBooleanField(
        label='Enable AWS Role Assumption',
        on_checked=['enable_aws_role', 'enable_aws_session'],
        on_unchecked=['disable_aws_role', 'disable_aws_session'],
        is_disabled_on_start=False,
        default="",
    )
    parab1c = PlainHTML("</div>")

    parab1d = PlainHTML("<br><br>")

    parab1e = PlainHTML("<div class='parallel'")
    mfa_token = CustomStringField(
        label='AWS MFA token ARN',
        validators=[],
        default="",
        is_disabled_on_start=False,
    )
    parab1f = PlainHTML("</div>")
    para9 = PlainHTML("<div class='parallel'")
    aws_role = CustomStringField(
        label='AWS Role ARN',
        validators=[],
        default="",
        is_disabled_on_start=False,
    )

    para10 = PlainHTML("</div>")
    para11 = PlainHTML("<div class='parallel'")
    aws_session = CustomStringField(
        label='AWS Session Name <i>(optional)</i>',
        validators=[],
        default="",
        is_disabled_on_start=False,
    )
    para12 = PlainHTML("</div>")


    panelend_aws = PlainHTML('<br><br></div><p> </p>')

    panelstart_config = PlainHTML('<button type="button" class="collapsible disable-select">Configuration Options</button><div class="content disable-select">')
    aws_2 = PlainHTML('<br><b class="subtitle">AWS Region</b><br>')
    single_config_mode_desc = PlainHTML('<p>By default Cloud discovery imports all of the AWS infrastucture into a single BlueCat configuration named after the AWS region being discovered</p><br>')

    para5 = PlainHTML("<div class='parallel'")
    aws_region_name = NoPreValidationSelectField(
        label='AWS Region',
        default="us-east-2",
        choices=VPC_REGIONS
    )
    para6 = PlainHTML("</div>")

    para13 = PlainHTML("<div class='parallel'")
    configuration = CustomStringField(
        required=False,
        label='BlueCat Configuration',
        default="us-east-2",
        validators=[],
        is_disabled_on_start=False,
    )
    para14 = PlainHTML("</div>")

    single_config_mode_desc2 = PlainHTML('<br><p><b>NOTE</b> :- Changing the AWS Region will dynamically update the Bluecat configuration, this can optionally be overridden by manually entering a new configuration name into the field</p>')

    single_config_mode_desc3 = PlainHTML('<br><b class="subtitle">Per VPC configuration mode</b><p>If VPC subnets are overlapping in the AWS region then the per VPC Configration Mode should be enabled, a unique BlueCat configuration per VPC will then be dynamically created during discovery</p><br>')
    dynamic_config_mode = CustomBooleanField(
        label='Enable VPC Configuration Mode',
        on_checked=['disable_configuration', 'clear_configuration'],
        on_unchecked=['enable_configuration', 'clear_configuration'],
        is_disabled_on_start=False,
        default=False,
    )

    # purge_html = PlainHTML('<br><p><b>WARNING - Use Exteme Caution</b> :- <i>Purge will delete and recreate configurations in BlueCat Address Manager during discovery, all existing data within the target configuration will be destroyed</i></p><br>')
    purge_configuration = CustomBooleanField(
        label='',
        is_disabled_on_start=False,
        default=False,
    )

    panelend_config = PlainHTML('<br><br></div><p> </p>')

    panelstart_address_space= PlainHTML('<button type="button" class="collapsible disable-select">Discovery Options</button><div class="content disable-select">')
    aws_3 = PlainHTML('<br><b class="subtitle">Discover AWS resources</b><br>')
    para15 = PlainHTML("<div class='parallel'")
    aws_vpc_import = CustomBooleanField(
        default=False,
        label='AWS VPC private address space',
        on_checked=['enable_aws_public_blocks', 'enable_purge_configuration'],
        on_unchecked=['disable_aws_public_blocks', 'disable_purge_configuration', 'clear_aws_public_blocks', 'clear_purge_configuration'],
        is_disabled_on_start=False,
        )
    para16 = PlainHTML("</div>")
    para17 = PlainHTML("<div class='parallel'")
    aws_public_blocks = CustomBooleanField(
        label='AWS Public address space',
        default=False,
        is_disabled_on_start=False,
        )
    para18 = PlainHTML("</div>")
    para19 = PlainHTML("<div class='parallel'")
    aws_ec2_import = CustomBooleanField(
        label='EC2 instances',
        on_checked=['enable_import_amazon_dns'],
        on_unchecked=['disable_import_amazon_dns', 'clear_import_amazon_dns', 'clear_import_target_domain'],
        is_disabled_on_start=False,
        default=False,
    )
    para20 = PlainHTML("</div>")
    para21 = PlainHTML("<div class='parallel'")
    import_amazon_dns = CustomBooleanField(
        default=False,
        label='EC2 instance DNS records',
        on_checked=['enable_import_target_domain'],
        on_unchecked=['disable_import_target_domain'],
        is_disabled_on_start=False,
    )
    para22 = PlainHTML("</div>")

    para25 = PlainHTML("<div class='parallel'")
    aws_elbv2_import = CustomBooleanField(
        label='Elastic Load Balancers ELBv2',
        on_checked=[],
        on_unchecked=[],
        is_disabled_on_start=False,
        default=False,
    )
    para26 = PlainHTML("</div>")
    para27 = PlainHTML("<div class='parallel'")
    aws_route53_import = CustomBooleanField(
        label='AWS Route53 DNS',
        default=False,
        on_checked=[],
        on_unchecked=[],
        is_disabled_on_start=False,
    )
    para28 = PlainHTML("</div>")
    aws_4 = PlainHTML('<br><br><b class="subtitle">BlueCat Target Zone</b>')
    import_amazon_dns_html2 = PlainHTML('<p>When Discovery of Amazon EC2 instance DNS records is enabled, the discovery records are additionally created on a new BlueCat Target Zone</p><br>')
    para23 = PlainHTML("<div class='single'")
    import_target_domain = CustomStringField(
        required=False,
        label='BlueCat Target Zone',
        default="",
        validators=[],
        is_disabled_on_start=False,
    )
    para24 = PlainHTML("</div>")
    import_amazon_dns_html3 = PlainHTML('<p><b>NOTE</b> :- Discovery will utilise any AWS Name tag placed upon an EC2 instance as the hostname on the target zone if its DNS compliant, if a Name tag is not defined or not valid then the EC2 InstanceID will be used</p>')
    break5 = PlainHTML('<br>')



    panelend1 = PlainHTML('<br></div><p> </p>')

    panelstart_sync = PlainHTML('<button type="button" class="collapsible disable-select">Visibility Options</button><div class="content disable-select">')
    break6 = PlainHTML('<br>')
    aws_4a = PlainHTML('<b class="subtitle">Visiblity Options</b><br>')
    para33a = PlainHTML("<div class='parallel'>")
    aws_sync_start = CustomBooleanField(
        label='Enable Visibility after Discovery',
        on_checked=['enable_aws_sync_user', 'enable_aws_sync_pass','enable_sqs_sync_key', 'enable_sqs_sync_secret', 'enable_dynamic_deployment','disable_aws_sync_stop'],
        on_unchecked=['disable_aws_sync_user', 'disable_aws_sync_pass', 'disable_sqs_sync_key', 'disable_sqs_sync_secret', 'disable_dynamic_deployment', 'clear_dynamic_deployment', 'enable_aws_sync_stop'],
        default=False,
        is_disabled_on_start=False,
    )
    para34c = PlainHTML("</div>")
    para33b = PlainHTML("<div class='parallel'>")
    dynamic_deployment = CustomBooleanField(
        label='Update DNS (Selective Deployment)',
        default=False,
        is_disabled_on_start=False,
    )
    para34c1 = PlainHTML("</div>")
    para33b2 = PlainHTML("<div class='parallel'>")
    aws_sync_stop = CustomBooleanField(
        label='Disable All Visibility Tasks',
        on_checked=['disable_aws_sync_start', 'clear_aws_sync_start','disable_dynamic_deployment', 'clear_dynamic_deployment','disable_aws_sync_user','disable_aws_sync_pass','disable_sqs_sync_secret','disable_sqs_sync_key'],
        on_unchecked=['enable_aws_sync_start', 'clear_aws_sync_stop','enable_dynamic_deployment','enable_aws_sync_user','enable_aws_sync_pass','enable_sqs_sync_key','enable_sqs_sync_secret'],
        is_disabled_on_start=False,
    )

    para34a = PlainHTML("</div>")

    aws_5 = PlainHTML('<br><br><b class="subtitle">BlueCat User</b>')
    html8b = PlainHTML('<p>The BlueCat username and password should be a BlueCat account with API privilages and full permissions</p><br>')
    para29 = PlainHTML("<div class='parallel'>")
    aws_sync_user = CustomStringField(
        label='BlueCat Username',
        default="",
        validators=[],
        is_disabled_on_start=False,
    )

    para30 = PlainHTML("</div>")
    para31 = PlainHTML("<div class='parallel'>")
    aws_sync_pass = CustomStringField(
        label='BlueCat Password',
        default="",
        validators=[],
        is_disabled_on_start=False,
    )

    para32 = PlainHTML("</div>")
    aws_6 = PlainHTML('<br><b class="subtitle">AWS Service Account</b>')
    html8 = PlainHTML('<p>The AWS Service Account is used to continously monitor AWS EC2 changes, the service account must not have MultiFactor Authentication enabled</p><br>')
    para33 = PlainHTML("<div class='parallel'>")
    sqs_sync_key = CustomStringField(
        label='Service Account Key',
        default="",
        validators=[],
        is_disabled_on_start=False,
    )
    para34 = PlainHTML("</div>")
    para35 = PlainHTML("<div class='parallel'>")
    sqs_sync_secret = CustomStringField(
        label='Service Account Secret',
        default="",
        validators=[],
        is_disabled_on_start=False,
    )
    para36 = PlainHTML("</div><br>")

    panelend_sync = PlainHTML('<br><br></div><p> </p>')

    panelstart_discovery_stats= PlainHTML('<button type="button" class="collapsible disable-select">Discovery History</button><div class="content disable-select">')
    sync_disc_title = PlainHTML('<br><b class="subtitle">Discovery History</b><br>')
    chart_panel = PlainHTML('<div id="panels"></div>')

    discovery_table = TableField(
    workflow_name=workflow_name,
    permissions=workflow_permission,
    label='',
    table_features=raw_discovery_data(),
    is_disabled_on_start=False,
    )

    panelend_discovery_stats = PlainHTML('<br></div><p> </p>')


    # Sync Status
    panelstart_sync_stat = PlainHTML('<button type="button" class="collapsible disable-select">Visibility Status & History</button><div class="content disable-select">')
    sync_stat_title = PlainHTML('<br><b class="subtitle">Visibility Status</b><br>')
    sync_table = TableField(
    workflow_name=workflow_name,
    permissions=workflow_permission,
    label='',
    # data_function=raw_table_data,
    table_features=raw_synctable_data(),
    is_disabled_on_start=False,
    )

    sync_hist_title = PlainHTML('<hr><b class="subtitle">Visibility History</b><br>')

    sync_history_table = TableField(
    workflow_name=workflow_name,
    permissions=workflow_permission,
    label='',
    # data_function=raw_table_data,
    table_features=raw_synctable_data2(),
    is_disabled_on_start=False,
    )
    panelend_sync_stat = PlainHTML('<br><br></div>')

    submit1 = SubmitField(label='Start Discovery')

    submit2 = CustomButtonField(label='Start Discovery')


    mfa_code = CustomStringField(
        validators=[],
        is_disabled_on_start=False,
        default="",
        required=False,
    )
