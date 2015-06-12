define([
    'jquery', 'underscore', 'icons',  'schema'
], function($, _, icons, schema) {
    "use strict";

    function getToken(settings, filename) {
        return settings.token_required_for_get ?
                    $.get('/attachment_gw/get_token/', { filename: filename })
                    : $.when(null);
    }


    function SpecifyAttachments(settings) {
        this.settings = settings;
    }

    _(SpecifyAttachments.prototype).extend({
        thumbnailable: ['image/jpeg', 'image/gif', 'image/png', 'image/tiff', 'application/pdf'],

        iconForMimeType: function(mimetype) {
            var iconName;

            if (mimetype === 'text/plain') return icons.getIcon('text');
            if (mimetype === 'text/html') return icons.getIcon('html');

            var parts = mimetype.split('/');
            var type = parts[0], subtype = parts[1];

            if (_("audio video image text".split()).contains(type)) {
                return icons.getIcon(type);
            }

            if (type === 'application') {
                iconName = {
                    'pdf': 'pdf',
                    'vnd.ms-excel': 'MSExcel',
                    'vnd.ms-word': 'MSWord',
                    'vnd.ms-powerpoint': 'MSPowerPoint'
                }[subtype];

                if (iconName) return icons.getIcon(iconName);
            }

            return icons.getIcon('unknown');
        },
        getThumbnail: function(attachment, scale) {
            var settings = this.settings;

            scale || (scale = 256);
            var style = "max-width:" + scale + "px; " + "max-height:" + scale + "px;";

            var mimetype = attachment.get('mimetype');
            if (!_(this.thumbnailable).contains(mimetype)) {
                var src = this.iconForMimeType(mimetype);
                return $.when( $('<img>', {src: src, style: style}) );
            }

            var attachmentLocation = attachment.get('attachmentlocation');

            return getToken(settings, attachmentLocation).pipe(function(token) {
                var src = settings.read + "?" + $.param({
                    coll: settings.collection,
                    type: "T",
                    filename: attachmentLocation,
                    token: token,
                    scale: scale
                });

                return $('<img>', {src: src, style: style});
            });
        },
        originalURL: function(attachmentLocation, token, downLoadName) {
            return this.settings.read + "?" + $.param({
                coll: this.settings.collection,
                type: "O",
                filename: attachmentLocation,
                downloadname: downLoadName,
                token: token
            });
        },
        openOriginal: function(attachment) {
            var attachmentLocation = attachment.get('attachmentlocation');
            var origFilename = attachment.get('origfilename').replace(/^.*[\\\/]/, '');

            getToken(this.settings, attachmentLocation).done(function(token) {
                var src = this.originalURL(attachmentLocation, token, attachment.get('origfilename'));
                window.open(src);
            }.bind(this));
        },
        uploadFile: function(file, progressCB) {
            var settings = this.settings;
            var formData = new FormData();
            var attachmentLocation;
            var attachment;

            return $.get('/attachment_gw/get_upload_params/', {filename: file.name})
                .pipe(function(uploadParams) {
                    attachmentLocation = uploadParams.attachmentlocation;

                    formData.append('file', file);
                    formData.append('token', uploadParams.token);
                    formData.append('store', attachmentLocation);
                    formData.append('type', "O");
                    formData.append('coll', settings.collection);

                    return $.ajax({
                        url: settings.write,
                        type: 'POST',
                        data: formData,
                        processData: false,
                        contentType: false,
                        xhr: function() {
                            var xhr = $.ajaxSettings.xhr();
                            xhr.upload && xhr.upload.addEventListener('progress', progressCB);
                            return xhr;
                        }
                    });
                }).pipe(function() {
                    return new schema.models.Attachment.Resource({
                        attachmentlocation: attachmentLocation,
                        mimetype: file.type,
                        origfilename: file.name
                    });
                });
        }
    });

    return SpecifyAttachments;
});