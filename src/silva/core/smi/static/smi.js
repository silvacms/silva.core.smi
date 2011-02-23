// SMI Javascript

// Add a rescope method
if (Function.prototype.scope === undefined) {
    Function.prototype.scope = function(scope) {
        var _function = this;

        return function() {
            return _function.apply(scope, arguments);
        };
    };
}


$(document).ready(function() {
    var base_url = $('#smi-content-url').attr('href');

    // Add new content auto submit
    $('#md-container-field-content').bind('change', function() {
        // Fill in the add in position field if possible
        var form = $('form[name=silvaObjects]');
        if (form) {
            var position = form.find('input[name=ids:list]:checked');
            if (position.length == 1) {
                var label = $('label[for=' + position.attr('id') + ']').text();
                $('#md-container-field-position').val(
                    label.replace(/^[^\d]*(\d*).*$/g, '$1'));
            };
        }
        $('#md-container-action-new').trigger('click');
    });
    // Update feedback status
    $(document).bind('smi-refresh-feedback', function() {
        $.getJSON(base_url + '/++rest++smi-feedback', function(data) {
            $('#feedback').replaceWith(data['messages']);
        });
    });
    // Add a loading message on server request
    var request_count = 0;
    var load_message = $('div#remote-request-loading');
    if (load_message) {
        $(document).ajaxSend(function() {
            if (!request_count) {
                load_message.fadeIn('fast');
            };
            request_count += 1;
        });
        $(document).ajaxComplete(function() {
            request_count -= 1;
            if (!request_count) {
                load_message.fadeOut('fast');
            };
        });
    };
});
