# Copyright 2019 BlueCat Networks. All rights reserved.
""" Cloud Discovery for AWS page - B.Shorland 2019 """
import os
import re
import json
from datetime import datetime, timedelta, timezone
from configparser import ConfigParser
import ipaddress
import boto3
from botocore.exceptions import ClientError
import requests
import requests.exceptions
from flask import render_template, flash, g, jsonify, copy_current_request_context
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from bluecat.util import has_response
from bluecat import api, route, util
from bluecat.internal.wrappers.rest_fault import RESTFault
from bluecat.api_exception import PortalException, APIException, BAMException
from bluecat.server_endpoints import get_result_template,empty_decorator
import config.default_config as config
from main_app import app
from app_user import UserSession
from .aws_form import GenericFormTemplate, raw_table_data
import logging
import collections


# pylint: disable=protected-access

JOB = ""
JOBS = []
DISCOVERYSTATUS = ""
SYNCSCHEDULER = BackgroundScheduler(daemon=True, timezone=pytz.utc)
SYNCSCHEDULER.start()
RELEASE_VERSION = "1.00"

def module_path():
    """ Returns module path dirname """
    return os.path.dirname(os.path.abspath(__file__))

def get_api():
    """Fetches API from flask globals:return: API
    """
    return g.user.get_api()

@route(app, '/aws/status', methods=['GET'])
def importstatus():
    """returns status in JSON for feedback on form"""
    response = jsonify(DISCOVERYSTATUS)
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1')
    return response

@route(app, '/aws/jobs', methods=['GET'])
def jobstatus():
    """returns sync job in JSON for feedback on form"""
    global JOBS
    templist = []
    for job in JOBS:
        g.user.logger.info('JOB ID: {id} JOB NAME: {name} FUNC: {func} TRIGGER: {trigger} max_instances: {max_instances}'.format(id=job.id, name=job.name, func=job.func, trigger=job.trigger, max_instances=job.max_instances))
        d = collections.OrderedDict()
        starttime = job.trigger
        starttime = str(job.trigger)
        starttime = starttime[5:]
        starttime = starttime[:-1]
        d['Region'] = job.id
        d['StartTime'] = starttime
        d['Target'] = job.name
        templist.append(d)
    return jsonify(templist)

@route(app, '/aws/aws_endpoint')
@util.workflow_permission_required('aws_page')
@util.exception_catcher
def aws_aws_page():
    """main endpoint"""
    form = GenericFormTemplate()
    return render_template(
        'aws_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/aws/form', methods=['POST'])
@util.workflow_permission_required('aws_page')
@util.exception_catcher
def aws_aws_page_form():
    """main form"""
    form = GenericFormTemplate()
    global aws_access_key_id, aws_secret_access_key, aws_session_token, aws_region_name, aws_session_expiration
    global assume_role, mfa, import_amazon_dns, target_zone, single_config_mode, configuration, dynamic_deployment
    global awspubs, DISCOVERYSTATUS, SYNCSCHEDULER, JOB
    if get_api().get_version() < '9.1.0':
        message = 'Error! Current BlueCat Address Manager version {version} is less than 9.1.0 and Cloud Discovery import will not work!'
        flash(message.format(version=get_api().get_version()))
        return render_template(
            'aws_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )

    parser = ConfigParser()
    parser.read(module_path() + '/cloudatlas.conf')

    if form.validate_on_submit():

        # Save the form values back to the cloudatlas.conf file on submission
        parser['aws_basic']['aws_region'] = form.aws_region_name.data
        parser['aws_basic']['aws_access_key'] = form.aws_access_key_id.data
        parser['aws_basic']['aws_secret_key'] = form.aws_secret_access_key.data

        parser['aws_advanced']['role_assume'] = str(form.role_assume.data)
        parser['aws_advanced']['aws_role_arn'] = form.aws_role.data
        parser['aws_advanced']['aws_session'] = form.aws_session.data
        parser['aws_advanced']['mfa'] = str(form.mfa.data)
        parser['aws_advanced']['aws_mfa_arn'] = form.mfa_token.data

        parser['discovery_options']['dynamic_config_mode'] = str(form.dynamic_config_mode.data)
        parser['discovery_options']['private_address_space'] = str(form.aws_vpc_import.data)
        parser['discovery_options']['public_address_space'] = str(form.aws_public_blocks.data)
        parser['discovery_options']['purge'] = str(form.purge_configuration.data)
        parser['discovery_options']['import_ec2'] = str(form.aws_ec2_import.data)
        parser['discovery_options']['import_elbv2'] = str(form.aws_elbv2_import.data)
        parser['discovery_options']['import_dns'] = str(form.import_amazon_dns.data)
        parser['discovery_options']['target_zone'] = form.import_target_domain.data
        parser['discovery_options']['import_route53'] = str(form.aws_route53_import.data)

        parser['sync_options']['enable_sync'] = str(form.aws_sync_start.data)
        parser['sync_options']['sync_user'] = form.aws_sync_user.data
        parser['sync_options']['sync_pass'] = form.aws_sync_pass.data
        parser['sync_options']['sqs_service_key'] = form.sqs_sync_key.data
        parser['sync_options']['sqs_service_secret'] = form.sqs_sync_secret.data
        parser['sync_options']['dynamic_deployment'] = str(form.dynamic_deployment.data)

        with open(module_path() + '/cloudatlas.conf', 'w') as configfile:
            parser.write(configfile)

        if not form.dynamic_config_mode.data:
            try:
                conf_entity = get_api().create_configuration(form.configuration.data)
            except BAMException:
                conf_entity = get_api().get_configuration(form.configuration.data)
            conf_entity.set_property('configurationGroup', 'Amazon Web Services')
            conf_entity.update()
            single_config_mode = True
        else:
            single_config_mode = False

        if form.role_assume.data and form.mfa.data:
            assume_role = True
            mfa = True
            aws_access_key_id, aws_secret_access_key, aws_session_token, aws_region_name, aws_session_expiration = connect_aws(form.aws_region_name.data, form.aws_access_key_id.data, form.aws_secret_access_key.data, form.aws_role.data, form.aws_session.data, form.mfa_token.data, form.mfa_code.data)
        else:
            assume_role = False
            mfa = False
            aws_access_key_id = form.aws_region_name.data
            aws_secret_access_key = form.aws_access_key_id.data
            aws_region_name = form.aws_region_name.data
        if form.import_amazon_dns.data:
            import_amazon_dns = True
        else:
            import_amazon_dns = False
        if form.import_target_domain.data:
            target_zone = form.import_target_domain.data
        if form.aws_sync_stop.data:
            JOB = False
            DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Terminating Visibility"
        else:
            JOB = True
        if form.dynamic_deployment.data:
            dynamic_deployment = True

        # Create AWS device type and sub-type if they don't exist
        DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Adding AWS Device Types"
        aws_type = get_or_create_device_type(0, "Amazon Web Services", 'DeviceType')
        ec2_subtype = get_or_create_device_type(aws_type.get_id(), "EC2 Instance", 'DeviceSubtype')
        elbv2_subtype = get_or_create_device_type(aws_type.get_id(), "ELBv2 LoadBalancer", 'DeviceSubtype')

        # Check and Create AWS Device udfs
        DISCOVERYSTATUS = "Adding AWS UDFs to BlueCat"
        check_and_create_aws_udfs()

        g.user.logger.info(form.purge_configuration.data,"PURGE")

        # AWS VPC Discovery
        if form.aws_vpc_import.data:
            if form.purge_configuration.data and single_config_mode:
                g.user.logger.info("P")
                DISCOVERYSTATUS = "Purging BlueCat Configuration " + form.configuration.data
                try:
                    get_api().delete_configuration(form.configuration.data)
                except PortalException:
                    pass # Conf doesn't exist in BAM

            # If running with in regional config mode and public import enabled
            if single_config_mode and form.aws_public_blocks.data:
                importawspublic(form.configuration.data)
            # Create the required BAM configurations
            discovervpcs()

        # AWS EC2 Discovery
        if form.aws_ec2_import.data:
            discoverec2(aws_type,ec2_subtype)

        # AWS ELBv2 Discovery
        if form.aws_elbv2_import.data:
            discoverelbv2(aws_type,elbv2_subtype)

        # AWS Route53 Discovery
        if form.aws_route53_import.data:
            discoverr53()

        if form.aws_sync_init.data:
            DISCOVERYSTATUS = "Initialising Continuous Visibility"
            g.user.logger.info('- AWS Realtime Syncronisation - Initialising SQS bluecat queue')
            if assume_role and mfa:
                sqs = boto3.client('sqs', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
                sqs_resource = boto3.resource('sqs', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
                cw_client = boto3.client('events', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
            else:
                sqs = boto3.client('sqs', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
                sqs_resource = boto3.resource('sqs', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
                cw_client = boto3.client('events', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
            try:
                aws_sqs_queue = sqs.get_queue_url(QueueName='Bluecat.fifo')
                g.user.logger.info('AWS SQS Queue "{data}"'.format(data=aws_sqs_queue))
                g.user.logger.info('AWS SQS Queue URL "{data}"'.format(data=aws_sqs_queue['QueueUrl']))
                queue_d = sqs_resource.get_queue_by_name(QueueName='Bluecat.fifo')
                g.user.logger.info('AWS SQS Queue ARN "{data}"'.format(data=queue_d.attributes['QueueArn']))
                aws_queue_arn = queue_d.attributes['QueueArn']
                aws_sqs_queue = aws_sqs_queue['QueueUrl']
            except ClientError as thisexception:
                if thisexception.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                    g.user.logger.info('- AWS Realtime Syncronisation - bluecat queue not found, creating')
                    if assume_role and mfa:
                        sqs_resource = boto3.resource('sqs', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
                    else:
                        sqs_resource = boto3.resource('sqs', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
                    queue = sqs_resource.create_queue(QueueName='Bluecat.fifo', Attributes={'FifoQueue': 'true', 'DelaySeconds': '0', 'VisibilityTimeout': '3600', 'ContentBasedDeduplication': 'true', 'MessageRetentionPeriod': '60', 'ReceiveMessageWaitTimeSeconds': '20'})
                    g.user.logger.info('Created Queue "{data}"'.format(data=queue.url))
                    aws_sqs_queue = queue.url
                    queue_d = sqs_resource.get_queue_by_name(QueueName='Bluecat.fifo')
                    g.user.logger.info('AWS SQS Queue ARN "{data}"'.format(data=queue_d.attributes['QueueArn']))
                    aws_queue_arn = queue_d.attributes['QueueArn']
                    sqs.tag_queue(QueueUrl=queue.url, Tags={'message group ID':'Bluecat'})
            g.user.logger.info('- AWS Realtime Syncronisation - Initialising CloudWatch to SQS alert rule')
            cw_event_pattern = '{"source": ["aws.ec2"],"detail-type": ["EC2 Instance State-change Notification"]}'
            response = cw_client.put_rule(Name='Bluecat', EventPattern=cw_event_pattern, State='ENABLED', Description='Rule sending all EC2 event status changes messages to Bluecat SQS FIFO queue for processing by Cloud Discovery')
            g.user.logger.info('Put Rule "{data}"'.format(data=response))
            response = cw_client.put_targets(Rule='Bluecat', Targets=[{'Arn': queue_d.attributes['QueueArn'], 'Id': 'Bluecat', 'SqsParameters': {'MessageGroupId': 'Bluecat'}}])
            response = cw_client.describe_rule(Name='Bluecat')
            g.user.logger.info('Describe Rule "{data}"'.format(data=response))
            g.user.logger.info('Rule ARN "{data}"'.format(data=response['Arn']))
            arn = response['Arn']
            # SQS policy template to add CloudWatch event to SQS queue permissions
            policy = {
                "Version": "2012-10-17",
                "Id": "{}/SQSDefaultPolicy".format(aws_queue_arn),
                "Statement":
                [
                    {
                        "Sid":"AWSEvents_Bluecat_Bluecat",
                        "Effect":"Allow",
                        "Principal":
                            {
                                "Service": "events.amazonaws.com"
                            },
                        "Action":"sqs:SendMessage",
                        "Resource":"{}".format(aws_queue_arn),
                        "Condition":
                            {
                                "ArnEquals":
                                {
                                    "aws:SourceArn": "{}".format(arn)
                                }
                            }
                    }
                ]
            }
            sqs.set_queue_attributes(QueueUrl=aws_sqs_queue, Attributes={'Policy': json.dumps(policy)})
            response = cw_client.list_targets_by_rule(Rule='Bluecat')
            g.user.logger.info('Rule Target "{data}"'.format(data=response))

        if form.aws_sync_start.data:
            DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Starting Visibility for " + aws_region_name
            g.user.logger.info('- AWS Realtime Syncronisation - Starting Syncronisation')
            if single_config_mode and form.configuration.data:
                single_config_mode = True
                configuration = form.configuration.data
            else:
                single_config_mode = False
                configuration = False

            @copy_current_request_context
            def syncjob():
                global aws_region_name, assume_role, single_config_mode
                global configuration, import_amazon_dns, target_zone, dynamic_deployment
                global DISCOVERYSTATUS, SYNCSCHEDULER, JOB, JOBS

                awspubs = awsblocks(form.aws_region_name.data)

                bam_url = config.api_url[0][1]
                username = form.aws_sync_user.data
                password = form.aws_sync_pass.data

                u = UserSession.validate(bam_url, username, password)
                token = u.get_unique_name()
                g.user = u
                g.user.logger.info('**** Cloud Discovery Realtime Sync Job ****')

                service_access_key = form.sqs_sync_key.data
                service_secret_key = form.sqs_sync_secret.data
                sts_client, sqs, sqs_resource, aws_sqs_queue, ec2_client, ec2_resource = connect_sqs(service_access_key, service_secret_key, aws_region_name)

                aws_sqs_queue = sqs.get_queue_url(QueueName='Bluecat.fifo')
                queue_d = sqs_resource.get_queue_by_name(QueueName='Bluecat.fifo')
                aws_sqs_queue = aws_sqs_queue['QueueUrl']

                SQS_QUEUE = {"QUEUE": aws_sqs_queue ,"REGION": aws_region_name, "CONFIGURATION": configuration, "TARGETZONE": target_zone}
                g.user.logger.info(SQS_QUEUE['QUEUE'],"QUEUE")
                g.user.logger.info(SQS_QUEUE['REGION'],"REGION")
                g.user.logger.info(SQS_QUEUE['CONFIGURATION'],"CONFIGURATION")
                g.user.logger.info(SQS_QUEUE['TARGETZONE'],"TARGETZONE")

                DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Visibility Started for " + SQS_QUEUE['REGION']

                # Get the Device Type ID for AWS and EC2 DeviceSubtype
                aws_type = g.user.get_api()._api_client.service.getEntityByName(0, "Amazon Web Services", 'DeviceType')
                aws_type = aws_type.id
                aws_type_ec2 = g.user.get_api()._api_client.service.getEntityByName(aws_type, "EC2 Instance", 'DeviceSubtype')
                aws_type_ec2 = aws_type_ec2.id

                while True:
                    if not JOB:
                        DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Visibility Terminated"
                        JOBS = []
                        return

                    g.user = u
                    # Check the SQS session expiration
                    timenow = datetime.now(timezone.utc)
                    timeexpire = sts_client["Credentials"]["Expiration"]
                    time_difference = timeexpire - timenow
                    expiration_timer = time_difference_in_minutes = time_difference / timedelta(minutes=1)
                    if expiration_timer < 1:
                        g.user.logger.info("SQS Session - Less than 1 minutes till session expiration")
                        g.user.logger.info("SQS Session - Refreshing session....")
                        try:
                            sts_client, sqs, sqs_resource, aws_sqs_queue, ec2_client, ec2_resource = connect_sqs(service_access_key, service_secret_key, SQS_QUEUE['REGION'])
                        except Exception as thisexception:
                            g.user.logger.info(thisexception)

                    # Try and get the next message from the SQS queue
                    try:
                        g.user.logger.info('Checking SQS queue {} for message'.format(SQS_QUEUE['QUEUE']))
                        messages = sqs.receive_message(QueueUrl=SQS_QUEUE['QUEUE'], MaxNumberOfMessages=1, WaitTimeSeconds=5) # Get the next message from queue
                    except Exception as thisexception:
                        g.user.logger.info(str(thisexception), "Exception receiving message")
                        if "expired_token" in str(thisexception):
                            g.user.logger.info("Refresh of AWS session required")

                    if 'Messages' in messages: # when the queue is exhausted, the response dict contains no 'Messages' key
                        for message in messages['Messages']: # 'Messages' is a list
                            body = json.loads(message['Body'])
                            g.user.logger.info(message, 'Message')
                            DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - " + body['detail']['state'] + " " + body['detail']['instance-id'] + " (" + SQS_QUEUE['REGION'] + ")"
                            # Handle terminated EC2 state
                            if body['detail']['state'] == "terminated":
                                # login to BAM using the API account, do stuff, logout
                                conn = api.API(bam_url)
                                conn.login(form.aws_sync_user.data,form.aws_sync_pass.data)
                                DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Terminating " + str(body['detail']['instance-id']) + " (" + SQS_QUEUE['REGION'] + ")"
                                g.user.logger.info('EC2 Instance Terminated - Deleting')
                                instanceid = body['detail']['instance-id']
                                instanceid = instanceid.split()
                                instance = ec2_client.describe_instances(InstanceIds=instanceid)
                                g.user.logger.info(instance)
                                for r in instance['Reservations']:
                                    for i in r['Instances']:
                                        g.user.logger.info(i['InstanceId'], "Instance ID")
                                        config_list = set()
                                        configurations = conn.get_configurations()
                                        g.user.logger.info(configurations)
                                        for conf in configurations:
                                            g.user.logger.info(conf)
                                            config_list.add(conf.get_id())
                                        for conf_id in config_list:
                                            try:
                                                dev = conn._api_client.service.getEntityByName(conf_id, i['InstanceId'], "Device")
                                                if dev.id != 0:
                                                    g.user.logger.info(i['InstanceId'], "Instance Device Found")
                                                    g.user.logger.info(conf_id, "In Config")
                                                    g.user.logger.info(i['InstanceId'], "Deleting Terminated Device")
                                                    conn._api_client.service.delete(dev.id)
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception)
                                if import_amazon_dns:
                                    if dynamic_deployment:
                                        hostrecs = conn.custom_search("EC2InstanceID=%s" %i['InstanceId'], "HostRecord")
                                        hosts = []
                                    for host in hostrecs:
                                        hosts.append(host)
                                        g.user.logger.info(host, "Target HostRecs")
                                    # Delete all IPv4 Address and External Host Records
                                    g.user.logger.info("Updating the Amazon DNS records for a Terminated Instance")
                                    try:
                                        for objtype in ("IP4Address", "IP6Address", "HostRecord"):
                                            stuff = conn.custom_search("EC2InstanceID=%s" %i['InstanceId'], objtype)
                                            for thing in stuff:
                                                g.user.logger.info(thing, "Deleting")
                                                thing.delete()
                                    except Exception as thisexception:
                                        g.user.logger.info(thisexception)
                                    if dynamic_deployment:
                                        for this in hosts:
                                            try:
                                                DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") +" - Dynamically Updating DNS"
                                                g.user.logger.info("Attempting Selective Deploy")
                                                g.user.logger.info(this,"this")
                                                hostidlist = []
                                                hostidlist.append(str(this.get_id()))
                                                g.user.logger.info(hostidlist,"HostID list")
                                                result = conn.selective_deploy(hostidlist)
                                                g.user.logger.info(result,"Selective Deployment Status")
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception, "Exception Selective Deploy")
                                DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Terminated " + str(body['detail']['instance-id']) + " (" + SQS_QUEUE['REGION'] + ")"
                                conn.logout()

                            # Handle stopped EC2 state
                            elif body['detail']['state'] == "stopped":
                                # login to BAM using the API account, do stuff, logout
                                conn = api.API(bam_url)
                                conn.login(form.aws_sync_user.data,form.aws_sync_pass.data)
                                g.user.logger.info('EC2 Instance Stopped - Updating')
                                instanceid = body['detail']['instance-id']
                                instanceid = instanceid.split()
                                instance = ec2_client.describe_instances(InstanceIds=instanceid)
                                DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Stopping " + str(body['detail']['instance-id']) + " (" + SQS_QUEUE['REGION'] + ")"
                                g.user.logger.info(instance)
                                for r in instance['Reservations']:
                                    for i in r['Instances']:
                                        g.user.logger.info(i)
                                        g.user.logger.info(i['InstanceId'], "Instance ID")
                                        nametag = get_instance_name(i['InstanceId'],ec2_resource)
                                        for n in i['NetworkInterfaces']:
                                            g.user.logger.info(n['OwnerId'], "OwnerID")
                                        v6_address = ""
                                        for n2 in i['NetworkInterfaces']:
                                            v6_addresses = n2['Ipv6Addresses']
                                            for v2 in v6_addresses:
                                                v6_address = v2['Ipv6Address']
                                                g.user.logger.info(v6_address, "Instance IPv6 address")
                                        vpc = ec2_resource.Vpc(i['VpcId'])
                                        vpc_name = ""
                                        if vpc.tags:
                                            for tag in vpc.tags:
                                                if tag['Key'] == "Name":
                                                    vpc_name = tag['Value']
                                        if single_config_mode:
                                            config_name = SQS_QUEUE['CONFIGURATION']
                                        else:
                                            if vpc_name:
                                                config_name = SQS_QUEUE['REGION'] + " - " + i['VpcId'] + " - " + vpc_name
                                            else:
                                                config_name = SQS_QUEUE['REGION'] + " - " + i['VpcId']
                                        conf_entity = conn.get_configuration(config_name)
                                        conf = conf_entity.get_id()
                                        try:
                                            dev = conn._api_client.service.getEntityByName(conf, i['InstanceId'], "Device")
                                            g.user.logger.info(dev)
                                        except Exception as thisexception:
                                            g.user.logger.info(thisexception)
                                        if dev.id != 0:
                                            g.user.logger.info(i['InstanceId'], "Device in Address Manager")
                                            try:
                                                g.user.logger.info(i['InstanceId'], "Deleting Device")
                                                conn._api_client.service.delete(dev.id)
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception)
                                        now = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
                                        try:
                                            pubip = i['PublicIpAddress']
                                        except KeyError:
                                            pubip = ""
                                        for block in awspubs:
                                            props = "name=" + SQS_QUEUE['REGION'] + " / Public AWS Block"
                                            try:
                                                publicblocks = conf_entity.get_entity_by_cidr(block)
                                            except PortalException:
                                                publicblocks = None
                                        if publicblocks:
                                            g.user.logger.info("AWS Public Blocks in configuration")
                                        else:
                                            g.user.logger.info("AWS Public Blocks NOT available in configuration")
                                        props = "PrivateDNSName="+i['PrivateDnsName'] + '|' + "PublicDNSName=" + i['PublicDnsName'] + '|' + "InstanceState="+body['detail']['state'] + '|' + "InstanceType="+i['InstanceType'] + "|" + "AvailabilityZone=" + i['Placement']['AvailabilityZone'] + "|" + "|CloudAtlasSyncTime=" + now + "|" + \
                                        "LaunchTime=" + i['LaunchTime'].strftime("%m/%d/%Y %H:%M:%S") + '|' + "Owner=" + n['OwnerId'] + '|' + 'KeyName=' + i['KeyName'] + '|' + 'NAMETAG=' + nametag
                                        if i['PrivateIpAddress'] and pubip and publicblocks:
                                            devips = i['PrivateIpAddress'] + "," + pubip
                                        else:
                                            devips = i['PrivateIpAddress']
                                        if import_amazon_dns:
                                            if dynamic_deployment:
                                                hostrecs = conn.custom_search("EC2InstanceID=%s" %i['InstanceId'], "HostRecord")
                                                hosts = []
                                            for host in hostrecs:
                                                hosts.append(host)
                                                g.user.logger.info(host, "Target HostRecs")
                                            g.user.logger.info(i['InstanceId'], "Deleting the Amazon DNS records Host Records / IPv4 Addresses for a Stopped Instance")
                                            try:
                                                for objtype in ("IP4Address", "IP6Address", "HostRecord"):
                                                    stuff = conn.custom_search("EC2InstanceID=%s" %i['InstanceId'], objtype)
                                                    for thing in stuff:
                                                        g.user.logger.info(thing, "Deleting")
                                                        thing.delete()
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception, "Exception Deleting")
                                            if dynamic_deployment:
                                                for this in hosts:
                                                    try:
                                                        DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") +" - Dynamically Updating DNS"
                                                        g.user.logger.info("Attempting Selective Deploy")
                                                        g.user.logger.info(this,"this")
                                                        hostidlist = []
                                                        hostidlist.append(str(this.get_id()))
                                                        g.user.logger.info(hostidlist,"HostID list")
                                                        result = conn.selective_deploy(hostidlist)
                                                        g.user.logger.info(result,"Selective Deployment Status")
                                                    except Exception as thisexception:
                                                        g.user.logger.info(thisexception, "Exception Selective Deploy")
                                        try:
                                            g.user.logger.info(i['InstanceId'], "Adding stopped EC2 Device")
                                            conn._api_client.service.addDevice(conf, i['InstanceId'], aws_type, aws_type_ec2, devips, v6_address, props)
                                        except Exception as thisexception:
                                            g.user.logger.info(thisexception)
                                        g.user.logger.info("Updating IPs with InstanceID ....")
                                        config_entity = conn.get_configuration(config_name)
                                        if pubip:
                                            try:
                                                ip_address_pub = config_entity.get_ip4_address(i['PublicIpAddress'])
                                                ip_address_pub.set_property("EC2InstanceID", i['InstanceId'])
                                                ip_address_pub.update()
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception, "Exception Getting Public IPv4")
                                        if v6_address:
                                            try:
                                                ip_address_pub6 = config_entity.get_ip6_address(v6_address)
                                                ip_address_pub6.set_property("EC2InstanceID", i['InstanceId'])
                                                ip_address_pub6.update()
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception, "Exception Getting Public IPv6")
                                        try:
                                            ip_address_private = config_entity.get_ip4_address(i['PrivateIpAddress'])
                                            ip_address_private.set_property("EC2InstanceID", i['InstanceId'])
                                            ip_address_private.update()
                                        except Exception as thisexception:
                                            g.user.logger.info(thisexception, "Exception Getting Private IP")
                                DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Stopped " + str(body['detail']['instance-id']) + " (" + SQS_QUEUE['REGION'] + ")"
                                conn.logout()

                            # Handle running EC2 state
                            elif body['detail']['state'] == "running":
                                # login to BAM using the API account, do stuff, logout
                                conn = api.API(bam_url)
                                conn.login(form.aws_sync_user.data,form.aws_sync_pass.data)
                                g.user.logger.info('EC2 Instance Running - Updating')
                                instanceid = body['detail']['instance-id']
                                instanceid = instanceid.split()
                                instance = ec2_client.describe_instances(InstanceIds=instanceid)
                                g.user.logger.info(instance)
                                DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Starting " + str(body['detail']['instance-id']) + " (" + SQS_QUEUE['REGION'] + ")"
                                for r in instance['Reservations']:
                                    for i in r['Instances']:
                                        g.user.logger.info(i)
                                        g.user.logger.info(i['InstanceId'], "Instance ID")
                                        nametag = get_instance_name(i['InstanceId'],ec2_resource)
                                        g.user.logger.info(nametag, "Instance Name Tag")
                                        for n in i['NetworkInterfaces']:
                                            g.user.logger.info(n['OwnerId'], "OwnerID")
                                        v6_address = ""
                                        for n2 in i['NetworkInterfaces']:
                                            v6_addresses = n2['Ipv6Addresses']
                                            for v2 in v6_addresses:
                                                v6_address = v2['Ipv6Address']
                                                g.user.logger.info(v6_address, "Instance IPv6 address")
                                        vpc = ec2_resource.Vpc(i['VpcId'])
                                        vpc_name = ""
                                        if vpc.tags:
                                            for tag in vpc.tags:
                                                if tag['Key'] == "Name":
                                                    vpc_name = tag['Value']
                                        if single_config_mode:
                                            config_name = SQS_QUEUE['CONFIGURATION']
                                        else:
                                            if vpc_name:
                                                config_name = SQS_QUEUE['REGION'] + " - " + i['VpcId'] + " - " + vpc_name
                                            else:
                                                config_name = SQS_QUEUE['REGION'] + " - " + i['VpcId']
                                        conf_entity = conn.get_configuration(config_name)
                                        conf = conf_entity.get_id()
                                        try:
                                            dev = conn._api_client.service.getEntityByName(conf, i['InstanceId'], "Device")
                                            g.user.logger.info(dev)
                                        except Exception as thisexception:
                                            g.user.logger.info(thisexception)
                                        if dev.id != 0:
                                            g.user.logger.info(i['InstanceId'], "Device in Address Manager")
                                            try:
                                                g.user.logger.info(i['InstanceId'], "Deleting Device")
                                                conn._api_client.service.delete(dev.id)
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception)
                                        now = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
                                        try:
                                            pubip = i['PublicIpAddress']
                                            g.user.logger.info("EC2 instance has a public IP")
                                        except KeyError:
                                            g.user.logger.info("EC2 instance DOES NOT have a public IP")
                                            pubip = ""
                                        for block in awspubs:
                                            props = "name=" + SQS_QUEUE['REGION'] + " / Public AWS Block"
                                            try:
                                                publicblocks = conf_entity.get_entity_by_cidr(block)
                                            except PortalException:
                                                publicblocks = None
                                        if publicblocks:
                                            g.user.logger.info("AWS Public Blocks in configuration")
                                        else:
                                            g.user.logger.info("AWS Public Blocks NOT available in configuration")
                                        props = "PrivateDNSName="+i['PrivateDnsName'] + '|' + "PublicDNSName=" + i['PublicDnsName'] + '|' + "InstanceState="+body['detail']['state'] + '|' + "InstanceType="+i['InstanceType'] + "|" + "AvailabilityZone=" + i['Placement']['AvailabilityZone'] + "|"  + "|CloudAtlasSyncTime=" + now + "|" + \
                                        "LaunchTime=" + i['LaunchTime'].strftime("%m/%d/%Y %H:%M:%S") + '|' + "Owner=" + n['OwnerId'] + '|' + 'KeyName=' + i['KeyName'] + '|' + 'NAMETAG=' + nametag
                                        if i['PrivateIpAddress'] and pubip and publicblocks:
                                            devips = i['PrivateIpAddress'] + "," + pubip
                                        else:
                                            devips = i['PrivateIpAddress']
                                        if import_amazon_dns:
                                            g.user.logger.info(i['InstanceId'], "Deleting the Amazon DNS records Host Records / IPv4 Address for a Running Instance")
                                            try:
                                                for objtype in ("IP4Address", "IP6Address", "HostRecord"):
                                                    stuff = conn.custom_search("EC2InstanceID=%s" %i['InstanceId'], objtype)
                                                    for thing in stuff:
                                                        g.user.logger.info(thing, "Deleting")
                                                        thing.delete()
                                                        if dynamic_deployment:
                                                            DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") +" - Dynamically Updating DNS"
                                                            g.user.logger.info("Attempting Selective Deploy")
                                                            g.user.logger.info(thing,"thing")
                                                            g.user.logger.info(thing.get_id(),"ID")
                                                            hostidlist = []
                                                            hostidlist.append(str(thing.get_id()))
                                                            g.user.logger.info(hostidlist,"HostID list")
                                                            result = conn.selective_deploy(hostidlist)
                                                            g.user.logger.info(result,"Selective Deployment Status")

                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception, "Exception Deleting")
                                        try:
                                            g.user.logger.info(i['InstanceId'], "Adding running EC2 Device")
                                            conn._api_client.service.addDevice(conf, i['InstanceId'], aws_type, aws_type_ec2, devips, v6_address, props)
                                        except Exception as thisexception:
                                            g.user.logger.info(thisexception, "Exception Adding Device")

                                        g.user.logger.info("Updating IPs with InstanceID ....")
                                        config_entity = conn.get_configuration(config_name)
                                        if pubip:
                                            try:
                                                ip_address_pub = config_entity.get_ip4_address(i['PublicIpAddress'])
                                                ip_address_pub.set_property("EC2InstanceID", i['InstanceId'])
                                                ip_address_pub.update()
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception, "Exception Getting Public IPv4")
                                        if v6_address:
                                            try:
                                                ip_address_pub6 = config_entity.get_ip6_address(v6_address)
                                                ip_address_pub6.set_property("EC2InstanceID", i['InstanceId'])
                                                ip_address_pub6.update()
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception, "Exception Getting Public IPv6")
                                        try:
                                            ip_address_private = config_entity.get_ip4_address(i['PrivateIpAddress'])
                                            ip_address_private.set_property("EC2InstanceID", i['InstanceId'])
                                            ip_address_private.update()
                                        except Exception as thisexception:
                                            g.user.logger.info(thisexception, "Exception Getting Private IP")
                                        if (import_amazon_dns and i['PublicDnsName'] and publicblocks and pubip):
                                            external_view = config_entity.get_view("Amazon DNS External")
                                            internal_view = config_entity.get_view("Amazon DNS Internal")
                                            if SQS_QUEUE['TARGETZONE']:
                                                try:
                                                    g.user.logger.info(SQS_QUEUE['TARGETZONE'], "Adding HOST for EC2 instance to target zone")
                                                    if is_valid_hostname(nametag):
                                                        public_host_record = external_view.add_host_record(nametag + "." + SQS_QUEUE['TARGETZONE'], [str(i['PublicIpAddress'])])
                                                    else:
                                                        public_host_record = external_view.add_host_record(str(i['InstanceId']) + "." + SQS_QUEUE['TARGETZONE'], [str(i['PublicIpAddress'])])
                                                    public_host_record.set_property("EC2InstanceID", str(i['InstanceId']))
                                                    public_host_record.update()
                                                except Exception as thisexception:
                                                    g.user.logger.info(thisexception)
                                                if dynamic_deployment:
                                                    try:
                                                        hostidlist = []
                                                        hostidlist.append(str(public_host_record.get_id()))
                                                        g.user.logger.info(hostidlist,"HostID list")
                                                        result = conn.selective_deploy(hostidlist)
                                                        g.user.logger.info(result,"Selective Deployment Status")
                                                    except Exception as thisexception:
                                                        g.user.logger.info(thisexception)
                                            try:
                                                g.user.logger.info(SQS_QUEUE['TARGETZONE'], "Adding default HOST for EC2 instance")
                                                public_host_record = external_view.add_host_record(i['PublicDnsName'] , [str(i['PublicIpAddress'])])
                                                public_host_record.set_property("EC2InstanceID", str(i['InstanceId']))
                                                public_host_record.update()
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception)
                                            if dynamic_deployment:
                                                try:
                                                    hostidlist = []
                                                    hostidlist.append(str(public_host_record.get_id()))
                                                    g.user.logger.info(hostidlist,"HostID list")
                                                    result = conn.selective_deploy(hostidlist)
                                                    g.user.logger.info(result,"Selective Deployment Status")
                                                except Exception as thisexception:
                                                    g.user.logger.info(thisexception)
                                        if (import_amazon_dns and i['PrivateDnsName'] and body['detail']['state'] == 'running'):
                                            internal_view = config_entity.get_view("Amazon DNS Internal")
                                            if SQS_QUEUE['TARGETZONE']:
                                                try:
                                                    g.user.logger.info(SQS_QUEUE['REGION'] + "." + SQS_QUEUE['TARGETZONE'], "Adding HOST record for EC2 instance to target zone")
                                                    a_record = internal_view.add_host_record(str(i['PrivateDnsName']).split(".")[0]+ "." + SQS_QUEUE['REGION'] + "." + SQS_QUEUE['TARGETZONE'], [str(i['PrivateIpAddress'])])
                                                    a_record.set_property("EC2InstanceID", str(i['InstanceId']))
                                                    a_record.update()
                                                except Exception as thisexception:
                                                    g.user.logger.info(thisexception)
                                            try:
                                                g.user.logger.info(SQS_QUEUE['REGION'] + "." + SQS_QUEUE['TARGETZONE'], "Adding default HOST record for EC2 instance to default private zone")
                                                a_record = internal_view.add_host_record(str(i['PrivateDnsName']), [str(i['PrivateIpAddress'])])
                                                a_record.set_property("EC2InstanceID", str(i['InstanceId']))
                                                a_record.update()
                                            except Exception as thisexception:
                                                g.user.logger.info(thisexception)
                                DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") +" - Running " + str(body['detail']['instance-id']) + " (" + SQS_QUEUE['REGION'] + ")"
                                conn.logout()
                            sqs.delete_message(QueueUrl=SQS_QUEUE['QUEUE'], ReceiptHandle=message['ReceiptHandle']) # Delete Processed Message from queue
                    else:
                        g.user.logger.info("No updates in queue")


            # Start an APscheduler background job
            now = datetime.utcnow()
            thisjob = SYNCSCHEDULER.add_job(syncjob, trigger='date', run_date=datetime.utcnow(), id=aws_region_name, name=configuration, replace_existing=True)
            g.user.logger.info(thisjob)
            if thisjob not in JOBS:
                JOBS.append(thisjob)

        if form.aws_sync_start.data:
            return render_template('aws_page.html', form=form, text=util.get_text(module_path(), config.language), options=g.user.get_options(), )
        else:
            DISCOVERYSTATUS = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S") + " - Completed Discovery"
            return render_template('aws_page.html', form=form, text=util.get_text(module_path(), config.language), options=g.user.get_options(), )
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template('aws_page.html', form=form, text=util.get_text(module_path(), config.language), options=g.user.get_options(), )

# Function to connect to AWS using roleAssume and MFA Token
def connect_aws(taws_region_name, taws_access_key_id, taws_secret_access_key, trolearn, tsession, tmfaarn, tmfa_token):
    """ Connect to AWS """
    sts = boto3.client('sts', aws_access_key_id=taws_access_key_id, aws_secret_access_key=taws_secret_access_key)
    tempcredentials = sts.get_session_token(DurationSeconds=3600, SerialNumber=tmfaarn, TokenCode=tmfa_token)
    sts = boto3.client('sts', aws_access_key_id=tempcredentials['Credentials']['AccessKeyId'], aws_secret_access_key=tempcredentials['Credentials']['SecretAccessKey'], aws_session_token=tempcredentials['Credentials']['SessionToken'])
    response = sts.assume_role(RoleArn=trolearn, RoleSessionName=str(tsession))
    credentials = response['Credentials']
    taws_access_key_id = credentials['AccessKeyId']
    taws_secret_access_key = credentials['SecretAccessKey']
    taws_session_token = credentials['SessionToken']
    taws_session_expiration = credentials['Expiration']
    return taws_access_key_id, taws_secret_access_key, taws_session_token, taws_region_name, taws_session_expiration

# Function to connect to AWS AQS using service account (i.e no MFA)
def connect_sqs(service_access_key, service_secret_key, aws_region):
    """ SQS connection session """
    mysession = boto3.Session(aws_access_key_id=service_access_key, aws_secret_access_key=service_secret_key, region_name=aws_region)
    sts_client = mysession.client('sts', region_name=aws_region).get_session_token(DurationSeconds=900)
    sqs_resource = mysession.resource('sqs', aws_region)
    ec2_resource = mysession.resource('ec2', aws_region)
    sqs_client = mysession.client('sqs', aws_region)
    ec2_client = mysession.client('ec2', aws_region)
    aws_sqs_queue = sqs_client.get_queue_url(QueueName='Bluecat.fifo')
    aws_sqs_queue = aws_sqs_queue['QueueUrl']
    return sts_client, sqs_client, sqs_resource, aws_sqs_queue, ec2_client, ec2_resource

# Function to get an existing DeviceType or add it
def get_or_create_device_type(parent_id, name, device_type):
    """Gets device type or creates device type if it doesn't exist."""
    result = get_api()._api_client.service.getEntityByName(parent_id, name, device_type)
    if has_response(result):
        device_type_object = get_api().instantiate_entity(result)
    elif parent_id == 0:
        device_type_object = get_api()._api_client.service.addDeviceType(name, '')
        device_type_object = get_api().get_entity_by_id(device_type_object)
    else:
        device_type_object = get_api()._api_client.service.addDeviceSubtype(parent_id, name, '')
        device_type_object = get_api().get_entity_by_id(device_type_object)
    return device_type_object

# Function to add a Device to BAM
def add_device(config_id, name, device_type_id, device_subtype_id, ip4address, ip6address, properties):
    """Add device to BAM."""
    response = get_api()._api_client.service.addDevice(config_id, name, device_type_id, device_subtype_id, ip4address, ip6address, properties)
    return get_api().get_entity_by_id(response)

# Function to get a Device to BAM
def get_device(config_id, device_name):
    """Get device from BAM."""
    device = None
    response = get_api()._api_client.service.getEntityByName(config_id, device_name, "Device")
    if has_response(response):
        device = get_api().instantiate_entity(response)
    return device

# Import AWS public address space
def importawspublic(targetconfiguration):
    """Import Public AWS address space into BAM"""
    global DISCOVERYSTATUS
    DISCOVERYSTATUS = "Discovering AWS Public Blocks for " + aws_region_name
    try:
        conf = get_api().get_configuration(targetconfiguration)
    except PortalException:
        conf = get_api().create_configuration(targetconfiguration)
    conf.set_property('configurationGroup', 'Amazon Web Services')
    conf.update()
    awspublicv4 = awsblocks(aws_region_name)
    awspublicv6 = awsblocks6(aws_region_name)
    for block4 in awspublicv4:
        props = "name=" + aws_region_name + " / Public AWS Block"
        try:
            blk = conf.get_entity_by_cidr(block4)
        except PortalException:
            blk = None
        if blk is None:
            try:
                blk = conf.add_ip4_block_by_cidr(block4, properties=props)
                blk.add_ip4_network(block4, props)
            except:
                pass
        if blk is not None:
            try:
                blk.add_ip4_network(block4, props)
            except:
                pass
    for block6 in awspublicv6:
        props = "name=" + aws_region_name + " / Public AWS Block"
        try:
            parentblock = conf.get_ip6_global_unicast_block()
            parentblock.get_ip6_block_by_prefix(block6)
        except Exception as thisexception:
            if 'No IP6Block found with prefix' in str(thisexception):
                parentblock.add_ip6_block_by_prefix(block6, block_name=aws_region_name + "/ Public AWS Block")

# Download AWS ip-ranges and filter to IPv4 EC2 prefix blocks
def awsblocks(target_region):
    """Get IPv4 block prefixes from AWS"""
    ip_ranges = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json').json()['prefixes']
    ec2_ips = [item['ip_prefix'] for item in ip_ranges if item["service"] == "EC2"]
    region_ips = [item['ip_prefix'] for item in ip_ranges if item["region"] == target_region]
    amazon_ips_ec2 = []
    for ips in ec2_ips:
        if ips in region_ips:
            amazon_ips_ec2.append(ips)
    return amazon_ips_ec2

# Download AWS ip-ranges and filter to IPv6 EC2 prefix blocks
def awsblocks6(target_region):
    """Get IPv6 block prefixes from AWS"""
    ip_ranges = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json').json()['ipv6_prefixes']
    ec2_ips = [item['ipv6_prefix'] for item in ip_ranges if item["service"] == "EC2"]
    region_ips = [item['ipv6_prefix'] for item in ip_ranges if item["region"] == target_region]
    amazon_ips_ec2 = []
    for ips in ec2_ips:
        if ips in region_ips:
            amazon_ips_ec2.append(ips)
    return amazon_ips_ec2

# Import Private VPCs
def discovervpcs():
    """ import private vpcs into """
    form = GenericFormTemplate()
    global DISCOVERYSTATUS
    if assume_role and mfa:
        ec2 = boto3.resource('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
        client = boto3.client('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
    else:
        ec2 = boto3.resource('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        client = boto3.client('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    vpcs = list(ec2.vpcs.filter())
    for vpc in vpcs:
        DISCOVERYSTATUS = "Discovering AWS VPCs"
        vpc_name = ""
        v6_block = ""
        # Get the VPC name if set
        if vpc.tags:
            for tag in vpc.tags:
                if tag['Key'] == "Name":
                    vpc_name = tag['Value']
        if single_config_mode:
            try:
                config_name = get_api().get_configuration(form.configuration.data)
                config_name = config_name.name
            except PortalException:
                config_name = get_api().create_configuration(form.configuration.data)
                config_name = config_name.name
        else:
            if vpc_name:
                config_name = aws_region_name + " - " + vpc.id + " - " + vpc_name
            else:
                config_name = aws_region_name + " - " + vpc.id
        # Get the IPv6 block for the VPC if defined
        if vpc.ipv6_cidr_block_association_set:
            for vdata in vpc.ipv6_cidr_block_association_set:
                v6_block = vdata['Ipv6CidrBlock']
        # If purge is enabed remove the existing conf and add again, tagging to AWS config group (9.1)
        if form.purge_configuration and not single_config_mode:
            DISCOVERYSTATUS = "Purging VPC configuration " + config_name
            try:
                get_api().delete_configuration(config_name)
            except PortalException:
                pass # Conf doesn't exist in BAM
        try:
            conf = get_api().get_configuration(config_name)
        except PortalException:
            conf = get_api().create_configuration(config_name)
        conf.set_property('configurationGroup', 'Amazon Web Services')
        conf.update()

        # Import AWS IPv4 and IPv6 public block - Dynamic Configuration Mode Only - for each VPC config
        if form.aws_public_blocks.data and not single_config_mode:
            DISCOVERYSTATUS = "Discovering AWS Public Blocks"
            importawspublic(config_name)

        # Add IPv4 VPC block to BAM
        if vpc_name:
            props = "name=" + aws_region_name + " / " + vpc.id + " / " + vpc_name
        else:
            props = "name=" + aws_region_name + " / " + vpc.id
        try:
            blk = conf.add_ip4_block_by_cidr(vpc.cidr_block, properties=props)
        except BAMException as thisexception:
            if 'duplicate' not in str(thisexception).lower():
                raise thisexception

        # If there is a IPV6 block in the VPC, convert the VPC IPv6 block to an IPv6 IP address, then get the parent AWS public block using get_ip_range_by_ip
        if v6_block:
            blkv6 = ""
            try:
                ip6 = "/".join(v6_block.split("/")[:-1])
                ip6 = ipaddress.IPv6Address(ip6)
                parentblock = conf.get_ip_range_by_ip('', ip6)
                block_name = props.split('=', 1)[-1]
                blkv6 = parentblock.add_ip6_block_by_prefix(v6_block, block_name=block_name, properties=props)
            except Exception as thisexception:
                ip6 = "/".join(v6_block.split("/")[:-1])
                ip6 = ipaddress.IPv6Address(ip6)
                g.user.logger.info(ip6,"Block")
                blkv6 = conf.get_ip_range_by_ip('',ip6)

        for subnet in vpc.subnets.all():
            response = client.describe_subnets(SubnetIds=[subnet.id,])
            data = response['Subnets']
            for dat in data:
                DISCOVERYSTATUS = "Discovering VPC Subnets"
                availablityzone = dat['AvailabilityZone']
                cidrblock = dat['CidrBlock']
                subnetv6 = dat['Ipv6CidrBlockAssociationSet']
                v6sub = ""
                try:
                    for dic in subnetv6:
                        if 'Ipv6CidrBlock' in dic:
                            v6sub = dic['Ipv6CidrBlock']
                            g.user.logger.info(v6sub,"Sub")
                except AttributeError:
                    pass
                subnetd = ec2.Subnet(subnet.id)
                subnet_name = ""
                if subnetd.tags:
                    for tag in subnetd.tags:
                        if tag['Key'] == "Name":
                            subnet_name = tag['Value']
                if subnet_name:
                    props = "name=" + subnet.id + " - " + availablityzone + ' - ' + subnet_name
                else:
                    props = "name=" + subnet.id + " - " + availablityzone
                blk = conf.get_entity_by_cidr(vpc.cidr_block)
                try:
                    sub = blk.add_ip4_network(cidrblock, props)
                except BAMException as thisexception:
                    sub = blk.get_entity_by_cidr(cidrblock, entity_type='IP4Network')

                # Reserve AWS VPC Fixed address in VPC Subnets
                # See https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html
                try:
                    # First free address is Amazon DNS
                    first = sub.get_first_addresses(1)
                    first2 = ipaddress.IPv4Address(first[0])+2
                    first3 = ipaddress.IPv4Address(first[0])+3
                    amazondns = sub.assign_ip4_address(first2,"", "", "MAKE_RESERVED", properties='')
                    # Next Available address is Amazon DHCP
                    amazondns.set_name("Reserved by AWS DNS")
                    amazondns.update()
                    amazondhcp = sub.assign_ip4_address(first3,"", "", "MAKE_RESERVED", properties='')
                    amazondhcp.set_name("Reserved by AWS Future")
                    amazondhcp.update()
                except BAMException as thisexception:
                    if 'duplicate' not in str(thisexception).lower():
                        raise thisexception

                if v6sub and blkv6:
                    try:
                        block_name = props.split('=', 1)[-1]
                        blkv6.add_ip6_network_by_prefix(v6sub, name=block_name)
                    except Exception as thisexception:
                        pass

# Import ELBv2 devices
def discoverelbv2(aws_type, elbv2_subtype):
    form = GenericFormTemplate()
    global DISCOVERYSTATUS
    DISCOVERYSTATUS = "Discovering ELBv2 LoadBalancers"
    if assume_role and mfa:
        elbclient = boto3.client('elbv2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
        ec2 = boto3.resource('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
    else:
        elbclient = boto3.client('elbv2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        ec2 = boto3.resource('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    lbs = elbclient.describe_load_balancers()
    for x in lbs['LoadBalancers']:
        lbname = x['LoadBalancerName']
        lbdnsname = x['DNSName']
        lbarn = x['LoadBalancerArn']
        lbvpcid = x['VpcId']
        lbtype = x['Type']
        lbstate = str(x['State']['Code'])
        target_list = []
        targetgroups = elbclient.describe_target_groups(LoadBalancerArn=lbarn)
        for y in targetgroups['TargetGroups']:
            targetgroup = y['TargetGroupName']
            z = elbclient.describe_target_health(TargetGroupArn=y['TargetGroupArn'])
            for target in z['TargetHealthDescriptions']:
                try:
                    ip = str(ipaddress.ip_address(target['Target']['Id']))
                    target_list.append(ip)
                except ValueError:
                    target_list.append(target['Target']['Id'])
        target_list = ','.join(target_list)
        target_list = str(target_list)
        vpc = ec2.Vpc(lbvpcid)
        vpc_name = ""
        if vpc.tags:
            for tag in vpc.tags:
                if tag['Key'] == "Name":
                    vpc_name = tag['Value']
        if single_config_mode:
            config_name = get_api().get_configuration(form.configuration.data)
            config_name = config_name.name
        else:
            if vpc_name:
                config_name = aws_region_name + " - " + lbvpcid + " - " + vpc_name
            else:
                config_name = aws_region_name + " - " + lbvpcid
        try:
            config_entity = get_api().get_configuration(config_name)
        except PortalException:
            config_entity = get_api().create_configuration(config_name)
            config_entity.set_property('configurationGroup', 'Amazon Web Services')
            config_entity.update()
        dev = get_device(config_entity.get_id(), lbname)
        if dev is not None:
            get_api()._api_client.service.delete(dev.get_id())
        now = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
        props = ""
        try:
            newdevice = add_device(config_entity.get_id(), lbname, aws_type.get_id(), elbv2_subtype.get_id(), "", "", props)
            newdevice.set_property("CloudAtlasSyncTime", now)
            newdevice.set_property("InstanceType", lbtype)
            newdevice.set_property("PublicDNSName", lbdnsname)
            newdevice.set_property("InstanceState", lbstate)
            newdevice.set_property("Targets", target_list)
            newdevice.set_property("TargetGroup", targetgroup)
            newdevice.update()
        except BAMException as thisexception:
            g.user.logger.info(str(thisexception))

# Import EC2 devices
def discoverec2(aws_type, ec2_subtype):
    form = GenericFormTemplate()
    global DISCOVERYSTATUS
    DISCOVERYSTATUS = "Discovering EC2 Instances"
    if assume_role and mfa:
        ec2 = boto3.resource('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
        client = boto3.client('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
    else:
        ec2 = boto3.resource('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        client = boto3.client('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    for instance in ec2.instances.all():
        if instance.state['Name'] == 'terminated':
            continue
        if instance.subnet_id:
            subnet = ec2.Subnet(instance.subnet_id)
            subnet_name = ""
        if subnet.tags:
            for tag in subnet.tags:
                if tag['Key'] == "Name":
                    subnet_name = tag['Value']
        if instance.vpc_id:
            vpc = ec2.Vpc(instance.vpc_id)
            vpc_name = ""
            if vpc.tags:
                for tag in vpc.tags:
                    if tag['Key'] == "Name":
                        vpc_name = tag['Value']
            # Currently not used in code path, gather DHCP options
            # if vpc.dhcp_options:
            #     dhcp_options = ec2.DhcpOptions(vpc.dhcp_options.id)
        v6_address = ""
        if instance.network_interfaces_attribute:
            for v in instance.network_interfaces_attribute:
                v6_addresses = v['Ipv6Addresses']
                for v2 in v6_addresses:
                    v6_address = v2['Ipv6Address']
        if single_config_mode:
            config_name = get_api().get_configuration(form.configuration.data)
            config_name = config_name.name
        else:
            if vpc_name:
                config_name = aws_region_name + " - " + instance.vpc_id + " - " + vpc_name
            else:
                config_name = aws_region_name + " - " + instance.vpc_id
        try:
            config_entity = get_api().get_configuration(config_name)
        except PortalException:
            config_entity = get_api().create_configuration(config_name)
            config_entity.set_property('configurationGroup', 'Amazon Web Services')
            config_entity.update()
        if import_amazon_dns:
            # Get or Add view "Amazon DNS Internal" to VPC configuration
            try:
                internal_view = config_entity.get_view("Amazon DNS Internal")
            except Exception as thisexception:
                internal_view = config_entity.add_view("Amazon DNS Internal")
            # Get or Add view "Amazon DNS External" to VPC configuration
            try:
                external_view = config_entity.get_view("Amazon DNS External")
            except Exception as thisexception:
                external_view = config_entity.add_view("Amazon DNS External")
        props = "name=" + config_entity.name
        try:
            blk = config_entity.get_entity_by_cidr(vpc.cidr_block)
        except PortalException:
            blk = None
        if blk is None:
            try:
                blk = config_entity.add_ip4_block_by_cidr(vpc.cidr_block, properties=props)
            except:
                pass
        try:
            sub = config_entity.get_entity_by_cidr(subnet.cidr_block)
        except PortalException:
            sub = None
        if sub is None:
            if subnet_name:
                props = "name=" + instance.subnet_id + " - " + subnet_name
            else:
                props = "name=" + instance.subnet_id
            try:
                sub = blk.add_ip4_network(subnet.cidr_block, props)
            except:
                pass
        config_entity = get_api().get_configuration(config_name)
        dev = get_device(config_entity.get_id(), instance.id)
        if dev is not None:
            get_api()._api_client.service.delete(dev.get_id())
        instanceid = instance.id.split()
        instance_detailed = client.describe_instances(InstanceIds=instanceid)
        for r in instance_detailed['Reservations']:
            for i in r['Instances']:
                nametag = ''
                ec2instance = ec2.Instance(instance.id)
                if ec2instance.tags:
                    for tags in ec2instance.tags:
                        if tags["Key"] == 'Name':
                            nametag = tags["Value"]
                for n in i['NetworkInterfaces']:
                    owner = n['OwnerId']
        now = datetime.utcnow().strftime("%m-%d-%Y %H:%M:%S")
        props = ""
        if instance.private_ip_address and instance.public_ip_address and form.aws_public_blocks.data:
            devips = instance.private_ip_address + "," + instance.public_ip_address
        else:
            devips = instance.private_ip_address
        devip6 = ""
        if v6_address and form.aws_public_blocks.data:
            devip6 = v6_address
        try:
            newdevice = add_device(config_entity.get_id(), instance.id, aws_type.get_id(), ec2_subtype.get_id(), devips, devip6, props)
            newdevice.set_property("PrivateDNSName", instance.private_dns_name)
            newdevice.set_property("PublicDNSName", instance.public_dns_name)
            newdevice.set_property("InstanceState", instance.state['Name'])
            newdevice.set_property("InstanceType", instance.instance_type)
            newdevice.set_property("AvailabilityZone", instance.placement['AvailabilityZone'])
            newdevice.set_property("CloudAtlasSyncTime", now)
            newdevice.set_property("LaunchTime", instance.launch_time.strftime("%m/%d/%Y %H:%M:%S"))
            newdevice.set_property("Owner", owner)
            newdevice.set_property("KeyName", instance.key_name)
            newdevice.set_property("NAMETAG", nametag)
            newdevice.update()
        except BAMException as thisexception:
            g.user.logger.info(str(thisexception))
        config_entity = g.user.get_api().get_configuration(config_name)
        if (instance.public_ip_address and form.aws_public_blocks.data):
            try:
                ip_address_pub = config_entity.get_ip4_address(instance.public_ip_address)
                ip_address_pub.set_property("EC2InstanceID", instance.id)
                ip_address_pub.update()
            except Exception as thisexception:
                g.user.logger.info(thisexception, "Exception Getting Public IPv4")

        if (v6_address and form.aws_public_blocks.data):
            try:
                ip_address_pub6 = config_entity.get_ip6_address(v6_address)
                ip_address_pub6.set_property("EC2InstanceID", instance.id)
                ip_address_pub6.update()
            except Exception as thisexception:
                g.user.logger.info(thisexception, "Exception Getting Public IPv6")
        try:
            ip_address_private = config_entity.get_ip4_address(instance.private_ip_address)
            ip_address_private.set_property("EC2InstanceID", instance.id)
            ip_address_private.update()
        except Exception as thisexception:
            g.user.logger.info(thisexception, "Exception Getting Private IP")

        if (import_amazon_dns and instance.public_dns_name and form.aws_public_blocks.data and instance.state['Name'] == 'running'):
            if instance.public_ip_address:
                try:
                    # Add the new target domain to the external view
                    if target_zone:
                        external_view.add_zone(target_zone, deployable=True)
                    # Add the default Amazon DNS zone to the external view
                    external_view.add_zone(instance.public_dns_name.split('.',1)[-1], deployable=True)

                except Exception as thisexception:
                    if "Duplicate" in str(thisexception):
                        pass
                if is_valid_hostname(nametag):
                    try:
                        if target_zone:
                            public_host_record = external_view.add_host_record(nametag + "." + target_zone, [instance.public_ip_address])
                            public_host_record.set_property("EC2InstanceID", instance.id)
                            public_host_record.update()
                        public_host_record = external_view.add_host_record(instance.public_dns_name, [instance.public_ip_address])
                        public_host_record.set_property("EC2InstanceID", instance.id)
                        public_host_record.update()
                    except Exception as thisexception:
                        g.user.logger.info(str(thisexception))
                else:
                    try:
                        if target_zone:
                            public_host_record = external_view.add_host_record(instance.id + "." + target_zone, [instance.public_ip_address])
                            public_host_record.set_property("EC2InstanceID", instance.id)
                            public_host_record.update()
                        public_host_record = external_view.add_host_record(instance.public_dns_name, [instance.public_ip_address])
                        public_host_record.set_property("EC2InstanceID", instance.id)
                        public_host_record.update()
                    except Exception as thisexception:
                        g.user.logger.info(str(thisexception))

        if import_amazon_dns and instance.private_dns_name and instance.state['Name'] == 'running':
                try:
                    if target_zone:
                        internal_view.add_zone(aws_region_name + "." + target_zone, deployable=True)
                    internal_view.add_zone(instance.private_dns_name.split('.',1)[-1], deployable=True)
                except Exception as thisexception:
                    if "Duplicate" in str(thisexception):
                        pass
                try:
                    if target_zone:
                        a_record = internal_view.add_host_record(instance.private_dns_name.split(".")[0]+"." + aws_region_name + "." + target_zone, [instance.private_ip_address])
                        a_record.set_property("EC2InstanceID", instance.id)
                        a_record.update()
                    a_record = internal_view.add_host_record(instance.private_dns_name, [instance.private_ip_address])
                    a_record.set_property("EC2InstanceID", instance.id)
                    a_record.update()
                except Exception as thisexception:
                    g.user.logger.info(str(thisexception))

# Import Route53 zones
def discoverr53():
    """ Discover Route53 public and private hosted zone, import into BAM views """
    form = GenericFormTemplate()
    global DISCOVERYSTATUS
    DISCOVERYSTATUS = "Discovering AWS Route53 DNS"
    if assume_role and mfa:
        rt53client = boto3.client('route53', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
        ec2 = boto3.resource('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)
    else:
        rt53client = boto3.client('route53', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        ec2 = boto3.resource('ec2', region_name=aws_region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    hostedZones = rt53client.list_hosted_zones(MaxItems="100")

    # Single Config Mode
    if single_config_mode:
        try:
            config_entity = get_api().get_configuration(form.configuration.data)
            config_name = config_entity.name
            config_id = config_entity.get_id()
        except PortalException:
            config_entity = get_api().create_configuration(config_name)
            config_entity.set_property('configurationGroup', 'Amazon Web Services')
            config_entity.update()
            config_name = config_entity.name
            config_id = config_entity.get_id()
        try:
            publicviewid = config_entity.get_view('Route53 Public Hosted Zones')
        except PortalException:
            publicviewid = get_api()._api_client.service.addView(config_id, 'Route53 Public Hosted Zones')
            publicviewid = config_entity.get_view('Route53 Public Hosted Zones')
        try:
            privateviewid = config_entity.get_view('Route53 Private Hosted Zones')
        except PortalException:
            privateviewid = get_api()._api_client.service.addView(config_id, 'Route53 Private Hosted Zones')
            privateviewid = config_entity.get_view('Route53 Private Hosted Zones')

        for hostedZone in hostedZones['HostedZones']:
            hzid = str(hostedZone['Id']).strip('/hostedzone/')
            hz = rt53client.get_hosted_zone(Id=hzid)
            if 'VPCs' in hz:
                bczonename = hostedZone['Name'].rstrip('.')
                bczonenamefields = bczonename.split('.')
                bczone = finddomain(bczonenamefields, len(bczonenamefields), privateviewid.get_id())
                bczoneid = bczone['id']
                if bczoneid != 0:
                    privateviewid.get_zone(bczonename)
                else:
                    privateviewid.add_zone(bczonename, deployable=True)
                zonerrsets = rt53client.list_resource_record_sets(HostedZoneId=hostedZone['Id'], MaxItems="100")
                for zonerrset in zonerrsets['ResourceRecordSets']:
                    bczonename = zonerrset['Name'].rstrip('.')
                    bczonenamefields = bczonename.split('.')
                    for rrdata in zonerrset['ResourceRecords']:
                        try:
                            get_api()._api_client.service.addGenericRecord(privateviewid.get_id(), zonerrset['Name'], zonerrset['Type'], rrdata['Value'], zonerrset['TTL'], "")
                        except:
                            # Just pass on exception, needs correct handling for other record types
                            pass
            elif 'DelegationSet' in hz:
                bczonename = hostedZone['Name'].rstrip('.')
                bczonenamefields = bczonename.split('.')
                bczone = finddomain(bczonenamefields, len(bczonenamefields), publicviewid.get_id())
                bczoneid = bczone['id']
                if bczoneid != 0:
                    publicviewid.get_zone(bczonename)
                else:
                    publicviewid.add_zone(bczonename, deployable=True)
                zonerrsets = rt53client.list_resource_record_sets(HostedZoneId=hostedZone['Id'], MaxItems="100")
                for zonerrset in zonerrsets['ResourceRecordSets']:
                    bczonename = zonerrset['Name'].rstrip('.')
                    bczonenamefields = bczonename.split('.')
                    for rrdata in zonerrset['ResourceRecords']:
                        try:
                            get_api()._api_client.service.addGenericRecord(publicviewid.get_id(), zonerrset['Name'], zonerrset['Type'], rrdata['Value'], zonerrset['TTL'], "")
                        except:
                            # Just pass on exception, needs correct handling for other record types
                            pass
    # Dynamic VPC config mode import
    else:
        for hostedZone in hostedZones['HostedZones']:
            hzid = str(hostedZone['Id']).strip('/hostedzone/')
            hz = rt53client.get_hosted_zone(Id=hzid)
            if 'VPCs' in hz:
                for vpc in hz['VPCs']:
                    vpcd = ec2.Vpc(vpc['VPCId'])
                    vpc_name = ""
                    if vpcd.tags:
                        for tag in vpcd.tags:
                            if tag['Key'] == "Name":
                                vpc_name = tag['Value']
                                if vpc_name:
                                    hzvpcconf = str(vpc['VPCId']) + " - " + vpc_name
                                else:
                                    hzvpcconf = str(vpc['VPCId'])
                    try:
                        config_entity = get_api().get_configuration(hzvpcconf)
                        config_name = config_entity.name
                        config_id = config_entity.get_id()
                    except PortalException:
                        config_entity = get_api().create_configuration(hzvpcconf)
                        config_entity.set_property('configurationGroup', 'Amazon Web Services')
                        config_entity.update()
                        config_name = config_entity.name
                        config_id = config_entity.get_id()
                    try:
                        privateviewid = config_entity.get_view('Route53 Private Hosted Zones')
                    except PortalException:
                        privateviewid = get_api()._api_client.service.addView(config_id, 'Route53 Private Hosted Zones')
                        privateviewid = config_entity.get_view('Route53 Private Hosted Zones')
                    bczonename = hostedZone['Name'].rstrip('.')
                    bczonenamefields = bczonename.split('.')
                    bczone = finddomain(bczonenamefields, len(bczonenamefields), privateviewid.get_id())
                    bczoneid = bczone['id']
                    if bczoneid != 0:
                        privateviewid.get_zone(bczonename)
                    else:
                        privateviewid.add_zone(bczonename, deployable=True)
                    zonerrsets = rt53client.list_resource_record_sets(HostedZoneId=hostedZone['Id'], MaxItems="100")
                    for zonerrset in zonerrsets['ResourceRecordSets']:
                        bczonename = zonerrset['Name'].rstrip('.')
                        bczonenamefields = bczonename.split('.')
                        for rrdata in zonerrset['ResourceRecords']:
                            try:
                                get_api()._api_client.service.addGenericRecord(privateviewid.get_id(), zonerrset['Name'], zonerrset['Type'], rrdata['Value'], zonerrset['TTL'], "")
                            except:
                                # Just pass on exception, needs correct handling for other record types
                                pass
            elif 'DelegationSet' in hz:
                try:
                    config_entity = get_api().get_configuration("Route53 Public Hosted Zones")
                    config_name = config_entity.name
                    config_id = config_entity.get_id()
                except PortalException:
                    config_entity = get_api().create_configuration("Route53 Public Hosted Zones")
                    config_entity.set_property('configurationGroup', 'Amazon Web Services')
                    config_entity.update()
                    config_name = config_entity.name
                    config_id = config_entity.get_id()
                try:
                    publicviewid = config_entity.get_view('Route53 Public Hosted Zones')
                except PortalException:
                    publicviewid = get_api()._api_client.service.addView(config_id, 'Route53 Public Hosted Zones')
                    publicviewid = config_entity.get_view('Route53 Public Hosted Zones')
                bczonename = hostedZone['Name'].rstrip('.')
                bczonenamefields = bczonename.split('.')
                bczone = finddomain(bczonenamefields, len(bczonenamefields), publicviewid.get_id())
                bczoneid = bczone['id']
                if bczoneid != 0:
                    publicviewid.get_zone(bczonename)
                else:
                    publicviewid.add_zone(bczonename, deployable=True)
                zonerrsets = rt53client.list_resource_record_sets(HostedZoneId=hostedZone['Id'], MaxItems="100")
                for zonerrset in zonerrsets['ResourceRecordSets']:
                    bczonename = zonerrset['Name'].rstrip('.')
                    bczonenamefields = bczonename.split('.')
                    for rrdata in zonerrset['ResourceRecords']:
                        try:
                            get_api()._api_client.service.addGenericRecord(publicviewid.get_id(), zonerrset['Name'], zonerrset['Type'], rrdata['Value'], zonerrset['TTL'], "")
                        except:
                            # Just pass on exception, needs correct handling for other record types
                            pass




# Given an EC2 instanceID provide the name tag
def get_instance_name(instanceid,ec2r):
    """get the EC2 instance tag"""
    ec2instance = ec2r.Instance(instanceid)
    instancename = ''
    if ec2instance.tags:
        for tag in ec2instance.tags:
            if tag["Key"] == 'Name':
                instancename = tag["Value"]
    return instancename

# Function to find a domain
def finddomain(domainnamefields, i, parentid):
    """find a domain"""
    i -= 1
    name = domainnamefields[i]
    domain = get_api()._api_client.service.getEntityByName(parentid, name, 'Zone')
    domainid = domain['id']
    if i > 0:
        domain = finddomain(domainnamefields, i, domainid)
    return domain

def get_resource_text():
    """return resource text"""
    return util.get_text(module_path(), config.language)

# Check if hostname tag is a valid hostname
def is_valid_hostname(hostname):
    """Check for valid hostname label"""
    if len(hostname) > 255:
        return False
    try:
        if hostname[-1] == ".":
            hostname = hostname[:-1] # strip exactly one dot from the right, if present
    except IndexError:
        pass
    allowed = re.compile(r"^(?!-)[a-zA-Z0-9--_]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))

def autologin_func():
    """
    Autologin func used by the Continuous Visibility sync calls
    """
    username = form.aws_sync_user.data
    password = form.aws_sync_pass.data
    return username, password

# Function to get the required UDFs or Create them if missing
def check_and_create_aws_udfs():
    """Created required UDFs for AWS if they don't exist already"""
    udf_attributes = {
        'type': 'TEXT',
        'defaultValue': '',
        'validatorProperties': '',
        'required': False,
        'hideFromSearch': False,
        'renderAsRadioButton': False,
    }
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='AvailabilityZone', displayName='Availability Zone'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='InstanceState', displayName='Instance State'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='InstanceType', displayName='Instance Type'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='PrivateDNSName', displayName='Private DNS Name'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='PublicDNSName', displayName='Public DNS Name'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='CloudAtlasSyncTime', displayName='CloudAtlas Sync Time'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='LaunchTime', displayName='Launch Time'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='LaunchTime', displayName='Launch Time'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='Owner', displayName='Owner'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='NAMETAG', displayName='Name Tag'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='KeyName', displayName='AWS SSH Key'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='TargetGroup', displayName='Target Group'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('Device', dict(udf_attributes, name='Targets', displayName='Targets'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('IP4Address', dict(udf_attributes, name='EC2InstanceID', displayName='AWS EC2 Instance ID'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('IP6Address', dict(udf_attributes, name='EC2InstanceID', displayName='AWS EC2 Instance ID'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
    try:
        get_api()._api_client.service.addUserDefinedField('ResourceRecord', dict(udf_attributes, name='EC2InstanceID', displayName='AWS EC2 Instance ID'),)
    except RESTFault as thisexception:
        if 'duplicate' not in str(thisexception).lower():
            raise thisexception
