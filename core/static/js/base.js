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
var register_tooltips = function(){
    $('.tooltip-field').tooltip({
        title: function() {
            var tip = $(this).attr('data-tip');
            return $('body').find('#tooltip-' + tip).html();
        },
        placement: 'bottom',
        container: 'body',
        html: true,
    });
}

$(document).ready(function() {
    register_tooltips();
    register_popover();

    $('.fblike').on('click', function(event) {
        fblike_button();
    });

    $(".button-ok").on("click", function() {
        url = $(this).parent().attr('data-url');
        row = $(this).parent().parent();
        $.post(url, {moderate: true, csrfmiddlewaretoken: csrftoken}, function(data) {
            row.hide(500);
        });
    });
    $("#moderationModal").on("show.bs.modal", function(event) {
        var button = $(event.relatedTarget);
        url = button.parent().data('url');
        row = button.parent().parent();
        
        // Set initial modal state:
        var modal = $(this);
        modal.data('url', url);
        modal.find('textarea').val('');
    })

    $('#moderationModal #deny-moderation').on('click', function(event) {
        var modal = $('#moderationModal');
        var url = modal.data('url');
        var message = $('#moderationModal #denial-message').val();
        modal.modal('hide');

        $.post(url, {
            moderate: false,
            csrfmiddlewaretoken: csrftoken,
            message: message,
        }, function(data) {
            row.hide(500);
        });
    });
});

// Generate a two-click like button.
// Shamelessly stolen from here: http://turkeyland.net/projects/two-click/
var fblike_button = function() {
    // Generate a string containing the HTML to place in the element (for readability)
    var html = "<div id=\"fb-root\">\n";
    html += "<div class=\"fb-like\" data-href=\"https://facebook.com/jabber.at\" data-send=\"true\" data-layout=\"button_count\" data-width=\"100\" data-show-faces=\"false\" data-font=\"arial\">\n";
    html += "</div>\n";

    // Replace the specified element's contents with the HTML necessary to display the
    // Like/+1 Buttons, *before* loading the SDKs below
    $('.fblike').html(html);

    // This is the code provided by facebook to asynchronously load their SDK
    var e = document.createElement('script'); e.async = true;
    e.src = document.location.protocol +
      '//connect.facebook.net/en_US/all.js#xfbml=1';
    document.getElementById('fb-root').appendChild(e);
}
