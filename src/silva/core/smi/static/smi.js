// SMI Javascript

$(document).ready(function() {
    // Add new content auto submit
    $('#md-container-field-content').bind('change', function() {
        $('#md-container-action-new').trigger('click');
    });
});
