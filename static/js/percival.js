api_version = '0.1';

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

$( document ).ready(function() {

    update_api_version();
    update_api_adapters();
    update_api_read_boards();
    update_api_read_controls();
    update_api_read_monitors();

//    get_led_states();
//   get_psu_states();

//    setInterval(update_api_sensors, 200);
});

function update_api_version() {

    $.getJSON('/api', function(response) {
        $('#api-version').html(response.api_version);
        api_version = response.api_version;
    });
}

function update_api_adapters() {

    $.getJSON('/api/' + api_version + '/adapters/', function(response) {
        adapter_list = response.adapters.join(", ");
        $('#api-adapters').html(adapter_list);
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

    $.getJSON('/api/' + api_version + '/percival/monitors/', function(response) {
        mon_list = response["monitors"];
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







