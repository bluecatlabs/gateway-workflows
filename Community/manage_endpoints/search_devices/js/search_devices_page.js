const SEARCH_LIMIT = 100;
let totalDevices;
let optionData = {}; // based on device group
let searchClick = false;
let group_access_right = {};
let config_name;

// Search values
let mac_address = "";
let name = "";
let ip_address = "";
let device_group = "";
let device_location = "";
let ip_network = "";
let dns_domain = "";
let account_id = "";

// let current_page = 1;
let allDevices = [];
let downloadingFile = false;

$(document).ready(function() {
    cleanUpData();
    try {
      getDefaultConfiguration()
    }
    catch(err) {
        changeNotificationMess("Missing config file. Please check installation.", 'fail', true);
    }
});



function getDefaultConfiguration(){
    // Get config name
    $.ajax({
        url: '/api/v1/configuration_name/',
        method: "GET",
        dataType: 'json',
        contentType: "application/json",
        success: function(result) {
            config_name = result;

            sessionStorage.removeItem('current-device');

            $("#spinning-wheel").css("display", "block");
            $.ajax({
                url: '/api/v1/tags/',
                method: "GET",
                dataType: 'json',
                contentType: "application/json",
                success: function(data) {
                    setTimeout(function() {
                        $("#spinning-wheel").css("display", "none");
                    }, 500);

                    device_groups = data.map(x => Object.keys(x)[0]);
                    for (let x of data) {
                        group_access_right = {...group_access_right, ...x}
                    }

                    for (let i=0; i < device_groups.length; i++) {
                        $('#device-group').append(`<option value=${i}>${device_groups[i]}</option>`);
                    }

                },
                error: function(error) {
                    $("#spinning-wheel").css("display", "none");
                    changeNotificationMess('Server error occurred. Check logs for more details.', 'fail', true);
                }
            });
        },
        error: function(error) {
            changeNotificationMess("Configuration not defined.", 'fail', true);
        }
    });
}


function hasSearch() {
    const name = $('#name').val();
    if (name.trim().length === 0 && name.length > 0) return false;
    const fields = ['#mac-address', '#device-group', '#name', '#ip-address'];
    let result = false;
    for (let field of fields) {
        if ($(field).val() !== '' && field !== '#device-group') result = true;
    }
    if ($("#device-group").val() !== '' && $("#location").val() !== '') return true;
   
    return result;
}

function enableSearch() {
    $(".dp-search").removeClass("blocked");
}

function disableSearch() {
    $(".dp-search").addClass("blocked");
}

function enableDownload() {
    $(".download-csv").removeClass("blocked");
}

function disableDownload() {
    $(".download-csv").addClass("blocked");
}

function switchSearchDownloadButton() {
    if (hasSearch()) {
        enableSearch();
    }
    else {
        disableSearch();
    }

    if (hasSearch()) {
        enableDownload();
    }
    else {
        disableDownload(); 
    }
}

function cleanUpData() {
    
    // Set Values
    $("#mac-address").val("");
    $("#ip-address").val("");
    $("#name").val("");
    $("#device-group").val("");
    $("#location").val("");
    $("#ip-network").val("");
    $("#dns-domain").val("");
    $(".textContent").html("");

    $("#mac-address").removeClass('disabled');
    $("#name").removeClass('disabled');
    $("#ip-address").removeClass('disabled');
    $("#device-group").removeClass('disabled');

    // Clear format validation mess on mac address field
    $( "#mac-address" ).removeClass('valid');
    $( "#mac-address" ).removeClass('invalid');

     // Close all fields
    $("#ip-network").addClass('disabled');
    $("#location").addClass('disabled');
    $("#ip-network").addClass('disabled');
    $("#dns-domain").addClass('disabled');
    $("#account-id").addClass('disabled');
}


function changeDeviceGroup() {

    const selectedDeviceGroup = $("#device-group").find('option:selected').text();
    const selectedLocation = $("#location").find('option:selected').text();

    if (selectedDeviceGroup !== "Please Select") {
        $('#location').removeClass('disabled');

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
                $('#location').empty().append('<option value="">Please Select</option>');
                for (let i=0; i < locations.length; i++) {
                    $('#location').append(`<option value=${i}>${locations[i]}</option>`);
                }

                 // Handle to keep the locations
                const locationIndex = locations.indexOf(selectedLocation);
                if (locationIndex !== -1) {
                    $('#location').val(locationIndex.toString());
                }

                changeLocation();
            },
            error: function(error) {
                $("#spinning-wheel").css("display", "none");
                changeNotificationMess(JSON.stringify(error), 'fail', true);
            }
        });
    }
    else {
        $('#location').empty().append('<option value="">Please Select</option>');
        $('#location').addClass('disabled');

        changeLocation();
    }

    switchSearchDownloadButton();
}

function changeLocation() {

    const selectedLocation = $("#location").find('option:selected').text();
    const selectedDomain = $("#dns-domain").find('option:selected').text();
    const selectedIpNetwork = $("#ip-network").find('option:selected').text();

    if (selectedLocation !== 'Please Select') {
        $("#ip-network").removeClass('disabled');

        // Reload options for IP Network
        const ipNetworks = getIpNetworks(optionData, getLocationCode(selectedLocation));
        $('#ip-network').empty().append('<option value="">Please Select</option>');
        for (let i=0; i < ipNetworks.length; i++) {
            $('#ip-network').append(`<option value=${i}>${ipNetworks[i]}</option>`);
        }  

        // Handle to keep the IP Network
        const ipNetworkIndex = ipNetworks.indexOf(selectedIpNetwork);
        if (ipNetworkIndex !== -1) {
            $('#ip-network').val(ipNetworkIndex.toString());
        }


    }
    else {
        $('#ip-network').empty().append('<option value="">Please Select</option>');
        $("#ip-network").addClass('disabled');

    }

    changeIpNetwork();
    switchSearchDownloadButton();
}

function changeIpNetwork() {
    const selectedLocation = $("#location").find('option:selected').text();
    const selectedIpNetwork = $("#ip-network").find('option:selected').text();
    const selectedDomain = $("#dns-domain").find('option:selected').text();

    if (selectedIpNetwork !== 'Please Select') {
        $("#dns-domain").removeClass('disabled');
        // Reload options for IP Domain
        const dnsDomains = getDnsDomains(optionData, getLocationCode(selectedLocation));
        $('#dns-domain').empty().append('<option value="">Please Select</option>');
        for (let i=0; i < dnsDomains.length; i++) {
            $('#dns-domain').append(`<option value=${i}>${dnsDomains[i]}</option>`);
        }

         // Handle to keep the dns domain
         const domainIndex = dnsDomains.indexOf(selectedDomain);
         if (domainIndex !== -1) {
            $('#dns-domain').val(domainIndex.toString());
         }

         // Fill detail and IP address 
        const detail = getIpNetworkDetail(optionData, getLocationCode(selectedLocation), selectedIpNetwork);
        const htmlContent = networkDetailTemplate(detail);
        document.querySelector('.textContent').innerHTML = htmlContent;
    }
    else {
        $('#dns-domain').empty().append('<option value="">Please Select</option>');
        $("#dns-domain").addClass('disabled');

        // Clear IP Network detail
        $(".textContent").html("");
    }
}

$( "#mac-address" ).on('keyup', function() {
    let openFields = false;
    const mac_address = $(this).val();

    if (mac_address !== '') {
        $("#name").addClass('disabled');
        $("#ip-address").addClass('disabled');
        $("#device-group").addClass('disabled');
    }
    else {
        $("#name").removeClass('disabled');
        $("#ip-address").removeClass('disabled');
        $("#device-group").removeClass('disabled');
    }

    if (validate(mac_address)) {
        $( "#mac-address" ).addClass('valid');
        $( "#mac-address" ).removeClass('invalid');
        openFields = true;
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

    if (openFields) {
        enableSearch();
        enableDownload();
    }
    else {
        disableSearch();
        disableDownload();
    }

});

$( "#device-group" ).on('change', function() {
    changeDeviceGroup();

    const device_group = $("#device-group").val();
    if (device_group !== '') {
        $("#mac-address").addClass('disabled');
        $("#ip-address").addClass('disabled');
        $("#name").addClass('disabled');

        $("#account-id").removeClass('disabled');
    }
    else {
        $("#mac-address").removeClass('disabled');
        $("#ip-address").removeClass('disabled');
        $("#name").removeClass('disabled');

        $("#account-id").addClass('disabled');
    }
});

$( "#location" ).on('change', function() {
    changeLocation();
});

$( "#ip-network" ).on('change', function() {
    changeIpNetwork();

});

$( "#name" ).on('keyup', function() {
    const name = $("#name").val();
    if (name !== '') {
        $("#mac-address").addClass('disabled');
        $("#ip-address").addClass('disabled');
        $("#device-group").addClass('disabled');
    }
    else {
        $("#mac-address").removeClass('disabled');
        $("#ip-address").removeClass('disabled');
        $("#device-group").removeClass('disabled');
    }

    switchSearchDownloadButton();
});

$( "#ip-address" ).on('keyup', function() {
    const ip_address = $("#ip-address").val();
    if (ip_address !== '') {
        $("#mac-address").addClass('disabled');
        $("#name").addClass('disabled');
        $("#device-group").addClass('disabled');
    }
    else {
        $("#mac-address").removeClass('disabled');
        $("#name").removeClass('disabled');
        $("#device-group").removeClass('disabled');
    }

    switchSearchDownloadButton();
});

function searchToTemplateData(searchData) {
    const result = searchData.map(x => (
        {
            dns_domain: getValue(x.dns_domain.host_name),
            id: x.mac_address,
            ip_address: Object.keys(x.ip_info).length > 0 ? x.ip_info.ip_address : '',
            last_modified: x['mac-audit-trail'][x['mac-audit-trail'].length - 1].date_time,
            mac_address: x.mac_address,
            name: getValue(x.name),
            account_id: getValue(x['mac-account-id'])
        }
    ));

    return result
}

function getAllDevicesApi(searchField, data) {
    let url;
    if (searchField === 'mac_address') {
        url = `/api/v1/configurations/${config_name}/mac_addresses/${data.mac_address}`
    }
    else if (searchField === 'name') {
        url = `/api/v1/configurations/${config_name}/search_mac_address_by_name?name=${data.name}`
    }
    else if (searchField === 'ip_address') {
        url = `/api/v1/configurations/${config_name}/search_mac_address_by_ip_address?ip_address=${data.ip_address}`
    }
    else if (searchField === 'device_group') {
        url = `/api/v1/configurations/${config_name}/mac_addresses?device_group=${data.device_group}&device_location=${data.device_location}&ip_network=${data.ip_network}&dns_domain=${data.dns_domain}&account_id=${account_id}`
    }

    $("#spinning-wheel").css("display", "block");
    changeNotificationMess('', '', false);
    $.ajax({
        url,
        method: "GET",
        dataType: 'json',
        contentType: "application/json",
        success: function(result) {
            $("#spinning-wheel").css("display", "none");
            
            allDevices = result.data;
            totalDevices = result.total;
            if (totalDevices > 0) {
                changeNotificationMess(`${totalDevices} device${totalDevices > 1 ? "s": ""} found`, 'success', true);
            }
            else {
                changeNotificationMess('No device found', 'fail', true);
            }

            // Show Pagination or not (at the first time clicking search)
            if (searchClick) {
                if (result.total > SEARCH_LIMIT) {
                    $("#pagination-container").css("display", "block");
                    $("#total-count").text(Math.ceil(result.total / SEARCH_LIMIT));

                    $("#previous").addClass("button-disable");
                    $("#next").removeClass("button-disable");
                    $("#current-page").text(1);
                    
                }
                else {
                    $("#pagination-container").css("display", "none");
                }
            }

            searchClick = false;
            let renderData = [];
            if (totalDevices > 0) renderData = allDevices.slice(0, Math.min(SEARCH_LIMIT, totalDevices));
            const data = searchToTemplateData(renderData);
            var html = tableTemplate(data);
            document.querySelector('#data-container table tbody').innerHTML = html;
        },
        error: function(error) {
            $("#spinning-wheel").css("display", "none");
            changeNotificationMess('No device found', 'fail', true);
            $("#data-container table tbody").html("");
        }
    });
}


function changeNotificationMess(content, status, show) {
    if (show) {
        $( ".notification" ).removeClass("hide");
        $( ".notification" ).text(content);
        if (status === 'fail') {
            $( ".notification" ).addClass('notification--fail');
        }
        else {
            $( ".notification" ).removeClass('notification--fail');
        }
    }
    else {
        $( ".notification" ).addClass("hide");
    }
}

function search() {
    const data = {
        mac_address,
        name,
        ip_address,
        device_group,
        device_location,
        ip_network,
        dns_domain,
        account_id
    }

    if (mac_address !== "") getAllDevicesApi('mac_address', data);
    if (name !== "") getAllDevicesApi('name', data);
    if (ip_address !== "") getAllDevicesApi('ip_address', data);
    if (device_group !== "") getAllDevicesApi('device_group', data);
}


$(".dp-search").click(function() {
    if ($(".dp-search").hasClass('blocked')) return;

    mac_address = convert_format($("#mac-address").val());
    name = $("#name").val();
    ip_address = $("#ip-address").val();
    device_group = $("#device-group").val() !== "" ? $("#device-group").find('option:selected').text() : "";
    device_location = $("#location").val() !== "" ? getLocationCode($("#location").find('option:selected').text()): "";
    ip_network = $("#ip-network").val() !== "" ? $("#ip-network").find('option:selected').text(): "";
    dns_domain = $("#dns-domain").val() !== "" ? $("#dns-domain").find('option:selected').text(): "";
    account_id = $("#account-id").val();

    searchClick = true;
    search();
})

$(".clear-search").click(function() {
    cleanUpData();
    $(".notification").addClass("hide");
    disableSearch();
    disableDownload(); // new 19/08
    window.scrollTo({ top: 0, behavior: 'smooth' });

    $("#data-container table tbody").html('');
    $("#pagination-container").css("display", "none");

    searchClick = false;
})

// **************************************************main download functions*******************************************************************************
function downloadCSV(data) {
    keys = [
        { fieldName: "device_name", label: "Device Name" },
        { fieldName: "ip_address", label: "IP Address" },
        { fieldName: "mac_address", label: "MAC Address" },
        { fieldName: "account_id", label: "Account ID" },
        { fieldName: "fqdn", label: "FQDN" },
      ];

    if (downloadingFile) {
        const extractedData = extractDataToDownload(data);
        const csvData = csvmaker(extractedData, keys);
        download(csvData);
        stopDownload();

    }
   
}

function callSearchToDownload() {
    const download_mac_address = convert_format($("#mac-address").val());
    const download_name = $("#name").val();
    const download_ip_address = $("#ip-address").val();
    const download_device_group = $("#device-group").val() !== "" ? $("#device-group").find('option:selected').text() : "";
    const download_device_location = $("#location").val() !== "" ? getLocationCode($("#location").find('option:selected').text()): "";
    const download_ip_network = $("#ip-network").val() !== "" ? $("#ip-network").find('option:selected').text(): "";
    const download_dns_domain = $("#dns-domain").val() !== "" ? $("#dns-domain").find('option:selected').text(): "";
    const download_account_id = $("#account-id").val();

    const data = {
        download_mac_address,
        download_name,
        download_ip_address,
        download_device_group,
        download_device_location,
        download_ip_network,
        download_dns_domain,
        download_account_id
    }

    let searchField;
    if (download_mac_address !== "") {
        searchField = 'mac_address';
    }
    if (download_name !== "") {
        searchField = 'name'
    }
    if (download_ip_address !== "") {
        searchField = 'ip_address';
    }
    if (download_device_group !== "") {
        searchField = 'device_group';
    }
  
    
    let url;
    if (searchField === 'mac_address') {
        url = `/api/v1/configurations/${config_name}/mac_addresses/${data.download_mac_address}`
    }
    else if (searchField === 'name') {
        url = `/api/v1/configurations/${config_name}/search_mac_address_by_name?name=${data.download_name}`
    }
    else if (searchField === 'ip_address') {
        url = `/api/v1/configurations/${config_name}/search_mac_address_by_ip_address?ip_address=${data.download_ip_address}`
    }
    else if (searchField === 'device_group') {
        url = `/api/v1/configurations/${config_name}/mac_addresses?device_group=${data.download_device_group}&device_location=${data.download_device_location}&ip_network=${data.download_ip_network}&dns_domain=${data.download_dns_domain}&account_id=${data.download_account_id}`
    }

   
    $.ajax({
      url,
      method: "GET",
      dataType: "json",
      contentType: "application/json",
      success: function (result) {
        downloadCSV(result.data);
      },
      error: function (error) {
        downloadCSV([]);
      },
    });
}
// *********************************************************************************************************************************


// ****************************************************support download functions***************************************************
function startDownloadDisableMode() {
    $('.list-group-item:contains("Search")').css('pointerEvents', 'none');
    $('.list-group-item:contains("Device Management")').css('pointerEvents', 'none');
    $('.data-row').css('pointerEvents', 'none');
    $("input").prop("disabled", true);
    $("select").prop("disabled", true);

    $(".dp-search").addClass("blocked");
    $(".clear-search").addClass("blocked");
}

function endDownloadDisableMode() {
    $('.list-group-item:contains("Search")').css('pointerEvents', 'auto');
    $('.list-group-item:contains("Device Management")').css('pointerEvents', 'auto');
    $('.data-row').css('pointerEvents', 'auto');
    $("input").prop("disabled", false);
    $("select").prop("disabled", false);

    $(".dp-search").removeClass("blocked");
    $(".clear-search").removeClass("blocked");
}

function startDownload() {
    $('.download-csv-mess').css('display', 'inline-block');

    $('.download-csv').css('display', 'none');
    $('.stop-download-csv').css('display', 'block');

    startDownloadDisableMode();
    callSearchToDownload();

    downloadingFile = true;
}

function stopDownload() {
    $('.download-csv-mess').css('display', 'none');

    $('.download-csv').css('display', 'block');
    $('.stop-download-csv').css('display', 'none');
    if (hasSearch()) {
        enableDownload();
    }
    else {
        disableDownload();
    }

    endDownloadDisableMode();
    downloadingFile = false;
}

$(".stop-download-csv").click(function() {
    stopDownload();
})

$(".download-csv").click(function() {
    if ($(".download-csv").hasClass('blocked')) return;
    startDownload();
})
// ******************************************************************************************************************************

function tableTemplate(data) {
    var html = ``;
    $.each(data, function(index, item){
        html += `
            <tr class="data-row" id=${item.mac_address} ip_address=${item.ip_address}>
                <td class="popup-column">
                    <span class="fixed-column name-column">${item.name}</span>
                    ${
                        item.name !== "" ?
                        `<span class="popup-text">${item.name}</span>`:
                        ''
                    }
                </td>
                <td>
                    <span class="fixed-column ip-column">${item.ip_address}</span>
                </td>
                <td>
                    <span class="fixed-column mac-column">${item.mac_address}</span>
                </td>
                <td class="popup-column">
                    <span class="fixed-column account-column">${item.account_id}</span>
                    ${
                        item.account_id !== "" ?
                        `<span class="popup-text">${item.account_id}</span>`:
                        ''
                    }
                </td>
                <td class="popup-column">
                    <span class="fixed-column domain-column">${item.dns_domain}</span>
                    ${
                        item.dns_domain !== "" ?
                        `<span class="popup-text">${item.dns_domain}</span>`:
                        ''
                    }
                </td>
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

// Handle onClick event on each device
$(document).on("click", ".table tbody tr", function() {
    const ip_address = this.getAttribute('ip_address');
    $(location).prop('href', `/device_management/device_management_endpoint?edit=true&mac=${this.id}&ip_address=${ip_address}`);
});

$("#next").click(function(){
    const current_page = $("#current-page").text();
    const updated_page = parseInt(current_page) + 1;
    $("#current-page").text(updated_page);
    $("#previous").removeClass("button-disable");

    // Disable next button
    if (updated_page === Math.ceil(totalDevices / SEARCH_LIMIT)) {
        $("#next").addClass("button-disable");
    }

    // search(updated_page);
    const renderData = allDevices.slice((updated_page-1)*SEARCH_LIMIT, Math.min(updated_page*SEARCH_LIMIT, totalDevices));
    const data = searchToTemplateData(renderData);
    var html = tableTemplate(data);
    document.querySelector('#data-container table tbody').innerHTML = html;
});

$("#previous").click(function(){
    const current_page = $("#current-page").text();
    const updated_page = parseInt(current_page) - 1;
    $("#current-page").text(updated_page);
    $("#next").removeClass("button-disable");

    // Disable previous button
    if (updated_page === 1) {
        $("#previous").addClass("button-disable");
    }

    // search(updated_page);
    const renderData = allDevices.slice((updated_page-1)*SEARCH_LIMIT, Math.min(updated_page*SEARCH_LIMIT, totalDevices));
    const data = searchToTemplateData(renderData);
    var html = tableTemplate(data);
    document.querySelector('#data-container table tbody').innerHTML = html;
});