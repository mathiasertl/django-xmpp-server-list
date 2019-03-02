$(document).ready(function() {
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
});
