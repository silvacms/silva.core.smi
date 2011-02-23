$(document).ready(function(){
    $.each($('div.widget-crop'), function(index, w) {
        var widget = $(w);
        var popupButton = $('a.widget-crop-popup-button', widget);

        popupButton.button(
            {icons: {primary: 'ui-icon ui-icon-carat-1-sw'}});

        var popup = $('div.widget-crop-popup', widget);
        var img = $('img.widget-crop-image', popup);

        popup.dialog({
            modal: true,
            autoOpen: false,
            buttons: {
                'ok': function(){ 
                    var c = img.data('crop');
                    if (c !== undefined) {
                        $('input', widget).val(
                            c.x + 'x' + c.y + '-' + c.x2 + 'x' + c.y2);
                        popup.dialog('close');
                    }
                },
                'cancel': function(){ popup.dialog('close'); }
            }
        });

        popupButton.bind('click', function(event){
            img.Jcrop({
                onSelect: function(c){
                    img.data('crop', c);
                },
                onChange: function(c){
                    img.data('crop', c);
                }
            });
            popup.dialog('open');
        });
    });
});