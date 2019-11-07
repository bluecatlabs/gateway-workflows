# Copyright 2019 BlueCat Networks. All rights reserved.
""" Cloud Discovery for AWS form - B.Shorland 2019 """

import os
from configparser import ConfigParser
from boto3.session import Session
from wtforms import SubmitField
from wtforms.validators import DataRequired
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import *
RELEASE_VERSION = "1.04"

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
        "paging": False,"searching": False,"info": False,"autoWidth": False,
        "columns": [
            {"title": "Region"},
            {"title": "StartTime"},
            {"title": "Target Conf"},
            {"title": "State Changes"},
        ],
        "data": [
            ["", "", "", ""],
        ]
    }

def raw_discovery_data(*args, **kwargs):
    """Returns table formatted data for display in the Discovery table """
    # pylint: disable=unused-argument
    return {
        "paging": False,"searching": False,"info": False,"autoWidth": False,
        "columns": [
            {"title": "AWS Region"},
            {"title": "Discovery Time"},
            {"title": "Infrastructure Type"},
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
    # Get options from cloudatlas.conf, set to null if exception
    PARSER = ConfigParser()
    try:
        PARSER.read(module_path() + '/cloudatlas.conf')
    except Exception as anexception:
        print(str(anexception))

    # Get Basic AWS parameter defaults from .conf
    try:
        AWS_REGION = PARSER.get('aws_basic', 'aws_region')
    except KeyError as doesnotexist:
        AWS_REGION = ""
    try:
        AWS_ACCESS_KEY_ID = PARSER.get('aws_basic', 'aws_access_key')
    except KeyError as doesnotexist:
        AWS_ACCESS_KEY_ID = ""
    try:
        AWS_SECRET_ACCESS_KEY = PARSER.get('aws_basic', 'aws_secret_key')
    except KeyError as doesnotexist:
        AWS_SECRET_ACCESS_KEY = ""
    try:
        AWS_REGION_NAME = PARSER.get('aws_basic', 'aws_region')
    except KeyError as doesnotexist:
        AWS_REGION_NAME = ""

    # Get Address Space defaults from .conf
    try:
        PRIVATE_ADDRESS_SPACE = PARSER.get('discovery_options', 'private_address_space')
    except KeyError as doesnotexist:
        PRIVATE_ADDRESS_SPACE = False
    try:
        PUBLIC_ADDRESS_SPACE = PARSER.get('discovery_options', 'public_address_space')
    except KeyError as doesnotexist:
        PUBLIC_ADDRESS_SPACE = False
    try:
        PURGE_EXIST = PARSER.get('discovery_options', 'purge')
        PURGE_EXIST = PURGE_EXIST.lower()
        if PURGE_EXIST == "false":
            PURGE_EXIST = False
        else:
            PURGE_EXIST = True
    except KeyError as doesnotexist:
        PURGE_EXIST = False

    # Get EC2 instance defaults from .conf
    try:
        IMPORT_EC2 = PARSER.get('discovery_options', 'import_ec2')
    except KeyError as doesnotexist:
        IMPORT_EC2 = False
    try:
        IMPORT_ELBV2 = PARSER.get('discovery_options', 'import_elbv2')
    except KeyError as doesnotexist:
        IMPORT_ELBV2 = False
    try:
        IMPORT_DNS = PARSER.get('discovery_options', 'import_dns')
    except KeyError as doesnotexist:
        IMPORT_DNS = False
    try:
        IMPORT_ZONE = PARSER.get('discovery_options', 'target_zone')
    except KeyError as doesnotexist:
        IMPORT_ZONE = False

    # Get Route53 defaults from .conf
    try:
        ROUTE53 = PARSER.get('discovery_options', 'import_route53')
    except KeyError as doesnotexist:
        ROUTE53 = False

    # Get Continuous Sync defaults from .conf
    try:
        SYNC = PARSER.get('sync_options', 'enable_sync')
    except KeyError as doesnotexist:
        SYNC = False
    try:
        SYNCUSER = PARSER.get('sync_options', 'sync_user')
    except KeyError as doesnotexist:
        SYNCUSER = ""
    try:
        SYNCPASS = PARSER.get('sync_options', 'sync_pass')
    except KeyError as doesnotexist:
        SYNCPASS = ""
    try:
        SQSKEY = PARSER.get('sync_options', 'sqs_service_key')
    except KeyError as doesnotexist:
        SQSKEY = ""
    try:
        SQSSECRET = PARSER.get('sync_options', 'sqs_service_secret')
    except KeyError as doesnotexist:
        SQSSECRET = ""
    try:
        SELECTIVE_DEPLOY = PARSER.get('sync_options', 'dynamic_deployment')
    except KeyError as doesnotexist:
        SELECTIVE_DEPLOY = False

    # Get AWS Advanced defaults from .conf
    try:
        ROLEASSUME = PARSER.get('aws_advanced', 'role_assume')
    except KeyError as doesnotexist:
        ROLEASSUME = False
    try:
        AWSROLEARN = PARSER.get('aws_advanced', 'aws_role_arn')
    except KeyError as doesnotexist:
        AWSROLEARN = ""
    try:
        AWSSESSION = PARSER.get('aws_advanced', 'aws_session')
    except KeyError as doesnotexist:
        AWSSESSION = ""
    try:
        MFAON = PARSER.get('aws_advanced', 'mfa')
    except KeyError as doesnotexist:
        MFAON = False
    try:
        AWSMFAARN = PARSER.get('aws_advanced', 'aws_mfa_arn')
    except KeyError as doesnotexist:
        AWSMFAARN = ""

    workflow_name = 'AWS'
    workflow_permission = 'aws_page'

    break_out = PlainHTML('</div>')

    # logo = '<img src="' + module_path() + '/img/cat-logo-white-512.png' + '" alt="cathead" style="width:170px;height:170px;margin-right:15px;"><h1>Discovery & Visibility for AWS</h1>'
    logo = "<div class='mylogo'><div class='mylogo_top'><div class='disable-select'><img src='img/cat-logo-white-512.png' alt='cat head' height='48' width='48'><h1> Discovery & Visibility AWS</h1></div></div>"

    title = PlainHTML(logo)
    status = PlainHTML('<div id="status" class="status disable-select"></div>')
    panelstart_aws = PlainHTML('<button type="button" class="collapsible disable-select">AWS Credentials</button><div class="content disable-select">')
    aws_info = PlainHTML('<br><p>Basic required AWS parameters, AWS region, API access key and API secret access key</p><br/>')

    para1 = PlainHTML("<div class='parallel'")
    aws_access_key_id = CustomStringField(
        label='AWS Access Key ID',
        required=True,
        default=AWS_ACCESS_KEY_ID,
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )
    para2= PlainHTML("</div>")
    para3 = PlainHTML("<div class='parallel'")
    aws_secret_access_key = CustomStringField(
        label='AWS Secret Access Key',
        required=True,
        default=AWS_SECRET_ACCESS_KEY,
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )
    para4 = PlainHTML("</div>")

    para5 = PlainHTML("<div class='single'")
    aws_region_name = NoPreValidationSelectField(
        label='AWS Region',
        default=AWS_REGION_NAME,
        choices=VPC_REGIONS
    )
    para6 = PlainHTML("</div>")

    aws_info2 = PlainHTML('<hr><p>Enable the following option if the AWS account requires MultiFactor Authentication, the Amazon Resource Number (ARN) for the assigned MFA token is required</p><br>')
    mfa = CustomBooleanField(
        label='Enable AWS Multifactor Authentication',
        on_checked=['enable_mfa_token', 'enable_mfa_code'],
        on_unchecked=['disable_mfa_token', 'disable_mfa_code', 'clear_mfa_token', 'clear_mfa_code'],
        is_disabled_on_start=False,
        default=MFAON,
    )

    brmf2 = PlainHTML('<br>')
    para7 = PlainHTML("<div class='single'")
    mfa_token = CustomStringField(
        label='AWS MFA token ARN',
        validators=[],
        default=AWSMFAARN,
        is_disabled_on_start=False,
    )
    para8 = PlainHTML("</div>")

    adv_aws_info = PlainHTML('<hr><p>Enable the following options if there is an AWS role to assume, the Role Amazon Resource Number (ARN) is required and an optional session name </p><br>')
    role_assume = CustomBooleanField(
        label='Enable AWS Role Assumption',
        on_checked=['enable_aws_role', 'enable_aws_session'],
        on_unchecked=['disable_aws_role', 'disable_aws_session', 'clear_aws_role', 'clear_aws_session'],
        is_disabled_on_start=False,
        default=ROLEASSUME,
    )

    br_role2 = PlainHTML('<br>')
    para9 = PlainHTML("<div class='parallel'")
    aws_role = CustomStringField(
        label='AWS Role ARN',
        validators=[],
        default=AWSROLEARN,
        is_disabled_on_start=False,
    )
    para10 = PlainHTML("</div>")
    para11 = PlainHTML("<div class='parallel'")
    aws_session = CustomStringField(
        label='AWS Session Name',
        validators=[],
        default=AWSSESSION,
        is_disabled_on_start=False,
    )
    para12 = PlainHTML("</div>")


    panelend_aws = PlainHTML('<br></div><p> </p>')

    panelstart_config = PlainHTML('<button type="button" class="collapsible disable-select">Configuration Options</button><div class="content disable-select">')
    single_config_mode_desc = PlainHTML('<br><p>By default Cloud discovery imports all of the AWS infrastucture into a single BlueCat configuration named after the AWS region being discovered</p><br>')
    para13 = PlainHTML("<div class='single'")
    configuration = CustomStringField(
        required=False,
        label='BlueCat Configuration',
        default=AWS_REGION,
        validators=[],
        is_disabled_on_start=False,
    )
    para14 = PlainHTML("</div>")
    single_config_mode_desc2 = PlainHTML('<br><p><b>NOTE</b> :- Changing the AWS Region in the AWS Credentials panel will dynamically update the Bluecat configuration show above, this can optionally be overridden by manually entering a new configuration name into the field</p>')
    single_config_mode_desc3 = PlainHTML('<hr><p>If VPC subnets are overlapping in the AWS region then the per VPC Configration Mode should be enabled, a unique BlueCat configuration per VPC will then be dynamically created during discovery</p><br>')
    dynamic_config_mode = CustomBooleanField(
        label='Enable VPC Configuration Mode',
        on_checked=['disable_configuration', 'clear_configuration'],
        on_unchecked=['enable_configuration', 'clear_configuration'],
        is_disabled_on_start=False,
    )

    # purge_html = PlainHTML('<br><p><b>WARNING - Use Exteme Caution</b> :- <i>Purge will delete and recreate configurations in BlueCat Address Manager during discovery, all existing data within the target configuration will be destroyed</i></p><br>')
    purge_configuration = CustomBooleanField(
        label='',
        is_disabled_on_start=False,
        default=PURGE_EXIST,
    )

    panelend_config = PlainHTML('<br><br></div><p> </p>')

    panelstart_address_space= PlainHTML('<button type="button" class="collapsible disable-select">Discovery Options</button><div class="content disable-select">')
    html_import_aws_address_space = PlainHTML('<br><p></p>')
    para15 = PlainHTML("<div class='parallel'")
    aws_vpc_import = CustomBooleanField(
        default=PRIVATE_ADDRESS_SPACE,
        label='Discover AWS VPC private address space',
        on_checked=['enable_aws_public_blocks', 'enable_purge_configuration'],
        on_unchecked=['disable_aws_public_blocks', 'disable_purge_configuration', 'clear_aws_public_blocks', 'clear_purge_configuration'],
        is_disabled_on_start=False,
        )
    para16 = PlainHTML("</div>")
    para17 = PlainHTML("<div class='parallel'")
    aws_public_blocks = CustomBooleanField(
        label='Discover AWS Public address space',
        default=PUBLIC_ADDRESS_SPACE,
        is_disabled_on_start=False,
        )
    para18 = PlainHTML("</div>")
    para19 = PlainHTML("<div class='parallel'")
    aws_ec2_import = CustomBooleanField(
        label='Discover EC2 instances',
        on_checked=['enable_import_amazon_dns'],
        on_unchecked=['disable_import_amazon_dns', 'clear_import_amazon_dns', 'clear_import_target_domain'],
        is_disabled_on_start=False,
        default=IMPORT_EC2,
    )
    para20 = PlainHTML("</div>")
    para21 = PlainHTML("<div class='parallel'")
    import_amazon_dns = CustomBooleanField(
        default=IMPORT_DNS,
        label='Discover Amazon EC2 instance DNS records',
        on_checked=['enable_import_target_domain', 'enable_import_amazon_dns_cname', 'enable_import_amazon_dns_host'],
        on_unchecked=['disable_import_target_domain', 'disable_import_amazon_dns_cname', 'disable_import_amazon_dns_host', 'clear_import_target_domain', 'clear_import_amazon_dns_cname', 'clear_import_amazon_dns_host'],
        is_disabled_on_start=False,
    )
    para22 = PlainHTML("</div>")

    para25 = PlainHTML("<div class='parallel'")
    aws_elbv2_import = CustomBooleanField(
        label='Discover Elastic Load Balancers ELBv2',
        on_checked=[],
        on_unchecked=[],
        is_disabled_on_start=False,
        default=IMPORT_ELBV2,
    )
    para26 = PlainHTML("</div>")
    para27 = PlainHTML("<div class='parallel'")
    aws_route53_import = CustomBooleanField(
        label='Discover AWS Route53 DNS',
        default=ROUTE53,
        on_checked=[],
        on_unchecked=[],
        is_disabled_on_start=False,
    )
    para28 = PlainHTML("</div>")

    break1 = PlainHTML('<br>')
    import_amazon_dns_html2 = PlainHTML('<br><p>When Discover Amazon EC2 instance DNS records is enabled, the discovery records are additionally created on a new BlueCat Target Zone</p>')
    import_amazon_dns_html3 = PlainHTML('<p><b>NOTE</b> :- Discovery will utilise any AWS Name tag placed upon an EC2 instance as the hostname on the target zone if its DNS compliant, if a Name tag is not defined or not valid then the EC2 InstanceID will be used</p><br>')
    para23 = PlainHTML("<div class='single'")
    import_target_domain = CustomStringField(
        required=False,
        label='BlueCat Target Zone',
        default=IMPORT_ZONE,
        validators=[],
        is_disabled_on_start=False,
    )
    para24 = PlainHTML("</div>")

    break5 = PlainHTML('<br>')



    panelend1 = PlainHTML('<br></div><p> </p>')


    panelstart_discovery_stats= PlainHTML('<button type="button" class="collapsible disable-select">Discovery History</button><div class="content disable-select">')
    chart_panel = PlainHTML('<div id="panels"></div>')

    discovery_table = TableField(
    workflow_name=workflow_name,
    permissions=workflow_permission,
    label='',
    table_features=raw_discovery_data(),
    is_disabled_on_start=False,
    )

    panelend_discovery_stats = PlainHTML('<br></div><p> </p>')

    panelstart_sync = PlainHTML('<button type="button" class="collapsible disable-select">Visibility Options</button><div class="content disable-select">')
    break6 = PlainHTML('<br>')

    aws_sync_start = CustomBooleanField(
        label='Start Visibility after Discovery',
        on_checked=['enable_aws_sync_user', 'enable_aws_sync_pass', 'disable_aws_sync_stop'],
        on_unchecked=['disable_aws_sync_user', 'disable_aws_sync_pass', 'clear_aws_sync_user', 'clear_aws_sync_pass', 'enable_aws_sync_stop'],
        default=SYNC,
        is_disabled_on_start=False,
    )
    br4b1a = PlainHTML('<br>')
    para29 = PlainHTML("<div class='parallel'>")
    aws_sync_user = CustomStringField(
        label='BlueCat Username',
        default=SYNCUSER,
        validators=[],
        is_disabled_on_start=False,
    )
    para30 = PlainHTML("</div>")
    para31 = PlainHTML("<div class='parallel'>")
    aws_sync_pass = CustomStringField(
        label='BlueCat Password',
        default=SYNCPASS,
        validators=[],
        is_disabled_on_start=False,
    )

    para32 = PlainHTML("</div>")
    html8b = PlainHTML('<p>The BlueCat username and password should be a BlueCat account with API privilages and full permissions</p><br>')

    para33 = PlainHTML("<div class='parallel'>")
    sqs_sync_key = CustomStringField(
        label='AWS Service Account Key',
        default=SQSKEY,
        validators=[],
        is_disabled_on_start=False,
    )
    para34 = PlainHTML("</div>")
    para35 = PlainHTML("<div class='parallel'>")
    sqs_sync_secret = CustomStringField(
        label='AWS Service Account Secret',
        default=SQSSECRET,
        validators=[],
        is_disabled_on_start=False,
    )
    para36 = PlainHTML("</div>")

    html8 = PlainHTML('<br><p>The AWS Service Account is used to continously monitor AWS EC2 changes, the service account must not have MultiFactor Authentication enabled</p><br>')

    html8a = PlainHTML('<hr><p>The AWS Service Account entered above will require WRITE permissions to AWS SQS and CloudWatch to initialise the SQS queue and CloudWatch rule used for Visibility</p><br>')
    aws_sync_init = CustomBooleanField(
        label='Initialise AWS SQS queue and CloudWatch Rule',
        is_disabled_on_start=False,
    )


    aws_sync_init_htmla = PlainHTML('<br><p>If WRITE permission are not available to the Service Account, have an AWS administrator configure the SQS queue/CloudWatch rules as per the instructions on BlueCat Labs</p><br>')
    aws_sync_init_html = PlainHTML('<p><b>NOTE</b> :- The initialisation process is only required once per discovery region, the created SQS queue and CloudWatch rule are persistent once initialised has been run</p>')


    aws_sync_init_html2 = PlainHTML('<hr><p>Dynamic Update will only operate if a BlueCat DNS server and DNS master role is assigned to the prior discovered views or domains in the BlueCat configuration, a full DNS deployment is required after the master DNS role has been assigned</p>')
    aws_sync_init_html3 = PlainHTML('<br><p>If reverse resolution dynamic updates are a requirement then additionally assign the DNS master role to all the discovered AWS public blocks</p><br>')

    dynamic_deployment = CustomBooleanField(
        label='Dynamically Update DNS using Selective Deployment',
        default=SELECTIVE_DEPLOY,
        is_disabled_on_start=False,
    )

    panelend_sync = PlainHTML('<br></div><p> </p>')

    # Sync Status
    panelstart_sync_stat = PlainHTML('<button type="button" class="collapsible disable-select">Visibility Status</button><div class="content disable-select">')
    sync_table = TableField(
    workflow_name=workflow_name,
    permissions=workflow_permission,
    label='',
    # data_function=raw_table_data,
    table_features=raw_synctable_data(),
    is_disabled_on_start=False,
    )

    aws_sync_stop_html2 = PlainHTML('<br><hr><br><p>Select this option during a Discovery to stop all the running Visibility tasks</p><br>')
    aws_sync_stop = CustomBooleanField(
        label='Disable All Continuous Synchronisation',
        on_checked=['disable_aws_sync_start', 'clear_aws_sync_start', 'disable_aws_sync_init', 'clear_aws_sync_init'],
        on_unchecked=['enable_aws_sync_start', 'clear_aws_sync_stop', 'enable_aws_sync_init', 'clear_aws_sync_init'],
        is_disabled_on_start=False,
    )
    panelend_sync_stat = PlainHTML('<br><br></div>')

    submit1 = SubmitField(label='Start Discovery')
    submit2 = CustomButtonField(label='Start Discovery')
    myversionstring = "<div class='myversion'>Version " + RELEASE_VERSION + "</div>"
    myversion = PlainHTML(myversionstring)

    if MFAON:
        mfa_code = CustomStringField(
            validators=[],
            is_disabled_on_start=False,
            default="",
            required=True,
        )
    else:
        mfa_code = CustomStringField(
            validators=[],
            is_disabled_on_start=True,
            default="",
        )
