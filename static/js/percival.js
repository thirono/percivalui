api_version = '0.1';
monitor_names = [];
monitor_desc = {};
current_page = "configuration-view";

percival = {
  api_version: '0.1',
  current_page: '.home-view',
  monitors: {},
  monitor_count: 0,
  monitor_divs: 0,
  groups: {},
  control_names: []
  };

$.put = function(url, data, callback, type)
{
  if ( $.isFunction(data) ){
    type = type || callback,
    callback = data,
    data = {}
  }

  return $.ajax({
    url: url,
    type: 'PUT',
    success: callback,
    data: data,
    contentType: type
  });
}

class ProgressBar
{
	constructor(id, labelId, units)
	{
		this.elem = $('#' + id);
		this.label = $('#' + labelId);
		this.units = units;
	}

	update(val)
	{
		var min = parseInt(this.elem.attr("aria-valuemin"));
		var max = parseInt(this.elem.attr("aria-valuemax"));
		
		var adjusted;
		if(val < min)
			adjusted = min;
		else if(val > max)
			adjusted = max;
		else
			adjusted = (val - min) / max * 100;

		this.elem.css("width", adjusted + "%");
		this.label.html(Math.round(val * 100) / 100 + this.units);
	}
}

class Monitor
{
  constructor(parent, id, device)
  {
    this.parent = parent;
    this.disp_name = id;
    this.id = id.split(' ').join('_');
    this.device = device.device;
    this.unit = device.unit;
    this.low_threshold = device.low_threshold;
    this.extreme_low_threshold = device.extreme_low_threshold;
    this.high_threshold = device.high_threshold;
    this.extreme_high_threshold = device.extreme_high_threshold;
    this.safety_exception = device.safety_exception;
    this.i2c_comms_error = device.i2c_comms_error;
    this.value = 0.0;
    this.raw_value = 0;
    this.sample_number = 0;
    this.html_text = "<div class=\"panel-heading clearfix\">" +
                     "<span class=\"panel-title pull-left\">" + this.disp_name + " [" + this.device +
                     "]</span>" +
                     "<button type=\"button\" id=\"" + this.id +
                     "-expbtn\" class=\"btn btn-outline-info btn-sm pull-right float-align-vertical\">" +
                     "<span id=\"" + this.id + "-expglp\" class=\"glyphicon glyphicon-resize-full\"></span></button></div>" +
                     "<table>";
                     //"<tr><td width=120px>Device:</td><td colspan=2 width=150px>" + this.device + "</td></tr>";
    if (this.device == "LTC2309"){
      this.html_text += "<tr><td width=120px>Voltage:</td><td colspan=2 id=\"" + this.id + "-value\">0.000 ";
    } else if (this.device == "MAX31730"){
      this.html_text += "<tr><td width=120px>Temperature:</td><td colspan=2 id=\"" + this.id + "-value\">0.000 ";
    }
    this.html_text += this.unit + "</td></tr></table>";
    this.html_text += "<table id=\"" + this.id + "-dtbl\">";
    this.html_text += "<tr><td width=120px>Raw Value:</td><td colspan=2 id=\"" + this.id + "-raw\">0</td></tr>";
    this.html_text += "<tr><td width=120px>Sample Number:</td><td colspan=2 id=\"" + this.id + "-sample\">0</td></tr>";
    this.html_text += "<tr><td width=120px></td><td width=75px>Warn</td><td width=75px>Error</td></tr>";
    this.html_text += "<tr><td>Low:</td><td id=\"" + this.id + "-low\">" + led_html(parseInt(device.low_threshold), "yellow", 25) + "</td>" +
                      "<td id=\"" + this.id + "-lolo\">" + led_html(parseInt(device.extreme_low_threshold), "red", 25) + "</td></tr>" + 
                      "<tr><td>High:</td><td id=\"" + this.id + "-high\">" + led_html(parseInt(device.high_threshold), "yellow", 25) + "</td>" + 
                      "<td id=\"" + this.id + "-hihi\">" + led_html(parseInt(device.extreme_high_threshold), "red", 25) + "</td></tr>" + 
                      "<tr><td>Safety Exception:</td><td></td><td id=\"" + this.id + "-safety\">" + led_html(parseInt(device.safety_exception), "red", 25) + "</td>" +
                      "<tr><td>i2c Error:</td><td></td><td id=\"" + this.id + "-i2c\">" + led_html(parseInt(device.i2c_comms_error), "red", 25) + "</td>" +
                      "</table>";
    $(this.parent).html(this.html_text);
    $('#' + this.id + '-dtbl').hide();
    $('#' + this.id + '-expbtn').click(function(){
        //alert("Clicked!! " + $(this).attr("id"));
        if ($('#' + $(this).attr("id").replace('-expbtn', '-dtbl')).is(':visible')){
            $('#' + $(this).attr("id").replace('-expbtn', '-dtbl')).hide();
            $('#' + $(this).attr("id").replace('-expbtn', '-expglp')).removeClass('glyphicon-resize-small');
            $('#' + $(this).attr("id").replace('-expbtn', '-expglp')).addClass('glyphicon-resize-full');
        } else {
            $('#' + $(this).attr("id").replace('-expbtn', '-dtbl')).show();
            $('#' + $(this).attr("id").replace('-expbtn', '-expglp')).removeClass('glyphicon-resize-full');
            $('#' + $(this).attr("id").replace('-expbtn', '-expglp')).addClass('glyphicon-resize-small');
        }
    });
    this.update(device);
  }

  hide()
  {
    $(this.parent).hide();
  }

  show()
  {
    $(this.parent).insertAfter('#status-anchor');
    $(this.parent).show();
  }

  update(device)
  {
    if (this.device == "LTC2309"){
      if (this.value != device.voltage){
        this.update_value(device.voltage);
      }
    } else if (this.device == "MAX31730"){
      if (this.value != device.temperature){
        this.update_value(device.temperature);
      }
    }
    if (this.raw_value != device.raw_value){
      this.update_raw_value(device.raw_value);
    }
    if (this.sample_number != device.sample_number){
      this.update_sample_number(device.sample_number);
    }
    this.update_warnings(device.low_threshold, device.high_threshold);
    this.update_errors(device.extreme_low_threshold,
                       device.extreme_high_threshold,
                       device.safety_exception,
                       device.i2c_comms_error);
  }
  
  update_raw_value(value)
  {
    $('#' + this.id + '-raw').html("" + parseInt(value));
    this.raw_value = value;
  }

  update_sample_number(value)
  {
    $('#' + this.id + '-sample').html("" + parseInt(value));
    this.sample_number = value;
  }

  update_value(value)
  {
    $('#' + this.id + '-value').html("" + parseFloat(value).toFixed(3) + " " + this.unit);
    this.value = value;
  }

  update_warnings(low_val, high_val)
  {
    $('#' + this.id + '-low').html(led_html(parseInt(low_val), "yellow", 25));
    $('#' + this.id + '-high').html(led_html(parseInt(high_val), "yellow", 25));
    this.high_threshold = high_val;
    this.low_threshold = low_val;
    if (high_val == 1 || low_val == 1){
        $(this.parent).addClass("panel-warning");
    } else {
        $(this.parent).removeClass("panel-warning");
    }
  }

  update_errors(lolo_val, hihi_val, safety, comms)
  {
    $('#' + this.id + '-hihi').html(led_html(parseInt(hihi_val), "red", 25));
    $('#' + this.id + '-lolo').html(led_html(parseInt(lolo_val), "red", 25));
    $('#' + this.id + '-safety').html(led_html(parseInt(safety), "red", 25));
    $('#' + this.id + '-i2c').html(led_html(parseInt(comms), "red", 25));
    this.extreme_high_threshold = hihi_val;
    this.extreme_low_threshold = lolo_val;
    this.safety_exception = safety;
    this.i2c_comms_error = comms;
    if (hihi_val == 1 || lolo_val == 1 || safety == 1 || comms == 1){
        $(this.parent).addClass("panel-danger");
    } else {
        $(this.parent).removeClass("panel-danger");
    }
  }
}

$( document ).ready(function() 
{
  update_api_version();
  update_api_adapters();
  update_server_setup();
  render('#/home-view');

  setInterval(update_server_setup, 1000);
  setInterval(update_api_read_monitors, 1000);
  setInterval(update_api_read_status, 100);

  $('#server-db-reconnect').click(function(){
    reconnect_db();
  });
  $('#server-ar-start').click(function(){
    auto_read('start');
  });
  $('#server-ar-stop').click(function(){
    auto_read('stop');
  });

  $(window).on('hashchange', function(){
		// On every hash change the render function is called with the new hash.
		// This is how the navigation of the app is executed.
		render(decodeURI(window.location.hash));
	});
});

function reconnect_db()
{
    $.put('/api/' + api_version + '/percival/influxdb/connect', function(response){});
}

function auto_read(action)
{
    $.put('/api/' + api_version + '/percival/auto_read/' + action, function(response){});
}

function update_api_version() {

    $.getJSON('/api', function(response) {
        $('#api-version').html(response.api_version);
        percival.api_version = response.api_version;
    });
}

function update_api_adapters() {
//alert("HERE");
    $.getJSON('/api/' + api_version + '/adapters/', function(response) {
        adapter_list = response.adapters.join(", ");
        $('#api-adapters').html(adapter_list);
        //alert(adapter_list);
    });
}

function update_server_setup() {
    $.getJSON('/api/' + api_version + '/percival/driver/', function(response) {
        $('#server-start-time').html(response.start_time);
        $('#server-up-time').html(response.up_time);
        $('#server-username').html(response.username);
        $('#server-db-address').html(response.influx_db.address);
        $('#server-db-port').html(response.influx_db.port);
        $('#server-db-name').html(response.influx_db.name);
        if (response.influx_db.connected){
            connected = 1;
            $('#server-db-reconnect').hide();
            $('#server-db-connected').html(led_html(1, "green", 25));
        } else {
            connected = 0;
            $('#server-db-reconnect').show();
            $('#server-db-connected').html(led_html(1, "red", 25));
        }
        $('#server-hw-address').html(response.hardware.address);
        $('#server-hw-port').html(response.hardware.port);
        if (response.hardware.connected){
            connected = 1;
            $('#server-hw-reconnect').hide();
            $('#server-hw-connected').html(led_html(1, "green", 25));
        } else {
            connected = 0;
            $('#server-hw-reconnect').show();
            $('#server-hw-connected').html(led_html(1, "red", 25));
        }
        if (response.auto_read){
            $('#server-ar-start').hide();
            $('#server-ar-stop').show();
            $('#server-ar-status').html(led_html(1, "green", 25));
        } else {
            $('#server-ar-start').show();
            $('#server-ar-stop').hide();
            $('#server-ar-status').html(led_html(1, "red", 25));
        }
    });
    $.getJSON('/api/' + api_version + '/percival/groups/', function(response) {
        percival.groups = response

        // Group list
        mg = percival.groups.monitor_groups.group_names;
        html = "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" href=\"#/status-view\" onclick=\"update_visible_monitors('All')\">All</a></li>";
        for (var index=0; index < mg.length; index++){
            html += "<li role=\"presentation\"><a role=\"menuitem\" tabindex=\"-1\" href=\"#/status-view\" onclick=\"update_visible_monitors('"+mg[index]+"')\">"+mg[index]+"</a></li>";
        }
        $('#status-group').html(html);
        //alert(JSON.stringify(response));

        // Control channels for manual set points
        cg = percival.groups.control_groups.group_names.concat(percival.control_names);
		html = "";
		for (var index=0; index < cg.length; index++){
            html += "<option role=\"presentation\">" + cg[index] + "</option>";
        }
        if (html != $('#control-set-channel').html()){
            $('#control-set-channel').html(html);
        }
    });
}

function update_visible_monitors(group)
{
    $('#status-group-name').text("Channels [ " + group + " ] ");

    var mon_length = monitor_names.length;
    //alert(mon_length);
    for (var index = 0; index < mon_length; index++){
        if (group == "All"){
            percival.monitors[monitor_names[index]].show();
        } else {

            percival.monitors[monitor_names[index]].hide();
        }
    }

    if (group != "All"){
        var monitors = percival.groups.monitor_groups[group].channels;
        for (var index = 0; index < monitors.length; index++){
            percival.monitors[monitors[index]].show();
        }
    }
}

function update_api_read_boards() {

    $.getJSON('/api/' + api_version + '/percival/boards/', function(response) {
        board_list = response["boards"];
        $('#overall-boards').tabulator({columns:[
                                          {title:"Name", field:"name", sorter:"string", width:"50%"},
                                          {title:"Type", field:"type", sorter:"string", width:"20%"},
                                          {title:"Controls", field:"controls", sorter:"number", width:"15%"},
                                          {title:"Monitors", field:"monitors", sorter:"number", width:"15%"}
                                          ]
                                        });
        var len = board_list.length;
        var monitor_count = 0;
        var tableData = [];
        for (var index = 0; index < len; index++){
            monitor_count += response[board_list[index]].monitors_count;
            tableData[index] = { id: index,
                               name:response[board_list[index]].name,
                               type:response[board_list[index]].type,
                               controls:response[board_list[index]].controls_count,
                               monitors:response[board_list[index]].monitors_count };
            }
        $('#overall-boards').tabulator("setData", tableData);
    });
}

function update_api_read_controls() {

    $.getJSON('/api/' + api_version + '/percival/controls/', function(response) {
        percival.control_names = response["controls"];
        ctrl_list = response["controls"];
        $('#overall-controls').tabulator({height:"220px",
                                          pagination:"local",
                                          columns:[
                                          {title:"Name", field:"name", sorter:"string", width:"50%"},
                                          {title:"Type", field:"type", sorter:"string", width:"50%"}
                                          ]
                                        });
        var len = ctrl_list.length;
        var tableData = [];
        for (var index = 0; index < len; index++){
          tableData[index] = { id: index, 
                               name:ctrl_list[index],
                               type:response[ctrl_list[index]] };
        }
        $('#overall-controls').tabulator("setData", tableData);
    });
}

function update_api_read_monitors()
{
    $.getJSON('/api/' + api_version + '/percival/monitors/', function(response) {
        monitor_names = response["monitors"];
        monitor_desc = response;
        percival.monitor_count = monitor_names.length;
    });
}

function render_config_view()
{
    //$('#overall-monitors').html("");
    $('#overall-monitors').tabulator({height:"220px",
                                      pagination:"local",
                                      columns:[
                                      {title:"Name", field:"name", sorter:"string", width:"50%"},
                                      {title:"Type", field:"type", sorter:"string", width:"50%"}
                                      ]
                                    });
    var len = monitor_names.length;
    var tableData = [];
    for (var index = 0; index < len; index++){
        tableData[index] = { id: index,
                             name:monitor_names[index],
                             type:monitor_desc[monitor_names[index]] };
    }
    $('#overall-monitors').tabulator("setData", tableData);
}

function update_api_read_status()
{
  $.getJSON('/api/' + api_version + '/percival/status/', function(response) {
    var len = monitor_names.length;
    render_status_view();
    var tableData = [];
    for (var index = 0; index < len; index++){
      if (percival.monitors[monitor_names[index]] == null){
        percival.monitors[monitor_names[index]] = new Monitor('#stat-' + (index+1), monitor_names[index], response[monitor_names[index]]);
      } else {
        percival.monitors[monitor_names[index]].update(response[monitor_names[index]]);
      }
    }
  });
}

function led_html(value, colour, width)
{
  var html_text = "<img width=" + width + "px src=img/";
  if (value == 0){
    html_text += "led-off";
  } else {
    html_text +=  colour + "-led-on";
  }
  html_text += ".png></img>";
  return html_text;
}


function render(url) 
{
  // This function decides what type of page to show 
  // depending on the current url hash value.
  // Get the keyword from the url.
  var temp = "." + url.split('/')[1];
  // Hide whatever page is currently shown.
  $(".page").hide();
		
  // Show the new page
  $(temp).show();
  current_page = temp;
    
  if (temp == ".home-view"){
    update_api_version();
    update_api_adapters();
  } else if (temp == ".configuration-view"){
    // Re-request the configuration
    update_api_read_boards();
    update_api_read_controls();
    render_config_view();
  }
}

function render_status_view()
{
    // Check if the number of monitors has increased past the number of holder divs
    if (percival.monitor_count > percival.monitor_divs){
        // Calculate the number of new rows
        var new_count = percival.monitor_count - percival.monitor_divs;
        //alert("New rows: " + new_row_count);
        for (var index = percival.monitor_divs; index < (percival.monitor_divs+new_count); index++){
            //html_text = "<div class=\"row sidebar-row vertical-align\"><div class=\"col-xs-1\">&nbsp;</div>";
            html_text = "";
                html_text += "<div id=\"stat-" + (index+1) +
                             "\" class=\"col-xs-3 status vertical-align panel panel-default\">&nbsp;</div>";
            //}
            //html_text += "</div>";
            //alert(html_text);
            // Append the rows to the container
            $('#stat-container').append(html_text);
        }
        percival.monitor_divs += new_count;
    }
}
