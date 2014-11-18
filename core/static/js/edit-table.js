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
    return row.attr('data-server');
}

function edit_service(cell) {
    switch_buttons(cell);
    switch_values(cell.parent());
}

function resend_service_notification(row) {
    data = {
        pk: get_service_id(row),
        csrfmiddlewaretoken: csrftoken,
    }
    $.post(resend_url, data, function(data) {});
}

function set_datepicker(row) {
    id = get_service_id($(row));
    row.find('#id_' + id + '-launched').datepicker({
        dateFormat: "yy-mm-dd", maxDate: "+0D", showButtonPanel: true, changeYear: true
    });
}

function get_csrftoken() {
    return $(csrfinput);
}

$(document).ready(function() {
    $("table").on("change", "input,select", function() {
        row = $(this).parent().parent().parent();
        if (!row.hasClass('changed')) {
            row.addClass('changed');
        }
    });
    
    $("table").on("click", ".button-edit", function() {
        edit_service($(this).parent());
    });

    $("table").on("click", ".button-resend", function() {
        resend_service_notification($(this).parent().parent());
    });
    
    /**
     * Delete a server.
     */
    $("table").on("click", ".button-delete", function() {
        var self = $(this);
        url = self.attr('data-url');

        $.ajax({
            url: url,
            type: 'DELETE',
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function() {
                self.parent().parent().hide(500);
            }
        })
    });
    
    /**
     * Submit an edited server.
     */
    $("table").on("click", ".button-save", function() {
        cell = $(this).parent();
        row = cell.parent()
        form_fields = row.find('input,select').add(get_csrftoken());
        
        if (row.hasClass('changed')) {
            $.post(row.attr('data-update-url'), form_fields.serialize(), function(data) {
                new_row = $(data);
                
                row.replaceWith(new_row);
                set_datepicker(new_row);
                register_popover();
                register_tooltips();
            })
        } else {
            edit_service(cell);
        }
    });
    
    /**
     * Cancel editing a server.
     */
    $("table").on("click", ".button-cancel", function() {
        edit_service($(this).parent());
    });
    
    /**
     * Add a new server.
     */
    $("table").on("click", ".button-add", function() {
        row = $(this).parent().parent();
        form_fields = row.find('input,select').add(get_csrftoken());
    
        $.post(row.attr('data-url'), form_fields.serialize(), function(data) {
            new_row = $(data);
            row.replaceWith(new_row);
            new_row.find('#id_launched').datepicker({
                dateFormat: "yy-mm-dd", maxDate: "+0D", showButtonPanel: true
            });

            register_tooltips();
            register_popover();
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
