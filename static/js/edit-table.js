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

$(document).ready(function() {
    $("table").on("change", "input,select", function() {
        row = $(this).parent().parent().parent();
        if (!row.hasClass('changed')) {
            row.addClass('changed');
        }
    });
    
    $("table").on("click", ".button-edit", function() {
        switch_buttons($(this).parent());
        switch_values($(this).parent().parent());
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
            })
        } else {
            switch_buttons(cell);
            switch_values(row);
        }
    });
    
    $("table").on("click", ".button-cancel", function() {
        switch_buttons($(this).parent());
        switch_values($(this).parent().parent());
    });
    
    $(".button-add").click(function() {
        cell = $(this).parent();
        row = cell.parent()
        header_fields = row.parent().find('th.no-borders').find('input');
        form_fields = row.find('input,select').add(header_fields);
    
        $.post(service_url, form_fields.serialize(), function(data, textStatus, jqXHR) {        
            new_row = $(data);
            row.before(new_row); // append new row above
            set_datepicker(new_row); // set datepicker
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