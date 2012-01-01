function switch_buttons(cell) {
    cell.find('.button-edit').toggle();
    cell.find('.button-delete').toggle();
    cell.find('.button-save').toggle();
    cell.find('.button-cancel').toggle();
}

function get_service_url(row) {
    id = row.attr('id');
    return service_url + id.split('_')[1] + '/'
}

$(document).ready(function() {
    $(".button-edit").click(function() {
        switch_buttons($(this).parent());
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
        switch_buttons($(this).parent());
    });
    $(".button-cancel").click(function() {
        switch_buttons($(this).parent());
    });
});