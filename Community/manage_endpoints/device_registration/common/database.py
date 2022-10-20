import json, ipaddress

from flask import g

from .constant import Device, DeviceProperties, NetworkItem


class DeviceDatabase():
    def __init__(self, bam_db):
        self.bam_db = bam_db

    def get_device(self, config, tag, location, network=None, dns_domain=None, account_id=None):
        sql = """
SELECT id as mac_id,name as mac_name,mac_address,"mac-account-id","mac-description","mac-audit-trail",unnest(string_to_array("mac-location", ',')) as "mac-location",ip_id,network_id,network_name,start_ip,end_ip,ipaddr_id,ip_address,result_temp.host_id,host_list.host_name,host_list.fqdn 
FROM (	SELECT * 
		FROM (	SELECT 	mac_list_filtered.id, 
			  			mac_list_filtered.name ,
			  			mac_list_filtered.address as mac_address,
			  			mac_list_filtered.ip_id,
						"mac-account-id",
						"mac-description",
						"mac-audit-trail",  
						"mac-location"
				FROM(	SELECT 	mac_list_filtered.id, mac_list_filtered.name, mac_list_filtered.address, ip_id,
					 			"mac-account-id",
								"mac-description",
								"mac-audit-trail",  
								"mac-location" 
					 	FROM (	SELECT 	mac_list.id, mac_list.name, mac_list.address, mac_list.ip_ids,
										MAX(CASE WHEN UDF.name = 'mac-account-id' THEN UDF.text END) as "mac-account-id",
										MAX(CASE WHEN UDF.name = 'mac-description' THEN UDF.text END) as "mac-description",
										MAX(CASE WHEN UDF.name = 'mac-audit-trail' THEN UDF.text END) as "mac-audit-trail",  
										MAX(CASE WHEN UDF.name = 'mac-location' THEN UDF.text END) as "mac-location"
								FROM (	SELECT 	id,
											  	name,
												long2mac(entity_maca.long1) AS address,
												array_to_string(ARRAY( 	SELECT entity_link.owner_id
																		FROM entity_link
																		WHERE entity_link.link_type::text = 'MACA_IP'::text 
																		AND entity_link.entity_id = entity_maca.id), ','::text) AS ip_ids
										FROM entity_maca
										WHERE entity_maca.id 
										IN (	SELECT owner_id 
												FROM entity_link
												WHERE entity_link.entity_id = %s
										)
									  	AND entity_maca.parent_id = %s
								) as mac_list
								JOIN (	SELECT metadata_value.owner_id, metadata_value.text, metadata_field.name 
										FROM metadata_value
										JOIN metadata_field
										ON metadata_value.field_id = metadata_field.id
										ORDER BY metadata_value.owner_id) as UDF
								ON mac_list.id = UDF.owner_id
								GROUP BY mac_list.id, mac_list.name, mac_list.address,ip_ids) as mac_list_filtered
						LEFT JOIN LATERAL unnest(string_to_array (mac_list_filtered.ip_ids, ',')) as ip_id ON true ) as mac_list_filtered
			 ) as mac
		LEFT JOIN (	SELECT 	ip_temp_list.ipaddr_id,
			  				ip_temp_list.ip_address,
			  				ip_temp_list.host_id,
			  				ip_temp_list.network_id,
			  				entity_trunk.name as network_name,
			  				long2ip4(entity_trunk.long1) as start_ip,
			  				long2ip4(entity_trunk.long2) as end_ip
					FROM(	SELECT 	ipaddr.id AS ipaddr_id,
					 				long2ip4(ipaddr.long1) as ip_address,
					 				host.id AS host_id,
					 				net.id as network_id
							FROM ip4_and_6_addrs ipaddr
							JOIN entity_trunk net 
						 	ON net.id = ipaddr.parent_id AND ipaddr.discriminator::text = 'IP4A'::text
							LEFT JOIN (	entity_link hostiplink
										JOIN entity_rrs host 
									   	ON hostiplink.owner_id = host.id 
									   	AND host.discriminator::text = 'HOST'::text 
									   	AND hostiplink.link_type::text = 'IP'::text) 
							ON hostiplink.entity_id = ipaddr.id
						) as ip_temp_list
				JOIN entity_trunk
				ON ip_temp_list.network_id = entity_trunk.id) as ip_list
		ON mac.ip_id::bigint = ip_list.ipaddr_id) 
	as result_temp
LEFT JOIN (	SELECT resource_record.id as host_id, resource_record.name as host_name, zone_fqn.fully_qualified_name as FQDN 
			FROM(	SELECT id, name, parent_id as zone_id
			 		FROM entity_rrs
			 		WHERE discriminator = 'HOST'
				) as resource_record
		JOIN zone_fqn
		ON resource_record.zone_id =  zone_fqn.id) as host_list
ON result_temp.host_id = host_list.host_id


																			
        """
        device_list = []
        g.user.logger.debug("Query devices from tag {}, within configuration {}".format(tag, config))
        try:
            query = self.bam_db.query(sql, (tag, config,))
            for device in query:
                device_network = ""
                if device[10] and device[11]:
                    device_network = list(ipaddress.summarize_address_range(
                                    ipaddress.IPv4Address(device[10]), ipaddress.IPv4Address(device[11])))[0].exploded
                if not account_id or str(account_id) in str(device[3]):
                    if not dns_domain or dns_domain == device[16]:
                        if not network or network == device_network:
                            if location == device[6]:
                                temp = {Device.Ip_info: ""}
                                device_list.append(
                                    {
                                        Device.Device_id: device[0],
                                        Device.Mac_address: device[2].replace('-', ':').upper(),
                                        Device.Name: device[1],
                                        Device.Group: tag,
                                        DeviceProperties.Location: device[6],
                                        Device.Network: {
                                            NetworkItem.DETAIL: {"CDIR": device_network}
                                                         },
                                        Device.Domain: {
                                            Device.Domain_name: device[16],
                                            Device.Host_record_name: str(device[15]) + '.' + str(device[16]) if device[15] else device[16]
                                        },
                                        DeviceProperties.Description: device[4],
                                        DeviceProperties.Audit: json.loads(device[5].replace("'",
                                        '"')) if device[5] else [{}],
                                        DeviceProperties.Account_id: device[3],
                                    }
                                )
                                if device[13]:
                                    temp = {
                                        Device.Ip_info:
                                            {
                                                Device.Ip_address: device[13]
                                            }
                                    }
                                if device_list[-1]:
                                    device_list[-1].update(temp)
        except Exception as e:
            g.user.logger.error("Query Device from BAM database failed! {}".format(str(e)))
        return device_list
