// Global data
let device_groups = [];
let optionData = {}; // based on device group
let group_access_right = {}
let config_name;

let isMultipleIp;


$(document).ready(function() {
    // Go to add or update page
    const isEdit = location.search.includes('?edit=true');
    const hasData = location.search.includes('mac=');

    if(!hasData) reloadField();
    if (isEdit) {
        $(".edit-mode").css('display', 'flex');
        $(".add-mode").css('display', 'none');

        $("#mac-address").addClass("blockEdit");
        $(".glyphicon-mac").addClass("hideIcon");

        // Change title of page
        $("#title").text('Update Device');
        $('#addDevice-text').css('display', 'none');
    }
    else {
        $(".edit-mode").css('display', 'none');
        $(".add-mode").css('display', 'block');
        $('#addDevice-text').css('display', 'block');
    }

    // Get config name
    $.ajax({
        url: '/api/v1/configuration_name/',
        method: "GET",
        dataType: 'json',
        contentType: "application/json",
        success: function(result) {
            config_name = result;

            // Call api to get device groups (just call at the first time)
            $("#spinning-wheel").css("display", "block");
            $.ajax({
                url: '/api/v1/tags/',
                method: "GET",
                dataType: 'json',
                contentType: "application/json",
                success: function(data) {
                    device_groups = data.map(x => Object.keys(x)[0]);
                    for (let x of data) {
                        group_access_right = {...group_access_right, ...x}
                    }

                    // Create options for group device
                    for (let i=0; i < device_groups.length; i++) {
                        $('#device-group').append(`<option value=${i}>${device_groups[i]}</option>`);
                    }

                    // Update or after delete mode
                    if (!hasData) {
                        const default_group_device = device_groups[0];
                        // Call api to get data (locations, dns domains, ip networks, ...) from device group (1st option)
                        $.ajax({
                            url: `/api/v1/tags/${default_group_device}/locations/`,
                            method: "GET",
                            dataType: 'json',
                            contentType: "application/json",
                            success: function(data) {
                                $("#spinning-wheel").css("display", "none");
                                optionData = data;

                                const locations = getLocations(optionData);
                                for (let i=0; i < locations.length; i++) {
                                    $('#location').append(`<option value=${i}>${locations[i]}</option>`);
                                }

                                const dnsDomains = getDnsDomains(optionData, getLocationCode(locations[0]));
                                for (let i=0; i < dnsDomains.length; i++) {
                                    $('#dns-domain').append(`<option value=${i}>${dnsDomains[i]}</option>`);
                                }

                                const ipNetworks = getIpNetworks(optionData, getLocationCode(locations[0]));
                                for (let i=0; i < ipNetworks.length; i++) {
                                    $('#ip-network').append(`<option value=${i}>${ipNetworks[i]}</option>`);
                                }

                                const ipAddress = getIpAddress(optionData, getLocationCode(locations[0]), ipNetworks[0]);
                                const detail = getIpNetworkDetail(optionData, getLocationCode(locations[0]), ipNetworks[0]);
                                $("#ip-address").val(ipAddress);
                                const htmlContent = networkDetailTemplate(detail);
                                $(".textContent").html(htmlContent);
                            },
                            error: function(error) {
                                $("#spinning-wheel").css("display", "none");
                                showErrorNotification(error['responseJSON'].includes('Please provide admin credential') ? error['responseJSON'] : 'Server error occurred. Check logs for more details.');
                            }
                        });
                    }
                    else {
                        $( "#mac-address" ).addClass('valid');
                        const afterDelete = sessionStorage.getItem('isDelete');
                        const mac_address = location.search.split("&").slice(-2)[0].split("=").slice(-1)[0];
                        const ip_address = location.search.split("&").slice(-2)[1].split("=").slice(-1)[0];
                        if (afterDelete) {
                            enableAdd();
                        }
                        getCurrentData(mac_address, ip_address, isEdit, afterDelete);
                    }

                },
                error: function(error) {
                    $("#spinning-wheel").css("display", "none");
                    showErrorNotification();
                }
            });
        },
        error: function(error) {
            var el = document.querySelector(".notification");
            el.style.display = 'block';
            el.classList.add('notification--fail');
            el.innerText = "Not defined configuration.";
        }
    });
    
});

function setCurrentData(data, isEdit, afterDelete) {
    $("#mac-address").val(data.mac_address);
    $("#name").val(data.name);
    checkNameField();
    $("#account-id").val(data["mac-account-id"]);
    $("#description").val(!!data["mac-description"] ? data["mac-description"] : "");

    if (!isEdit) {
        $("#ip-network").removeClass('disabled');
        $("#dns-domain").removeClass('disabled');
    }
    device_group_value = device_groups.indexOf(data.device_group);
    $("#device-group").val(device_group_value.toString());

    const ip_network = data.device_network.detail ? data.device_network.detail['CIDR'] : ''
    if (isEdit) {
        $('#location').empty();
        $('#location').append(`<option value={0}>${getValue(data["mac-location"])}</option>`);
        $('#ip-network').empty();
        $('#ip-network').append(`<option value={0}>${getValue(ip_network)}</option>`);
        $('#dns-domain').empty();
        $('#dns-domain').append(`<option value={0}>${getValue(data.dns_domain.domain)}</option>`);
        const detail = getIpNetworkDetail(data.device_network, data["mac-location"], ip_network);
        const htmlContent = networkDetailTemplate(detail);
        $(".textContent").html(htmlContent);
        $("#ip-address").val(data.ip_info.ip_address);

        // Handle case: There is no device group
        if(Array.isArray(data.device_group) || !device_groups.includes(data.device_group)) {

            $("#name").addClass('disabled');
            $("#description").addClass('disabled');
            $("#account-id").addClass('disabled');
            $('.dp-update').css('display', 'none');
            $('.dp-clearUpdate').css('display', 'none');
            $('.dp-delete').css('display', 'none');
            $('.dp-unassign').css('display', 'none');
            $('#title').text('View Device');
            $('#addDevice-text').css('display', 'block');
            $('#addDevice-text').text('Can not update device without Tag Device Group');

            $( "#name" ).removeClass('invalid');
            $( "#name" ).removeClass('valid');

        }

        if (sessionStorage.getItem('isUnassign')) {
            var el = document.querySelector(".notification");
            el.style.display = 'block';
            el.classList.add('notification--success');
            el.innerHTML = `<span>Unassigned the IP Address <span style="font-weight: 800">${sessionStorage.getItem('unassignIp')}</span></span>`;
            sessionStorage.removeItem('unassignIp');
            sessionStorage.removeItem('isUnassign');
        }

        return
    }

    // Call api to get data options from device group
    $.ajax({
        url: `/api/v1/tags/${data.device_group}/locations/`,
        method: "GET",
        dataType: 'json',
        contentType: "application/json",
        success: function(resultData) {
            $("#spinning-wheel").css("display", "none");
            if (afterDelete) {
                var el = document.querySelector(".notification");
                el.style.display = 'block';
                el.classList.add('notification--success');
                el.innerHTML = `<span>Deleted device with MAC address <span style="font-weight: 800">${data.mac_address}</span></span>`;
                sessionStorage.removeItem('isDelete');
            }
            optionData = resultData;

            const locations = getLocations(optionData);
            $('#location').empty();
            for (let i=0; i < locations.length; i++) {
                $('#location').append(`<option value=${i}>${locations[i]}</option>`);
            }
            
            if (data["mac-location"] !== "") {
                location_value = getLocationCodes(locations).indexOf(data["mac-location"]);
                $("#location").val(location_value);

                $('#ip-network').empty();
                const ipNetworks = getIpNetworks(optionData, data["mac-location"]);
                for (let i=0; i < ipNetworks.length; i++) {
                    $('#ip-network').append(`<option value=${i}>${ipNetworks[i]}</option>`);
                }   

                const ip_network = data.device_network.detail ? data.device_network.detail['CIDR'] : '';
                if (ip_network !== '') {
                    ip_network_value = ipNetworks.indexOf(ip_network);

                    if (ip_network_value !== -1) {
                        $("#ip-network").val(ip_network_value);

                        // Fill detail and IP address 
                        const ipAddress = getIpAddress(optionData, data["mac-location"], ip_network);
                        const detail = getIpNetworkDetail(optionData, data["mac-location"], ip_network);

                        if (isEdit) {
                            $("#ip-address").val(data.ip_info.ip_address);
                        }
                        else {
                            $("#ip-address").val(ipAddress);
                        }
                        
                        const htmlContent = networkDetailTemplate(detail);
                        $(".textContent").html(htmlContent);
                    }
                    else {
                        $("#ip-address").val('');
                        $(".textContent").html('');
                    }

                    const dnsDomains = getDnsDomains(optionData, data["mac-location"]);
                    $('#dns-domain').empty();
                    for (let i=0; i < dnsDomains.length; i++) {
                        $('#dns-domain').append(`<option value=${i}>${dnsDomains[i]}</option>`);
                    }   

                    if (Object.keys(data.dns_domain).length > 0) {
                        if (data.dns_domain.domain !== '') {
                            dns_domain_value = dnsDomains.indexOf(data.dns_domain.domain);
                            if (dns_domain_value !== -1) {
                                $("#dns-domain").val(dns_domain_value);
                            }
                        }
                    }
                }
                else {
                    // Handle the case: deleted device has no IP Address
                    const dnsDomains = getDnsDomains(optionData, data["mac-location"]);
                    $('#dns-domain').empty();
                    for (let i=0; i < dnsDomains.length; i++) {
                        $('#dns-domain').append(`<option value=${i}>${dnsDomains[i]}</option>`);
                    }  

                    const ipNetworks = getIpNetworks(optionData, data["mac-location"]);
                    const ipAddress = getIpAddress(optionData, data["mac-location"], ipNetworks[0]);
                    const detail = getIpNetworkDetail(optionData, data["mac-location"], ipNetworks[0]);
                    $("#ip-address").val(ipAddress);
                    const htmlContent = networkDetailTemplate(detail);
                    $(".textContent").html(htmlContent);
                }
            }

            switchAddButton();
        },
        error: function(error) {
            $("#spinning-wheel").css("display", "none");
            showErrorNotification(error['responseJSON'].includes('Please provide admin credential') ? error['responseJSON'] : 'Server error occurred. Check logs for more details.');
        }
    });
}

function getCurrentData(mac_address, ip_address, isEdit, afterDelete) {

    $("#name").removeClass('disabled');
    $("#account-id").removeClass('disabled');
    $("#description").removeClass('disabled');


    if (isEdit) {
        let searchUrl = `/api/v1/configurations/${config_name}/mac_addresses/${mac_address}`;
        if (ip_address) searchUrl = `/api/v1/configurations/${config_name}/search_mac_address_by_ip_address?ip_address=${ip_address}`;
        
          // Call api to get device data of the mac address
        $.ajax({
            url: searchUrl,
            method: "GET",
            dataType: 'json',
            contentType: "application/json",
            success: function(result) {
                $("#spinning-wheel").css("display", "none");

                const data = result.data.filter(x => x.mac_address === mac_address)[0];
                sessionStorage.setItem('current-device', JSON.stringify(data));

                // enable or disable unasign/delete button
                if (data.is_multiple_ip) {
                    $(".dp-unassign" ).removeClass('blocked');
                    $(".dp-delete" ).addClass('blocked');
                    $('#multiple-ip-mess').css('display', 'block');
                    isMultipleIp = true;
                }
                else {
                    $(".dp-delete" ).removeClass('blocked');
                    $(".dp-unassign" ).addClass('blocked');
                    $('#multiple-ip-mess').css('display', 'none');
                    isMultipleIp = false;
                }
                
                setCurrentData(data, isEdit);

                $("#device-group").addClass('disabled');
                $("#location").addClass('disabled');
                $("#ip-network").addClass('disabled');
                $("#dns-domain").addClass('disabled');
        
                // add audit table
                var html = auditTableTemplate(data['mac-audit-trail']);
                $("#auditTable tbody").html(html);
                
            },
            error: function(error) {
                $("#spinning-wheel").css("display", "none");
                showErrorNotification();
            }
        });

    }
    else {
        const data = JSON.parse(sessionStorage.getItem('current-device'));
        setCurrentData(data, isEdit, afterDelete);
    }

}

function reloadField() {
    $("#mac-address").val("");
    $("#name").val("");
    $("#description").val("");
    $("#account-id").val("");
}

function cleanUpData() {
    $("#mac-address").val("");
    $("#name").val("");
    checkNameField();
    $("#description").val("");
    $("#account-id").val("");
    $('#location option:first').prop('selected', true);
    $("#ip-network").val("");
    $("#dns-domain").val("");
    $(".textContent").html("");
    $("#ip-address").val("");
}

function notChanged() {
    const name = $("#name").val();
    const account_id = $("#account-id").val();
    const description = $("#description").val();

    const data = JSON.parse(sessionStorage.getItem('current-device'));
    if (data === undefined) {
        return true
    }

    return (name === data.name && account_id === data['mac-account-id'] && description === (data['mac-description'] === null ? "": data['mac-description'])) || name === '' || account_id === '' || !validateName(name)

}

function enableAddCondition() {
    const mac_address = $("#mac-address").val();
    const name = $("#name").val();
    if (!validate(mac_address) || !validateName(name)) {
         return false
    }

    const device_group = $("#device-group").find('option:selected').text();
    const location = $("#location").find('option:selected').text();
    const account_id = $("#account-id").val();
    const ip_address = $("#ip-address").val();

    if (device_group !== '' && location !== '' && account_id !== '' && name !== '' && ip_address !== '') {
        return true
    }
    return false
}

$( "#mac-address" ).on('input', function() {
    const mac_address = $(this).val();
    if (validate(mac_address)) {
        $( "#mac-address" ).addClass('valid');
        $( "#mac-address" ).removeClass('invalid');
    }
    else {
        if (mac_address.length >= 17) {
            $( "#mac-address" ).addClass('invalid');
            $( "#mac-address" ).removeClass('valid');
        }
        else {
            $( "#mac-address" ).removeClass('valid');
            $( "#mac-address" ).removeClass('invalid');
        }
    }

    switchUpdateButton();
    switchAddButton();
});


function enableAdd() {
    const addNextEl = $(".dp-addNext");
    addNextEl.removeClass("blocked");
}

function disableAdd() {
    const addNextEl = $(".dp-addNext");
    addNextEl.addClass("blocked");
}

function enableUpdate() {
    const updateEl = $(".dp-update");
    updateEl.removeClass("blocked");
}

function disableUpdate() {
    const updateEl = $(".dp-update");
    updateEl.addClass("blocked");
}

function switchUpdateButton() {
    const isEdit = location.search.includes('?edit=true');
    if (isEdit) {
        if (notChanged()) {
            disableUpdate();
        }
        else {
            enableUpdate();
        }
    }
}

function switchAddButton() {
    if (enableAddCondition()) {
        enableAdd();
    }
    else {
        disableAdd();
    }
}

function changeDeviceGroup() {
    const selectedDeviceGroup = $("#device-group").find('option:selected').text();
    const selectedLocation = $("#location").find('option:selected').text();
    
    // Call api to get optionData again
    $("#spinning-wheel").css("display", "block");
    $.ajax({
        url: `/api/v1/tags/${selectedDeviceGroup}/locations/`,
        method: "GET",
        dataType: 'json',
        contentType: "application/json",
        success: function(data) {
            $("#spinning-wheel").css("display", "none");
            optionData = data;

             // Reload options of location
            const locations = getLocations(optionData);
            $('#location').empty();
            for (let i=0; i < locations.length; i++) {
                $('#location').append(`<option value=${i}>${locations[i]}</option>`);
            }

            // Handle to keep the location selected
            const locationIndex = locations.indexOf(selectedLocation);
            if (locationIndex !== -1) {
                $('#location').val(locationIndex.toString());
            }
            changeLocation();

            switchUpdateButton();
            switchAddButton();
        },
        error: function(error) {
            $("#spinning-wheel").css("display", "none");
            showErrorNotification(error['responseJSON'].includes('Please provide admin credential') ? error['responseJSON'] : 'Server error occurred. Check logs for more details.');
        }
    });
}

function changeLocation() {
    const selectedLocation = $("#location").find('option:selected').text();
    const selectedDomain = $("#dns-domain").find('option:selected').text();
    const selectedIpNetwork = $("#ip-network").find('option:selected').text();

    if (selectedLocation !== '') {
        $("#ip-network").removeClass('disabled');
        const ipNetworks = getIpNetworks(optionData, getLocationCode(selectedLocation));
        $('#ip-network').empty();
        for (let i=0; i < ipNetworks.length; i++) {
            $('#ip-network').append(`<option value=${i}>${ipNetworks[i]}</option>`);
        }  

        $("#dns-domain").removeClass('disabled');
        const dnsDomains = getDnsDomains(optionData, getLocationCode(selectedLocation));
        $('#dns-domain').empty();
        for (let i=0; i < dnsDomains.length; i++) {
            $('#dns-domain').append(`<option value=${i}>${dnsDomains[i]}</option>`);
        }   

         // Handle to keep the dns domain selected
         const domainIndex = dnsDomains.indexOf(selectedDomain);
         if (domainIndex !== -1) {
            $('#dns-domain').val(domainIndex.toString());
         }

        // Handle to keep the IP Network selected
        const ipNetworkIndex = ipNetworks.indexOf(selectedIpNetwork);
        if (ipNetworkIndex !== -1) {
            $('#ip-network').val(ipNetworkIndex.toString());
        }
    }
    else {
        $('#ip-network').empty();
        $("#ip-network").addClass('disabled');

        $('#dns-domain').empty();
        $("#dns-domain").addClass('disabled');
    }

    changeIpNetwork();

    switchUpdateButton();
    switchAddButton();
}

function changeIpNetwork() {
    const selectedLocation = $("#location").find('option:selected').text();
    const selectedIpNetwork = $("#ip-network").find('option:selected').text();

    if (selectedIpNetwork !== '') {
        const ipAddress = getIpAddress(optionData, getLocationCode(selectedLocation), selectedIpNetwork);
        const detail = getIpNetworkDetail(optionData, getLocationCode(selectedLocation), selectedIpNetwork);
        $("#ip-address").val(ipAddress)

        const htmlContent = networkDetailTemplate(detail);
        $(".textContent").html(htmlContent);
    }
    else {
        $("#ip-address").val("");
        $(".textContent").html("");
    }

    switchUpdateButton();
}

$( "#device-group" ).on('change', function() {
    changeDeviceGroup();
});

$("#name" ).on('input', function() {
    checkNameField();
    switchUpdateButton();
    switchAddButton();
});

function checkNameField() {
    const name = $('#name').val();   
    if (validateName(name)) {
        $( "#name" ).addClass('valid');
        $( "#name" ).removeClass('invalid');
    }
    else {
        if (name !== '') {
            $( "#name" ).addClass('invalid');
            $( "#name" ).removeClass('valid');
        }
        else {
            $( "#name" ).removeClass('invalid');
            $( "#name" ).removeClass('valid');
        }
    }
}

$( "#location" ).on('change', function() {
    changeLocation();
});

$( "#ip-network" ).on('change', function() {
    changeIpNetwork();
    switchAddButton();
    const ip_address = $('#ip-address').val();
    const ip_network = $('#ip-network').find('option:selected').text();
    if (ip_address !== '') {
        changeNotificationMess('', '', false);
    } 
    else {
        changeNotificationMess(`Network ${ip_network} is out of IP Address`, 'fail', true);
    }
});

$( "#dns-domain" ).on('change', function() {
    switchUpdateButton();
});

$( "#description" ).on('input', function() {
    switchUpdateButton();
});

$( "#account-id" ).on('input', function() {
    switchUpdateButton();
    switchAddButton();
});

$(".dp-clear").click(function() {
    $(location).prop('href', '/device_management/device_management_endpoint');
})

$('.dp-delete').on('click', function(event){
    if ($('.dp-delete').hasClass('blocked')) return;
    event.preventDefault();
    $('.delete-popup').addClass('is-visible');
});

$('.dp-unassign').on('click', function(event){
    if ($('.dp-unassign').hasClass('blocked')) return;
    event.preventDefault();
    $('.unassign-popup').addClass('is-visible');
});

// *******************************************Delete *********************************************

$('.delete-popup').on('click', function(event){
    if( $(event.target).is('.delete-popup-close') || $(event.target).is('.delete-popup') ) {
        event.preventDefault();
        $(this).removeClass('is-visible');
    }
});

$(document).keyup(function(event){
    if(event.which=='27'){
        $('.delete-popup').removeClass('is-visible');
    }
});

$(document).on("click", function (event) {
    if ($(".delete-popup").css('display') === 'block') {
        if ($(event.target).closest(".delete-popup-container").length === 0 && $(event.target).closest(".dp-delete").length === 0) {
            $('.delete-popup').removeClass('is-visible');
          }
    }
});

$('.cancel-delete').on('click', function(event){
    $('.delete-popup').removeClass('is-visible');
});

$('.accept-delete').on('click', function(event){
    $('.delete-popup').removeClass('is-visible');

    const mac_address = location.search.split("&").slice(-2)[0].split("=").slice(-1)[0];
    let ip_address = location.search.split("&").slice(-2)[1].split("=").slice(-1)[0];
    const data = JSON.parse(sessionStorage.getItem('current-device'));
    if (data.ip_info.ip_address) ip_address = data.ip_info.ip_address;

    $("#spinning-wheel").css("display", "block");
    $.ajax({
        url: `/api/v1/configurations/${config_name}/mac_address?is_multiple_ip=${0}`,
        method: "DELETE",
        data: JSON.stringify({
            "mac_address": mac_address,
            "name": "",
            "device_group": "",
            "device_location": "",
            "ip_address": ip_address,
            "dns_domain": "",
            "account_id": "",
            "description": "",
            "access_right": "",
            // "is_multiple_ip": 0
        }),
        dataType: 'json',
        contentType: "application/json",
        success: function(data) {
            $("#spinning-wheel").css("display", "none");
        },
        error: function(error) {
            if (error.responseText === 'Delete successful!') {
                sessionStorage.setItem('isDelete', true);
                const currentUrl = location.search;
                window.location.replace(currentUrl.replace('edit=true&', ''));
            }
            else {
                $("#spinning-wheel").css("display", "none");
            }
        }
    });
    
});

// *********************************************************************************************


// *******************************************Unassign *********************************************
$('.unassign-popup').on('click', function(event){
    if( $(event.target).is('.unassign-popup-close') || $(event.target).is('.unassign-popup') ) {
        event.preventDefault();
        $(this).removeClass('is-visible');
    }
});

$(document).keyup(function(event){
    if(event.which=='27'){
        $('.unassign-popup').removeClass('is-visible');
    }
});

$(document).on("click", function (event) {
    if ($(".unassign-popup").css('display') === 'block') {
        if ($(event.target).closest(".delete-popup-container").length === 0 && $(event.target).closest(".dp-unassign").length === 0) {
            $('.unassign-popup').removeClass('is-visible');
          }
    }
});

$('.cancel-unassign').on('click', function(event){
    $('.unassign-popup').removeClass('is-visible');
});

$('.accept-unassign').on('click', function(event){
    $('.unassign-popup').removeClass('is-visible');

    const mac_address = location.search.split("&").slice(-2)[0].split("=").slice(-1)[0];
    let ip_address = location.search.split("&").slice(-2)[1].split("=").slice(-1)[0];
    const data = JSON.parse(sessionStorage.getItem('current-device'));
    if (data.ip_info.ip_address) ip_address = data.ip_info.ip_address;


    $("#spinning-wheel").css("display", "block");
    $.ajax({
        url: `/api/v1/configurations/${config_name}/mac_address?is_multiple_ip=${1}`,
        method: "DELETE",
        data: JSON.stringify({
            "mac_address": mac_address,
            "name": "",
            "device_group": "",
            "device_location": "",
            "ip_address": ip_address,
            "dns_domain": "",
            "account_id": "",
            "description": "",
            "access_right": "",
            // "is_multiple_ip": 1
        }),
        dataType: 'json',
        contentType: "application/json",
        success: function(data) {
            $("#spinning-wheel").css("display", "none");
        },
        error: function(error) {
            if (error.responseText === 'Delete successful!') {
                sessionStorage.setItem('isDelete', true);
                sessionStorage.setItem('isUnassign', true);
                sessionStorage.setItem('unassignIp', ip_address);
                window.location.replace(`/device_management/device_management_endpoint?edit=true&mac=${mac_address}&ip_address=`);
            }
        }
    });
    
});
// *********************************************************************************************


$('.dp-addNext').on('click', function(event){
    if (!$(".dp-addNext").hasClass('blocked')) {
        $(".notification").css("display", "none");
        
        $("#spinning-wheel").css("display", "block");
        const mac_address = convert_format($("#mac-address").val());
        $.ajax({
            url: `/api/v1/configurations/${config_name}/mac_address/`,
            method: "POST",
            data: JSON.stringify({
                "mac_address": mac_address,
                "access_right": group_access_right[$("#device-group").find('option:selected').text()],
                "name": $("#name").val(),
                "device_group": $("#device-group").val() !== "" ? $("#device-group").find('option:selected').text() : "",
                "device_location": $("#location").val() !== "" ? getLocationCode($("#location").find('option:selected').text()): "",
                "ip_address": $("#ip-address").val(),
                "dns_domain": $("#dns-domain").val() !== "" ? $("#dns-domain").find('option:selected').text(): "",
                "account_id": $("#account-id").val(),
                "description": $("#description").val()
            }),
            dataType: 'json',
            contentType: "application/json",
            success: function(data) {
                if (typeof data === 'object') {
                    $("#mac-address").val('');
                
                    const default_group_device = $("#device-group").find('option:selected').text();
                    $.ajax({
                        url: `/api/v1/tags/${default_group_device}/locations/`,
                        method: "GET",
                        dataType: 'json',
                        contentType: "application/json",
                        success: function(data) {
                            $("#spinning-wheel").css("display", "none");
                            var el = document.querySelector(".notification");
                            el.style.display = 'block';
                            el.classList.remove('notification--fail');
                            el.innerHTML = `<span>Device added with MAC address <span style="font-weight: 800">${mac_address}</span></span>`;
                            optionData = data;
        
                            if ($("#ip-network").val() !== "") {
                                const selectedLocation = $("#location").find('option:selected').text();
                                const selectedIpNetwork = $("#ip-network").find('option:selected').text();
                                const ipAddress = getIpAddress(optionData, getLocationCode(selectedLocation), selectedIpNetwork);
                                $("#ip-address").val(ipAddress);
                            }
        
                        },
                        error: function(error) {
                            $("#spinning-wheel").css("display", "none");
                            showErrorNotification(error['responseJSON'].includes('Please provide admin credential') ? error['responseJSON'] : 'Server error occurred. Check logs for more details.');
                        }
                    });

                    $( "#mac-address" ).removeClass('valid');
                    disableAdd();
                }
                else {
                    $("#spinning-wheel").css("display", "none");
                    var el = document.querySelector(".notification");
                    el.style.display = 'block';
                    el.classList.add('notification--fail');
                    el.innerText = data;
                }
            },
            error: function(error) {
                $("#spinning-wheel").css("display", "none");
                var el = document.querySelector(".notification");
                el.style.display = 'block';
                el.classList.add('notification--fail');
                el.innerText = error.responseText;

            }
        });

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

$('.dp-update').on('click', function(event){
    if ($(".dp-update").hasClass('blocked')) return;

    const mac_address = location.search.split("&").slice(-2)[0].split("=").slice(-1)[0];
    const data = JSON.parse(sessionStorage.getItem('current-device'));

    const updateData = {
        "mac_address": mac_address,
        "name": $( "#name" ).val(),
        "access_right": data.access_right,
        "ip_address_id": data.ip_info.ip_address_id ? data.ip_info.ip_address_id.toString() : "",
        "host_record_id": data.dns_domain.host_record_id ? data.dns_domain.host_record_id.toString(): "",
        "account_id": $( "#account-id" ).val(),
        "description": $( "#description" ).val()
    }

    // Update data in session storage
    const newCurrentDevice = {
        ...data,
        "mac_address": mac_address,
        "name": $( "#name" ).val(),
        "mac-account-id": $( "#account-id" ).val(),
        "mac-description": $( "#description" ).val()
    }
    sessionStorage.setItem('current-device', JSON.stringify(newCurrentDevice));

    $("#spinning-wheel").css("display", "block");
    changeNotificationMess('', '', false);
    $.ajax({
        url: `/api/v1/configurations/${config_name}/mac_address/`,
        method: "PATCH",
        data: JSON.stringify(updateData),
        dataType: 'json',
        contentType: "application/json",
        success: function(data) {
            $("#spinning-wheel").css("display", "none");
            changeNotificationMess('Device updated successfully', 'success', true);

            // Update the audit list
            var html = auditTableTemplate(data);
            $("#auditTable tbody").html(html);
        },
        error: function(error) {
            $("#spinning-wheel").css("display", "none");
            changeNotificationMess('Failed to update device', 'fail', true);
        }
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
    disableUpdate();

});


$('.dp-clearUpdate').on('click', function(event){
    const data = JSON.parse(sessionStorage.getItem('current-device'));
    $("#name").val(data.name);
    checkNameField();
    $("#account-id").val(data['mac-account-id']);
    $("#description").val(!!data["mac-description"] ? data["mac-description"] : "");

    disableUpdate();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

function changeNotificationMess(content, status, show) {
    if (show) {
        var el = document.querySelector(".notification");
        el.style.display = 'block';
        el.innerText = content;
        if (status === 'success') {
            el.classList.remove('notification--fail');
        }
        else {
            el.classList.add('notification--fail');
        }
    }
    else {
        var el = document.querySelector(".notification");
        el.style.display = 'none';
    }
}

// Show error message when error happens in the server (issues when calling api)
function showErrorNotification(content=null) {
    var el = document.querySelector(".notification");
    el.style.display = 'block';
    el.classList.add('notification--fail');
    if (content) {
        el.innerText = content;
    }
    else {
        el.innerText = 'Server error occurred. Check server logs for more details.';
    }
}

// Create a audit template table
function auditTableTemplate(data) {
    var html = ``;
    $.each(data, function(index, item){
        html += `
            <tr id=${index}>
                <td>${getValue(item.user)}</td>
                <td>${getValue(item.action)}</td>
                <td>${getValue(item.date_time)}</td>
            </tr>
        `;
    });
    return html;
}

function networkDetailTemplate(data) {
    let html = ``;
    $.each(data, function(index, item){
        html += `
        <li>
            <span class="detail-title">${item.title}: </span>
            <span class="content">${item.content}</span>
        </li>
        `;
    });
    html = '<ul>' + html + '</ul>'

    return html
}