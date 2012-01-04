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
        dateFormat: "yy-mm-dd", maxDate: "+0D", showButtonPanel: true
    }); 
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
    alert(point.x + ', ' + point.y);
    
    var lonlat = point.transform(map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
    alert(lonlat.lon + ", " + lonlat.lat);
}

$(document).ready(function() {
    map_1_location.layers.vector.events.on({'featureadded': add_wkt, scope: map_1_location});
/*    $(".olMap").click(function() {
        loc = map_1_location;
        map = loc.map;
        opt = loc.options
        
//        alert('fuck:' + loc.get_ewkt);
        wkt = document.getElementById(opt.id).value;
        alert(wkt);
        
//        sanitized = loc.read_wkt(wkt);
//        alert(sanitized);
    });
*/
    
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
            success: function() {
                row.hide(500);
            }
        })
    });
    
    $("table").on("click", ".button-save", function() {
        cell = $(this).parent();
        row = cell.parent()
        header_fields = row.parent().find('th.no-borders').find('input');
        form_fields = row.find('input,select').add(header_fields);
        
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
    
    $(".button-add").click(function() {
        cell = $(this).parent();
        row = cell.parent()
        header_fields = row.parent().find('th.no-borders').find('input');
        form_fields = row.find('input,select').add(header_fields);
    
        $.post(service_url, form_fields.serialize(), function(data) {        
            new_row = $(data);
            row.before(new_row); // append new row above
            set_datepicker(new_row); // set datepicker
            new_row.find("a[rel]").overlay(overlay_params);
            
            row.find("input").val(''); // clear input values of this row
        }).error(function() {
            alert('error');
        })
    });
    
    // datepicker:
    $('.your-servers tr[id^="server"]').each(function(index, row){
        set_datepicker($(row));
    });
    $('#id_launched').datepicker({
        dateFormat: "yy-mm-dd", maxDate: "+1D", showButtonPanel: true
    });
});