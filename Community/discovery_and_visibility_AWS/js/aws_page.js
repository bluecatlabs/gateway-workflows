// Copyright 2019 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.

$(function () {
//-----------------------Presets--------------------------//


    var bt = document.getElementById('submit1')
    bt.disabled = false;
    bt.style.display = "none";

    var bt2 = document.getElementById('submit2')
    bt2.disabled = false;
    bt2.className = "mysubmit"

    var region = document.getElementById('aws_region_name')
    region.disabled = false;

    var container = document.getElementById('main-container')
    container.className = "panel login large col-sm-4 col-md-6 col-lg-8";

    $('#aws_secret_access_key').attr('type','password');
    $('#aws_sync_pass').attr('type','password');
    $('#sqs_sync_secret').attr('type','password');
    document.getElementById("status").style.display = "none";
    document.getElementById("mfa_code").style.display = "none";
    document.getElementById("purge_configuration").style.display = "none";

    x = document.querySelector("#sync_history_table_length > label > select")
    console.log("X",x)

    // Load for values from WebStorage
    loadformvalues()

    // Get the latest table data
    sync_table();
    discovery_table();
    sync_history_table();
});

// if the AWS_Region is changed, update the configuration field
$('#aws_region_name').on('change', function()
{
$('#configuration').val($('#aws_region_name').val());
}
);

// If the region is changed update the target configuration
var checkbox = document.getElementById('dynamic_config_mode')
checkbox.addEventListener('change', (event) => {
  if (event.target.checked) {
    console.log('checked')
  } else {
    $('#configuration').val($('#aws_region_name').val());
  }
})


// Handle the submit if there is MFA and save the form values to WebStorage
var bt2 = document.getElementById('submit2')
var mfa = document.getElementById('mfa')
var token = document.getElementById('mfa_code')
var form = document.getElementById('aws_page_form')
bt2.onclick = function () {
if (mfa.checked == true){
  var code = prompt("Enter MFA token code", "");
  document.getElementById('submit2')
  if (!code) {
    return;
  };
  token.value = code;
  saveformvalues()
  form.submit();
} else {
  saveformvalues()
  form.submit();
}
};

// update the status bar every second
setInterval(function() {
  $.ajax({
      url: "status",
      method: 'GET',
      headers: {  'Access-Control-Allow-Origin': 'http://127.0.0.1' },
      success: function(data) {
      if (data)
        {
          document.getElementById("status").style.display = "block";
          var status = document.getElementById('status')
          status.innerHTML = data;
        }
      }
  });
}, 1000);

// update the Tables every 5 seconds
setInterval(function() {
  // Get the latest table data
  console.log('Refreshing Tables')
  sync_table()
  discovery_table()
  sync_history_table()
}, 5000);


function saveformvalues() {
  if (typeof(Storage) !== "undefined") {
    localStorage.setItem("aws_access_key_id", document.getElementById('aws_access_key_id').value );
    localStorage.setItem("aws_secret_access_key", document.getElementById('aws_secret_access_key').value );
    localStorage.setItem("aws_region_name", document.getElementById('aws_region_name').value );
    localStorage.setItem("mfa", $('#mfa').prop('checked') );
    localStorage.setItem("mfa_token", document.getElementById('mfa_token').value );
    localStorage.setItem("role_assume", $('#role_assume').prop('checked') );
    localStorage.setItem("aws_role", document.getElementById('aws_role').value );
    localStorage.setItem("aws_session", document.getElementById('aws_session').value );

    localStorage.setItem("configuration", document.getElementById('configuration').value );
    // localStorage.setItem("dynamic_config_mode", $('#dynamic_config_mode').prop('checked') );

    localStorage.setItem("aws_vpc_import", $('#aws_vpc_import').prop('checked') );
    localStorage.setItem("aws_public_blocks", $('#aws_public_blocks').prop('checked') );
    localStorage.setItem("aws_ec2_import", $('#aws_ec2_import').prop('checked') );
    localStorage.setItem("import_amazon_dns", $('#import_amazon_dns').prop('checked') );
    localStorage.setItem("aws_elbv2_import", $('#aws_elbv2_import').prop('checked') );
    localStorage.setItem("aws_route53_import", $('#aws_route53_import').prop('checked') );
    localStorage.setItem("import_target_domain", document.getElementById('import_target_domain').value );

    localStorage.setItem("aws_sync_start", $('#aws_sync_start').prop('checked') );
    localStorage.setItem("aws_sync_user", document.getElementById('aws_sync_user').value );
    localStorage.setItem("aws_sync_pass", document.getElementById('aws_sync_pass').value );
    localStorage.setItem("sqs_sync_key", document.getElementById('sqs_sync_key').value );
    localStorage.setItem("sqs_sync_secret", document.getElementById('sqs_sync_secret').value );
    // localStorage.setItem("aws_sync_init", $('#aws_sync_init').prop('checked') );
    localStorage.setItem("dynamic_deployment", $('#dynamic_deployment').prop('checked') );

  } else {
    console.log('WebStorage not supported by Browser')
  }
}

function loadformvalues() {
  if (typeof(Storage) !== "undefined") {
    if (localStorage.getItem("aws_access_key_id")) { document.getElementById('aws_access_key_id').value = localStorage.getItem("aws_access_key_id"); }
    if (localStorage.getItem("aws_secret_access_key")) { document.getElementById('aws_secret_access_key').value = localStorage.getItem("aws_secret_access_key"); }
    if (localStorage.getItem("aws_region_name")) { document.getElementById('aws_region_name').value = localStorage.getItem("aws_region_name"); }
    if (localStorage.getItem("mfa")) { $('#mfa').prop('checked',localStorage.getItem("mfa")); }
    if (localStorage.getItem("mfa_token")) { document.getElementById('mfa_token').value = localStorage.getItem("mfa_token"); }
    if (localStorage.getItem("role_assume")) { $('#role_assume').prop('checked',localStorage.getItem("role_assume")); }
    if (localStorage.getItem("aws_role")) { document.getElementById('aws_role').value = localStorage.getItem("aws_role"); }
    if (localStorage.getItem("aws_session")) { document.getElementById('aws_session').value = localStorage.getItem("aws_session"); }

    if (localStorage.getItem("configuration")) { document.getElementById('configuration').value = localStorage.getItem("configuration"); }
    // if (localStorage.getItem("dynamic_config_mode")) { $('#dynamic_config_mode').prop('checked',localStorage.getItem("dynamic_config_mode")); }

    if (localStorage.getItem("aws_vpc_import")) { $('#aws_vpc_import').prop('checked',localStorage.getItem("aws_vpc_import")); }
    if (localStorage.getItem("aws_public_blocks")) { $('#aws_public_blocks').prop('checked',localStorage.getItem("aws_public_blocks")); }
    if (localStorage.getItem("aws_ec2_import")) { $('#aws_ec2_import').prop('checked',localStorage.getItem("aws_ec2_import")); }
    if (localStorage.getItem("import_amazon_dns")) { $('#import_amazon_dns').prop('checked',localStorage.getItem("import_amazon_dns")); }
    if (localStorage.getItem("aws_elbv2_import")) { $('#aws_elbv2_import').prop('checked',localStorage.getItem("aws_elbv2_import")); }
    if (localStorage.getItem("aws_route53_import")) { $('#aws_route53_import').prop('checked',localStorage.getItem("aws_route53_import")); }
    if (localStorage.getItem("import_target_domain")) { document.getElementById('import_target_domain').value = localStorage.getItem("import_target_domain"); }

    if (localStorage.getItem("aws_sync_start")) { $('#aws_sync_start').prop('checked',localStorage.getItem("aws_sync_start")); }
    if (localStorage.getItem("aws_sync_user")) { document.getElementById('aws_sync_user').value = localStorage.getItem("aws_sync_user"); }
    if (localStorage.getItem("aws_sync_pass")) { document.getElementById('aws_sync_pass').value = localStorage.getItem("aws_sync_pass"); }
    if (localStorage.getItem("sqs_sync_key")) { document.getElementById('sqs_sync_key').value = localStorage.getItem("sqs_sync_key"); }
    if (localStorage.getItem("sqs_sync_secret")) { document.getElementById('sqs_sync_secret').value = localStorage.getItem("sqs_sync_secret"); }
    // if (localStorage.getItem("aws_sync_init")) { $('#aws_sync_init').prop('checked',localStorage.getItem("aws_sync_init")); }
    if (localStorage.getItem("dynamic_deployment")) { $('#dynamic_deployment').prop('checked',localStorage.getItem("dynamic_deployment")); }

    if (localStorage.getItem("mfa_code")) { document.getElementById('mfa_code').value = localStorage.getItem("mfa_code"); }

  } else {
    console.log('WebStorage not supported by Browser')
  }
}

function sync_table() {
  $("#sync_table").DataTable();
    $.ajax({
      type: 'GET',
      url: "jobs",
      contentType: "text/plain",
      dataType: 'json',
      success: function (data) {
        myJsonData = data;
        populateDataTable(myJsonData);
      },
      error: function (e) {
        console.log("There was an error with your request...");
      }
    });

  // populate the Sync Status data table with JSON data
  function populateDataTable(data) {
    console.log("populating sync_table table...");
    console.log("DATA:",data)
    $("#sync_table").DataTable().destroy();
    $("#sync_table").DataTable({
      paging: false,
      order: [1,"desc"],
      searching: false,
      info: false,
      autoWidth: false,
      processing: false,
      data: data,
      columns: [ { data: "Region"}, { data: "StartTime"}, { data: "Target"}, { data: "StateChanges"}, ]
    }
  );
}};;


// Get the latest Sync Status data JSON data
function discovery_table() {
  $("#discovery_table").DataTable();
    $.ajax({
      type: 'GET',
      url: "discovery_stats",
      contentType: "text/plain",
      dataType: 'json',
      success: function (data) {
        myJsonData = data;
        populateDataTable(myJsonData);
      },
      error: function (e) {
        console.log("There was an error with your request...");
      }
    });

  // populate the Sync hist data table with JSON data
  function populateDataTable(data) {
    console.log("populating discovery_table table...");
    console.log("DATA:",data)
    $("#discovery_table").DataTable().destroy();
    $("#discovery_table").DataTable({
      searching: false,
      order: [1,"desc"],
      info: true,
      autoWidth: false,
      processing: true,
      paging: true,
      data: data,
      columns: [ { data: "Region"}, { data: "Time"}, { data: "Infrastructure"}, { data: "count"}, ]
    }
  );
}};

// Get the latest Sync Status data JSON data
function sync_history_table() {
  $("#sync_history_table").DataTable();
    $.ajax({
      type: 'GET',
      url: "synchistory",
      contentType: "text/plain",
      dataType: 'json',
      success: function (data) {
        myJsonData = data;
        populateDataTable(myJsonData);
      },
      error: function (e) {
        console.log("There was an error with your request...");
      }
    });

  // populate the Sync Satus data table with JSON data
  function populateDataTable(data) {
    console.log("populating sync_history_data table...");
    console.log("DATA:",data)
    $("#sync_history_table").DataTable().destroy();
    $("#sync_history_table").DataTable({
      searching: false,
      order: [1,"desc"],
      info: true,
      autoWidth: false,
      processing: true,
      paging: true,
      data: data,
      columns: [ { data: "Region"}, { data: "Time"}, { data: "Action"}, { data: "EC2"}, ]
    }
  );
}};
