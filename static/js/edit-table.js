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

function get_service_url(row) {
    id = row.attr('id');
    return service_url + id.split('_')[1] + '/'
}

$(document).ready(function() {
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
        switch_buttons(cell);
        switch_values(row);
        header_fields = row.parent().find('th.no-borders').find('input');
        form_fields = row.find('input,select').add(header_fields);
//        alert(form_fields.serialize());
        
        $.post(get_service_url(row), form_fields.serialize())
            .error(function() {
                // called on error.
            })
            .success(function() {
                row.find('.value-error').hide();
            });
    });
    
    $(".button-cancel").click(function() {
        switch_buttons($(this).parent());
        switch_values($(this).parent().parent());
    });
});