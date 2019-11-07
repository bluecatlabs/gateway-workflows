// Copyright 2019 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.

var red10 = ["#ff0000", "#e60000","#cc0000","#b30000","#990000","#800000","#660000","#4d0000","#330000","#1a0000"]
var blue10 = ["#4D9BE8", "#3C91E6","#3784D2","#3277BD","#2C6AA8","#275D93","#21507E","#1C4269","#163554","#11283F"]
var green10 = ["#00ff00", "#00e600","#00cc00","#00b300","#009900","#008000","#006600","#004d00","#003300","#001a00"]
var rainbow = ["#3366cc", "#dc3912","#ff9900","#109618","#990099","#0099c6","#DD4477","#66AA00","#B82E2E","#316395","#994499","#22AA99","#AAAA11","#6633CC"]

var barconfig = {
                  tooltips: {
                  mode: 'index',
                  },
                  responsive: true,
                  maintainAspectRatio: true,
                  layout: { padding: { left: 0, right: 40, top: 10, bottom: 50, } },
                  scales: { xAxes: [{ ticks: { beginAtZero:true }, stacked: true, }], yAxes: [{ ticks: { beginAtZero:true }, stacked: true, }]  },
                  legend: { display: false, position: "bottom" },
                  title: { display: false, text: 'BARCONFIG', },
};

Chart.defaults.global.defaultFontColor = "#0093b8";

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
    document.getElementById("purge_configuration").style.display = "none";

    // var panels = document.getElementById('panels')
    // var region = document.getElementById('aws_region_name').value
    // console.log(region)
    //
    // // Generate Panels for each discovery
    // let url = '/aws/discovery_stats';
    // fetch(url)
    // .then(res => res.json())
    // .then((out) => {
    //   if (out.length !== 0) {
    //   console.log("Found Prior Stats:",out)
    //   div = document.createElement( 'div' );
    //   div.innerHTML = "<div class='col disable-select'><h2>" + region + "</h2></div>" + "<canvas id='chart_panel_" +region+ "' width='800' height='450'></canvas><br>"
    //   panels.appendChild( div )
    //   var ctx = document.getElementById("chart_panel_"+region)
    //   console.log("Generated Chart_Panel: ",ctx)
    //   get_graph(region,out)
    //   }
    //   else {
    //   console.log("No prior discovery stats")
    //   }
    //
    // })
    // .catch(err => { throw err }
    // );
    //
    // async function get_graph(region,out) {
    //   var ctx = document.getElementById("chart_panel_"+region)
    //   console.log("Generated Chart_Panel in get_graph: ", ctx)
    //   console.log("get_graph data:",out)
    //   var labels = [];
    //   var counts = [];
    //   let x = "item." + region
    //   out.forEach(item => labels.push(item[region]))
    //   out.forEach(item => counts.push(item.count))
    //   var graphdata = {
    //     labels: labels,
    //     datasets: [
    //     {
    //       datalabels: {
    //       display: false
    //     },
    //     label: 'Object Count',
    //     data: counts,
    //     backgroundColor: rainbow,
    //   }],
    //   }
    //   console.log("Labels", labels)
    //   console.log("Counts", counts)
    //   var chart = new Chart(ctx, {type: 'bar', data: graphdata, options: barconfig});
    // }

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
  document.getElementById('submit2')
  if (!code) {
    return;
  };
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
      columns: [ { data: "Region"}, { data: "StartTime"}, { data: "Target"}, { data: "StateChanges"}, ]
    }
  );
  }
});

// Get the latest Sync Status data JSON data
$(function() {
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
        console.log("error: " + JSON.stringify(e));
      }
    });

  // populate the Sync Satus data table with JSON data
  function populateDataTable(data) {
    console.log("populating data table...");
    console.log("DATA:",data)
    $("#discovery_table").DataTable().destroy();
    $("#discovery_table").DataTable({
      paging: false,
      searching: false,
      info: false,
      autoWidth: false,
      processing: true,
      data: data,
      columns: [ { data: "Region"}, { data: "Time"}, { data: "Infrastructure"}, { data: "count"}, ]
    }
  );
  }
});
