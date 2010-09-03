// SMI Javascript

$(document).ready(function() {
    var baseurl = $('#smi-content-url').attr('href');

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
    $(document).bind('zeam-popup-closed', function() {
        $.getJSON(baseurl + '/++rest++smi-feedback', function(data) {
            $('#feedback').replaceWith(data['messages']);
        });
    });
});
