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

function get_service_url(row) {
    id = row.attr('id');
    return service_url + id.split('_')[1] + '/'
}

$(document).ready(function() {
    $("input,select").change(function() {
        row = $(this).parent().parent().parent();
        if (!row.hasClass('changed')) {
            row.addClass('changed');
        }
    });
    
    $(".button-edit").click(function() {
        switch_buttons($(this).parent());
        switch_values($(this).parent().parent());
    });
    
    $(".button-delete").click(function() {
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
    
    $(".button-save").click(function() {
        cell = $(this).parent();
        row = cell.parent()
        header_fields = row.parent().find('th.no-borders').find('input');
        form_fields = row.find('input,select').add(header_fields);
        
        if (row.hasClass('changed')) {
            $.post(get_service_url(row), form_fields.serialize())
                .error(function() {
                    row.find('.value-error').hide();
                    //TODO: display new errors
                })
                .success(function() {
                    row.find('.value-error').hide();
                    switch_buttons(cell);
                    switch_values(row);
                    update_values(row);
                });
        }
    });
    
    $(".button-cancel").click(function() {
        switch_buttons($(this).parent());
        switch_values($(this).parent().parent());
    });
    
    $(".button-add").click(function() {
        cell = $(this).parent();
        row = cell.parent()
        header_fields = row.parent().find('th.no-borders').find('input');
        form_fields = row.find('input,select').add(header_fields);
        $.post(service_url, form_fields.serialize(), function(data, textStatus, jqXHR){
            // append new row:
            row.before(data);
            // clear add-row
            row.html(row.next().html());
        }).error(function() {
            alert('error');
        })
    });
});