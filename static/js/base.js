var register_popover = function() {
    $('.popover-field').popover({
        html: true,
        content: function() {
            var content = '';
            var url = $(this).attr('data-url');
            $.ajax({
                url: url,
                type: 'GET',
                async: false,
            }).done(function(result) {
                content = result;
            });
            return content;
        },
        container: 'body',
        placement: 'bottom',
    });
}
$(document).ready(function() {
    console.log('ready');
    $('.tooltip-field').tooltip({
        title: function() {
            var tip = $(this).attr('data-tip');
            console.log('#tooltip-' + tip);
            return $('body').find('#tooltip-' + tip).html();
        },
        placement: 'bottom',
        container: 'body',
        html: true,
    });
    
    register_popover();
});
