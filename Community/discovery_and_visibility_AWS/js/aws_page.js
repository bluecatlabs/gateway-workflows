// Copyright 2019 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.
// v1.0.7 - B.Shorland

$(function () {
//-----------------------Presets--------------------------//

    document.getElementById('exit').addEventListener('click', function (event)
    {
      window.location.href='/'
    }, false);

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

    // update the status bar every second
    setInterval(function() {
      $.ajax({
          url: "status",
          method: 'GET',
          headers: {  'Access-Control-Allow-Origin': 'http://127.0.0.1' },
          success: function(sdata) {
          var status = document.getElementById('status')

          // Remove the errorExit div using pure JS from the string
          var relexit = status.innerHTML
          var relexit = relexit.replace('<div class="errorexit" id="errorexit" style="display: inline-block; float: right;"><i class="material-icons">clear</i></div>','')

          if (relexit.trim() !== sdata.trim()) {
            {
              if (sdata.includes('ERROR')) {
                console.log('ERROR alert')
                status.innerHTML = sdata;
                $('#status').css('background-color','#DA6900')
                $('#status').css('color','#001c32')
                $('.status').fadeIn("fast");
                // Dynamically add a close to the ERROR status
                const div = document.createElement('div');
                div.className = 'errorexit';
                div.id = 'errorexit'
                div.style.display = "inline-block";
                div.style.float = 'right';
                div.innerHTML = `<i class='material-icons'>clear</i>`;
                div.onclick = function() { $('.status').fadeOut("fast"); console.log("Cleared Error Status") };
                status.appendChild(div);

              }
              else {
                console.log('INFO alert')
                status.innerHTML = sdata;
                $('#status').css('background-color','#01b5ff')
                $('#status').css('color','white')
                $('.status').fadeIn("slow");
              }
            }
          }
        }
      });
    }, 1000);

    setTimeout(function() {
        var thisstatus = document.getElementById('status').innerHTML;
        if (thisstatus.includes('ERROR')) {
          return;
        }
        else {
          $('.status').fadeOut("slow");
        }
    }, 5000); // <-- time in milliseconds


    // update the Tables every 5 seconds
    setInterval(function() {
      // Get the latest table data
      console.log('Refreshing Tables')
      sync_table()
      discovery_table()
      sync_history_table()
    }, 5000);


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
  $('html, body').animate({ scrollTop: 0 }, 'fast');
  form.submit();
} else {
  saveformvalues()
  form.submit();
}
};


function saveformvalues() {
  if (typeof(Storage) !== "undefined") {

    // Handle save field values
    localStorage.setItem("aws_access_key_id", document.getElementById('aws_access_key_id').value );
    localStorage.setItem("aws_secret_access_key", document.getElementById('aws_secret_access_key').value );
    localStorage.setItem("aws_region_name", document.getElementById('aws_region_name').value );
    localStorage.setItem("mfa_token", document.getElementById('mfa_token').value );
    localStorage.setItem("aws_role", document.getElementById('aws_role').value );
    localStorage.setItem("aws_session", document.getElementById('aws_session').value );
    localStorage.setItem("configuration", document.getElementById('configuration').value );
    localStorage.setItem("import_target_domain", document.getElementById('import_target_domain').value );
    localStorage.setItem("aws_sync_user", document.getElementById('aws_sync_user').value );
    localStorage.setItem("aws_sync_pass", document.getElementById('aws_sync_pass').value );
    localStorage.setItem("sqs_sync_key", document.getElementById('sqs_sync_key').value );
    localStorage.setItem("sqs_sync_secret", document.getElementById('sqs_sync_secret').value );

    // Handle toggle buttons state save
    localStorage.setItem("mfa", document.getElementById("mfa").checked);
    console.log("mfa storage:" + localStorage.mfa)
    console.log("mfa box:" + document.getElementById("mfa").checked)

    localStorage.setItem("role_assume", document.getElementById("role_assume").checked);
    console.log("role_assume storage:" + localStorage.role_assume)
    console.log("role_assume box:" + document.getElementById("role_assume").checked)

    localStorage.setItem("dynamic_config_mode", document.getElementById("dynamic_config_mode").checked);
    console.log("dynamic_config_mode storage:" + localStorage.dynamic_config_mode)
    console.log("dynamic_config_mode box:" + document.getElementById("dynamic_config_mode").checked)

    localStorage.setItem("aws_vpc_import", document.getElementById("aws_vpc_import").checked);
    console.log("aws_vpc_import storage:" + localStorage.aws_vpc_import)
    console.log("aws_vpc_import box:" + document.getElementById("aws_vpc_import").checked)

    localStorage.setItem("aws_public_blocks", document.getElementById("aws_public_blocks").checked);
    console.log("aws_public_blocks storage:" + localStorage.aws_public_blocks)
    console.log("aws_public_blocks box:" + document.getElementById("aws_public_blocks").checked)

    localStorage.setItem("aws_ec2_import", document.getElementById("aws_ec2_import").checked);
    console.log("aws_ec2_import storage:" + localStorage.aws_ec2_import)
    console.log("aws_ec2_import box:" + document.getElementById("aws_ec2_import").checked)

    localStorage.setItem("import_amazon_dns", document.getElementById("import_amazon_dns").checked);
    console.log("import_amazon_dns storage:" + localStorage.import_amazon_dns)
    console.log("import_amazon_dns box:" + document.getElementById("import_amazon_dns").checked)

    localStorage.setItem("aws_elbv2_import", document.getElementById("aws_elbv2_import").checked);
    console.log("aws_elbv2_import storage:" + localStorage.aws_elbv2_import)
    console.log("aws_elbv2_import box:" + document.getElementById("aws_elbv2_import").checked)

    localStorage.setItem("aws_route53_import", document.getElementById("aws_route53_import").checked);
    console.log("aws_route53_import storage:" + localStorage.aws_route53_import)
    console.log("aws_route53_import box:" + document.getElementById("aws_route53_import").checked)

    localStorage.setItem("aws_sync_start", document.getElementById("aws_sync_start").checked);
    console.log("aws_sync_start storage:" + localStorage.aws_sync_start)
    console.log("aws_sync_start box:" + document.getElementById("aws_sync_start").checked)

    localStorage.setItem("dynamic_deployment", document.getElementById("dynamic_deployment").checked);
    console.log("dynamic_deployment storage:" + localStorage.dynamic_deployment)
    console.log("dynamic_deployment box:" + document.getElementById("dynamic_deployment").checked)



  } else {
    console.log('WebStorage not supported by Browser')
  }
}

function loadformvalues() {
  if (typeof(Storage) !== "undefined") {
    // Field strings
    if (localStorage.getItem("aws_access_key_id")) { document.getElementById('aws_access_key_id').value = localStorage.getItem("aws_access_key_id"); }
    if (localStorage.getItem("aws_secret_access_key")) { document.getElementById('aws_secret_access_key').value = localStorage.getItem("aws_secret_access_key"); }
    if (localStorage.getItem("aws_region_name")) { document.getElementById('aws_region_name').value = localStorage.getItem("aws_region_name"); }
    if (localStorage.getItem("mfa_token")) { document.getElementById('mfa_token').value = localStorage.getItem("mfa_token"); }
    if (localStorage.getItem("aws_role")) { document.getElementById('aws_role').value = localStorage.getItem("aws_role"); }
    if (localStorage.getItem("aws_session")) { document.getElementById('aws_session').value = localStorage.getItem("aws_session"); }
    if (localStorage.getItem("configuration")) { document.getElementById('configuration').value = localStorage.getItem("configuration"); }
    if (localStorage.getItem("import_target_domain")) { document.getElementById('import_target_domain').value = localStorage.getItem("import_target_domain"); }
    if (localStorage.getItem("aws_sync_user")) { document.getElementById('aws_sync_user').value = localStorage.getItem("aws_sync_user"); }
    if (localStorage.getItem("aws_sync_pass")) { document.getElementById('aws_sync_pass').value = localStorage.getItem("aws_sync_pass"); }
    if (localStorage.getItem("sqs_sync_key")) { document.getElementById('sqs_sync_key').value = localStorage.getItem("sqs_sync_key"); }
    if (localStorage.getItem("sqs_sync_secret")) { document.getElementById('sqs_sync_secret').value = localStorage.getItem("sqs_sync_secret"); }
    if (localStorage.getItem("mfa_code")) { document.getElementById('mfa_code').value = localStorage.getItem("mfa_code"); }

    // Toggle states
    document.getElementById("mfa").checked = localStorage.mfa === 'true';
    document.getElementById("role_assume").checked = localStorage.role_assume === 'true';
    document.getElementById("dynamic_config_mode").checked = localStorage.dynamic_config_mode === 'true';
    document.getElementById("aws_vpc_import").checked = localStorage.aws_vpc_import === 'true';
    document.getElementById("aws_public_blocks").checked = localStorage.aws_public_blocks === 'true';
    document.getElementById("aws_ec2_import").checked = localStorage.aws_ec2_import === 'true';
    document.getElementById("import_amazon_dns").checked = localStorage.import_amazon_dns === 'true';
    document.getElementById("aws_elbv2_import").checked = localStorage.aws_elbv2_import === 'true';
    document.getElementById("aws_route53_import").checked = localStorage.aws_route53_import === 'true';
    document.getElementById("aws_sync_start").checked = localStorage.aws_sync_start === 'true';
    document.getElementById("dynamic_deployment").checked = localStorage.dynamic_deployment === 'true';

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
    $("#sync_table").DataTable().destroy();
    $("#sync_table").DataTable({
      paging: false,
      order: [0,"desc"],
      searching: false,
      info: false,
      autoWidth: false,
      processing: false,
      data: data,
      columns: [ { data: "StartTime"}, { data: "Region"}, { data: "Target"}, { data: "StateChanges"}, ]
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
    $("#discovery_table").DataTable().destroy();
    $("#discovery_table").DataTable({
      searching: false,
      order: [0,"desc"],
      info: true,
      autoWidth: false,
      processing: true,
      paging: true,
      data: data,
      columns: [ { data: "Time"}, { data: "Region"},  { data: "Infrastructure"}, { data: "count"}, ]
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
    $("#sync_history_table").DataTable().destroy();
    $("#sync_history_table").DataTable({
      searching: false,
      order: [0,"desc"],
      info: true,
      autoWidth: false,
      processing: true,
      paging: true,
      data: data,
      columns: [ { data: "Time"}, { data: "Region"}, { data: "Action"}, { data: "EC2"}, ]
    }
  );
}};
