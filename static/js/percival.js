api_version = '0.1';
monitor_names = [];
current_page = "configuration-view";

percival = {
  api_version: '0.1',
  current_page: '.home-view',
  monitors: {}
  };


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
    this.id = id;
    this.device = device.device;
    this.unit = device.unit;
    this.low_threshold = device.low_threshold;
    this.extreme_low_threshold = device.extreme_low_threshold;
    this.high_threshold = device.high_threshold;
    this.extreme_high_threshold = device.extreme_high_threshold;
    this.safety_exception = device.safety_exception;
    this.i2c_comms_error = device.i2c_comms_error;
    this.value = 0.0;
    this.html_text = "<div class=\"panel-heading clearfix\">" +
                     "<span class=\"panel-title pull-left\">" + this.id + "</span>" +
                     "<button type=\"button\" id=\"" + this.id +
                     "-expbtn\" class=\"btn btn-outline-info btn-sm pull-right float-align-vertical\">" +
                     "<span id=\"" + this.id + "-expglp\" class=\"glyphicon glyphicon-resize-full\"></span></button></div>" +
                     "<table>" + 
                     "<tr><td width=120px>Device:</td><td colspan=2 width=150px>" + this.device + "</td></tr>";
    if (this.device == "LTC2309"){
      this.html_text += "<tr><td>Voltage:</td><td colspan=2 id=\"" + this.id + "-value\">0.000 ";
    } else if (this.device == "MAX31730"){
      this.html_text += "<tr><td>Temperature:</td><td colspan=2 id=\"" + this.id + "-value\">0.000 ";            
    }
    this.html_text += this.unit + "</td></tr></table>";
    this.html_text += "<table id=\"" + this.id + "-dtbl\">";
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
  
  update(device)
  {
    if (this.device == "LTC2309"){
      if (this.value != device.voltage){
        this.update_value(device.voltage);
        this.update_high(device.extreme_high_threshold);
      }
    } else if (this.device == "MAX31730"){
      if (this.value != device.temperature){
        this.update_value(device.temperature);
      }
    }    
  }
  
  update_value(value)
  {
    $('#' + this.id + '-value').html("" + parseFloat(value).toFixed(3));
    this.value = value;
  }

  update_high(value)
  {
    $('#' + this.id + '-hihi').html(led_html(parseInt(value), "red", 25));
    this.extreme_high_threshold = value;
    if (value == 1){
        $(this.parent).removeClass("panel-default");
        $(this.parent).removeClass("panel-warning");
        $(this.parent).addClass("panel-danger");
    }
  }
}

$( document ).ready(function() 
{
  update_api_version();
  update_api_adapters();
  update_server_setup();
  render('#/home-view');
  
  setInterval(update_api_read_status, 100);

  $(window).on('hashchange', function(){
		// On every hash change the render function is called with the new hash.
		// This is how the navigation of the app is executed.
		render(decodeURI(window.location.hash));
	});
});

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
    $.getJSON('/api/' + api_version + '/percival/setup/', function(response) {
        $('#server-start-time').html(response.start_time);
        $('#server-username').html(response.username);
        alert(response.start_time);
    });
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
        var tableData = [];
        for (var index = 0; index < len; index++){
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

function update_api_read_monitors() {
//alert("Here");
    $.getJSON('/api/' + api_version + '/percival/monitors/', function(response) {
        mon_list = response["monitors"];
        monitor_names = mon_list;
        //$('#overall-monitors').html("");
        $('#overall-monitors').tabulator({height:"220px",
                                          pagination:"local",
                                          columns:[
                                          {title:"Name", field:"name", sorter:"string", width:"50%"},
                                          {title:"Type", field:"type", sorter:"string", width:"50%"}
                                          ]
                                        });
        var len = mon_list.length;
        var tableData = [];
        for (var index = 0; index < len; index++){
          tableData[index] = { id: index, 
                               name:mon_list[index],
                               type:response[mon_list[index]] };
        }
        $('#overall-monitors').tabulator("setData", tableData);
    });
}

function update_api_read_status() 
{
  $.getJSON('/api/' + api_version + '/percival/status/', function(response) {
    var len = monitor_names.length;
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
    update_api_read_monitors();
  }    		
}


