function validateMacAddress(input) {
  const macAddressForm1 = '00:00:00:00:00:00';
  const predictedMacAddress1 = input + macAddressForm1.slice(input.length, );
  const macAddressForm2 = '00-00-00-00-00-00';
  const predictedMacAddress2 = input + macAddressForm2.slice(input.length, );
  const regex1 = /^[a-fA-F0-9]{2}(:[a-fA-F0-9]{2}){5}$/; 
  const regex2 = /^[a-fA-F0-9]{2}(-[a-fA-F0-9]{2}){5}$/;

  return regex1.test(predictedMacAddress1) || regex2.test(predictedMacAddress2)
}

// Handle the case: 1a:2:3:4:5:6
function mac_convert_01(input) {
  li = input.split(':');
  result = [];
  if (li.length === 6) {
    for (let i = 0; i < 6; i++) {
      if (li[i].length === 1 && Number.isInteger(Number(li[i]))) {
        result.push('0' + li[i])
      }
      else {
        result.push(li[i])
      }
    }
    return result.join(':')
  }
  else {
    return input
  }
}

// Handle the case: 1A2B3C4d5e6f
function mac_convert_02(input) {
  if (input.length === 12 && !input.includes('.') && !input.includes(':') && !input.includes('-')) {
    let result = '';
    for (let i = 0; i < 12; i++) {
      if (i % 2 === 1 && i < 11) result = result + input[i] + ':';
      else {
        result = result + input[i]
      }
    }
    return result
  }
  return input
}

// Handle the case: 1A2B.3C4d.1234
function mac_convert_03(input) {
  if (input.length === 14 && input.split('.').length === 3) {
     return mac_convert_02(input.split('.').join(''))   
  }
  return input
}

function validate(input) {
  let final_mac;
  if (input.length >= 11 && input.length < 17) {
    final_mac = mac_convert_01(input);
    final_mac = mac_convert_02(final_mac);
    final_mac = mac_convert_03(final_mac);
  }
  else {
    final_mac = input;
  }
  
  const regex1 = /^[a-fA-F0-9]{2}(:[a-fA-F0-9]{2}){5}$/; 
  const regex2 = /^[a-fA-F0-9]{2}(-[a-fA-F0-9]{2}){5}$/;
  // convert input
  return regex1.test(final_mac) || regex2.test(final_mac)
}

function validateName(input) {
  if (input === '') return false;
  const notAllowedList = ['^', '`', '!', '$', '&', '(', ')', '|', ';', '<', '>', '"', "'", '\\', ' '];
  for (let c of notAllowedList) {
    if (input.includes(c)) return false;
  }
  return true;
}

function convert_format(input) {
  let final_mac;
  if (input.length >= 11 && input.length < 17) {
    final_mac = mac_convert_01(input);
    final_mac = mac_convert_02(final_mac);
    final_mac = mac_convert_03(final_mac);
  }
  else {
    final_mac = input;
  }
  return final_mac.split('-').join(':').toUpperCase()
}

function getLocations(data) {
  return data.map(x => {
    const location_code = Object.keys(x)[0];
    const location_name = x[location_code].Location_name;
    return location_name + ' (' + location_code + ')'
  })
}

function getLocationCode(location) {
  const li = location.split("(");
  const result = li[li.length - 1].slice(0, -1);
  return result
}

// Get location code list from locations list
function getLocationCodes(locations) {
  return locations.map(x => getLocationCode(x))
}

  
function getIpNetworks(data, location) {
    try {
      return data.filter(x => Object.keys(x)[0] === location)[0][location]["IP4Network"].map(y => y["detail"]["CIDR"])
    }
    catch {
      return []
    }
    
}
  
function getDnsDomains(data, location) {
    return data.filter(x => Object.keys(x)[0] === location)[0][location]["DNS_domain"]
    
}
  
function getIpAddress(data, location, IpNetwork) {
    return data.filter(x => Object.keys(x)[0] === location)[0][location]["IP4Network"].filter(y => y["detail"]["CIDR"] === IpNetwork)[0]["next_ip"]
    
}

function getIpNetworkDetail(data, location, IpNetwork) {
    // Handle case: device_network = []
  if (data.length === 0) {
    return [
        {title: 'Name', content: ''},
        {title: 'vlan id', content: ''}
    ]
  }

  let detailData = data;
  if (Array.isArray(data)) {
    detailData = data.filter(x => Object.keys(x)[0] === location)[0][location]["IP4Network"].filter(y => y["detail"]["CIDR"] === IpNetwork)[0];
  }
  const result = [
    {title: 'Name', content: detailData.name ? detailData.name : ""},
    {title: 'vlan id', content: detailData.detail ? detailData.detail["ip4ar-vlan-id"]: ""}
  ]
  return result
}

function getValue(input) {
    return input ? input : ''
}