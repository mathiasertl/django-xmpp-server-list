$(document).ready(function() {
    var server_moderate_row;

    /* Approve server */
    $('button.btn-approve').click(function(e) {
        var button = $(e.target);
        var tr = button.parents('tr');
        var url = tr.data('url');
        $.post(url, {
            moderate: true
        }, function(data) {
            tr.hide(500);
        });
    });

    /* Set server_moderate_row when modal is shown so we can access it later */
    $('#reject-modal').on('show.bs.modal', function(e) {
        var button = $(e.relatedTarget);
        server_moderate_row = button.parents('tr');
    });

    /* Remove any existing text from the reject message */
    $('#reject-modal').on('show.bs.modal', function(e) {
        $('#reject-message').val('');
    });

    /* Reject a server */
    $('button.btn-reject-modal').click(function(e) {
        var button = $(e.target);
        var message = $('#reject-message').val();
        var url = server_moderate_row.data('url')
        console.log(url);
        console.log(message);

        $.post(url, {
            moderate: false,
            message: message
        }, function(data) {
            server_moderate_row.hide(500);
            $('#reject-modal').modal('hide');
        });
    });
});
