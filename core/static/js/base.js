/**
 * Setup ajax requests to use the CSRF token
 */

// get the token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// setup ajax
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

/*
 * Currently unused
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
*/

$(document).ready(function() {
    //register_tooltips();
    //register_popover();

    /* Currently unused
    $(".button-ok").on("click", function() {
        url = $(this).parent().attr('data-url');
        row = $(this).parent().parent();
        $.post(url, {moderate: true, csrfmiddlewaretoken: csrftoken}, function(data) {
            row.hide(500);
        });
    });
    */
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
