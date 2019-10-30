// Copyright 2019 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.
$(function () {
//-----------------------Presets--------------------------//
    var bt = document.getElementById('submit1')
    bt.disabled = false;
    bt.style.display = "none";

    // document.getElementById("submit").className = 'mysubmit'

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
    // document.getElementByID("purge_configuration").style.display = "none";
});

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

var bt2 = document.getElementById('submit2')
var mfa = document.getElementById('mfa')
var token = document.getElementById('mfa_code')
var form = document.getElementById('aws_page_form')
bt2.onclick = function () {
if (mfa.checked == true){
  var code = prompt("Enter MFA token code", "");
  token.value = code;
  form.submit();
} else {
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

// Get the latest Sync Status data JSON data
$(function() {
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
        console.log("error: " + JSON.stringify(e));
      }
    });

  // populate the Sync Satus data table with JSON data
  function populateDataTable(data) {
    console.log("populating data table...");
    console.log("DATA:",data)
    $("#sync_table").DataTable().destroy();
    $("#sync_table").DataTable({
      paging: false,
      searching: false,
      info: false,
      autoWidth: false,
      processing: true,
      data: data,
      columns: [ { data: "Region"}, { data: "StartTime"}, { data: "Target"} ]
    }
  );
  }
});
