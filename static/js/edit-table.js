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

function update_values(row) {
    row.find('td').each(function(index) {
        td = $(this);
        $(this).find('input').each(function(index) {
            value = $(this).val();
            name = $(this).attr('name');
            if (td.hasClass('multivalue')) {
                td.find('.value-display .' + name).html(value);
            } else {
                td.find('.value-display.' + name).html(value);
            }
        });
        $(this).find('select').each(function(index) {
            value = $(this).find('option:selected').text();
            name = $(this).attr('name');
            td.find('.value-display.' + name).html(value);
        });
    });
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
                row.replaceWith(data);
            })
/*
                .error(function(dataTypeExpression) {
                    row.find('.value-error').hide();
                    alert(data);
                    //TODO: display new errors
                })
                .success(function() {
                    row.find('.value-error').hide();
                    switch_buttons(cell);
                    switch_values(row);
                    update_values(row);
                });
*/
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
            
            // append new row:
            row.before(new_row);
            
            // set datepicker:
            new_id = get_service_id(new_row);
            new_row.find('#id_' + new_id + '-launched').datepicker({
                dateFormat: "yy-mm-dd", maxDate: "+1D", showButtonPanel: true
            }); 
            
            
            // clear add-row
            row.html(row.next().html());
        }).error(function() {
            alert('error');
        })
    });
    
    // datepicker:
    $('.your-servers tr[id^="server"]').each(function(index, row){
        row = $(row);
        id = get_service_id($(row));
        row.find('#id_' + id + '-launched').datepicker({
            dateFormat: "yy-mm-dd", maxDate: "+1D", showButtonPanel: true
        }); 
    });
});