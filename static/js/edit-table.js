function switch_buttons(cell) {
    cell.find('.button-edit').toggle();
    cell.find('.button-delete').toggle();
    cell.find('.button-save').toggle();
    cell.find('.button-cancel').toggle();
}

function switch_values(row) {
    row.find('.value-display').toggle();
    row.find('.value-edit').toggle()
}

function get_service_id(row) {
    return row.attr('id').split('_')[1];
}

function get_service_url(row) {
    return service_url + get_service_id(row) + '/';
}

function edit_service(cell) {
    switch_buttons(cell);
    switch_values(cell.parent());
}

function set_datepicker(row) {
    id = get_service_id($(row));
    row.find('#id_' + id + '-launched').datepicker({
        dateFormat: "yy-mm-dd", maxDate: "+0D", showButtonPanel: true, changeYear: true
    });
}

function get_csrftoken() {
    return $(csrftoken).find('input');
}

var overlay_params = {
    top: 'relative',
    left: 'relative',
    closeOnClick: true,
    onBeforeLoad: function() {
        // grab wrapper element inside content
        var wrap = this.getOverlay().find(".contentWrap");

        // load the page specified in the trigger
        wrap.load(this.getTrigger().attr("href"));
    }
}

add_wkt = function(event) {
    map = this.map;
    feature = event.feature;
    feat = OpenLayers.Util.properFeatures(feature, this.options.geom_type);
    point = feat.geometry;
    //alert(point.x + ', ' + point.y);
    
    var lonlat = point.transform(map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
    //alert(lonlat.x + ", " + lonlat.y);
    
    // find: id_1-location (we have: id_1-osmlocation_map)
    input_id =         this.options.map_id.replace(/osmlocation_map/, 'location');
    document.getElementById(input_id).value = lonlat.x.toFixed(2) + ',' + lonlat.y.toFixed(2);
    input = $(document).find('#' + input_id);
    cell = input.parent().parent();
    row = cell.parent();
    if (!row.hasClass('changed')) {
        row.addClass('changed');
    }
}

$(document).ready(function() {
    $("a[rel]").overlay(overlay_params);
    
    $("table").on("change", "input,select", function() {
        row = $(this).parent().parent().parent();
        if (!row.hasClass('changed')) {
            row.addClass('changed');
        }
    });
    
    $("table").on("click", ".button-edit", function() {
        edit_service($(this).parent());
    });
    
    $("table").on("click", ".button-delete", function() {
        row = $(this).parent().parent();
        url = get_service_url(row);
        
	$.ajax({
            url: get_service_url(row),
            type: 'DELETE',
	    beforeSend: function(xhr) {
		xhr.setRequestHeader("X-CSRFToken", $(csrftoken).attr('value'));
	    },
            success: function() {
                row.hide(500);
            }
        })
    });
    
    $("table").on("click", ".button-save", function() {
        cell = $(this).parent();
        row = cell.parent()
        form_fields = row.find('input,select').add(get_csrftoken());
        
        if (row.hasClass('changed')) {
            $.post(get_service_url(row), form_fields.serialize(), function(data) {
                new_row = $(data);
                
                row.replaceWith(new_row);
                set_datepicker(new_row);
                new_row.find("a[rel]").overlay(overlay_params);
            })
        } else {
            edit_service(cell);
        }
    });
    
    $("table").on("click", ".button-cancel", function() {
        edit_service($(this).parent());
    });
    
    $("table").on("click", ".button-add", function() {
        cell = $(this).parent();
        row = cell.parent()
        form_fields = row.find('input,select').add(get_csrftoken());
    
        $.post(service_url, form_fields.serialize(), function(data) {        
            new_row = $(data);
            row.before(new_row); // append new row above
            set_datepicker(new_row); // set datepicker
            new_row.find("a[rel]").overlay(overlay_params);
            
            row.find("input").val(''); // clear input values of this row
            row.find(".fielderrors").html('');
        }).fail(function(data) {
            new_row = $(data.responseText);
            
            row.replaceWith(new_row);
            // set datepicker manually because we do not have an id here
            new_row.find('#id_launched').datepicker({
                dateFormat: "yy-mm-dd", maxDate: "+0D", showButtonPanel: true
            });
            new_row.find("a[rel]").overlay(overlay_params);
        })
    });
    
    // datepicker:
    $('tr[id^="server"]').each(function(index, row){
        set_datepicker($(row));
    });
    $('#id_launched').datepicker({
        dateFormat: "yy-mm-dd", maxDate: "+1D", showButtonPanel: true, changeYear: true
    });
});
