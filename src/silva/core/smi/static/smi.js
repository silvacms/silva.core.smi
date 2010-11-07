// SMI Javascript

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

if ($.browser.msie) {
    // hack to prevent ie from reloading
    window.location.hash = window.location.hash;
}

function HashDispatcher(name) {
    this.name = name;
    this._matchRegexp = new RegExp("^#" + this.name + '/?');

    this.registerHooks = function() {
        // register as handler for hash changed
        var self = this;
        $(window).hashchange(function(){
            self.hashChanged()
        });
    };

    this.extractPath = function() {
        var hash = window.location.hash;
        if (hash.match(this._matchRegexp)) {
            return hash.replace(this._matchRegexp, '');
        }
        return '';
    };
};

function Browser(options){
    this.options = options || {};
    this.baseURL = window.location.href.replace(/\/edit.*/, '');
    this.browserURL = this.baseURL;

    this.getElement = function() {
        return $('#container-listing-main');
    };

    this.hashChanged = function() {
        this.path = this.extractPath();
        this.browserURL = this.baseURL + '/' + this.path;
        this.update();
    };

    this.update = function() {
        var self = this;
        var url = this.browserURL +
            '/edit/containerlisting?browse=' + this.path;
        $.ajax({settings: {ajaxSend: function(){}},
                url: url,
                dataType: 'html',
                success: function(data){
                    self.getElement().html(data);
                }
               });
    };

    this.rewriteURL = function(event) {
        var url = $(event.target).attr('href');
        var new_url = url.replace(this.baseURL, this.browserURL);
        window.location.href = new_url;
        return false;
    };

};

Browser.prototype = new HashDispatcher('browse');

if (window.location.href.match(/\/edit(#.*)?$/)) {
    var browser = new Browser();

    $(document).ready(function(){
        browser.registerHooks();
        browser.hashChanged();
    });

    $('.tabs a').live('click', function(event){
        return browser.rewriteURL(event);
    });
    $('.middleground a').live('click', function(event){
        return browser.rewriteURL(event);
    });
}
