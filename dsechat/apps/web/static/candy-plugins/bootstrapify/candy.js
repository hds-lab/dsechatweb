var CandyShop = (function (self) {
    return self;
}(CandyShop || {}));

CandyShop.Bootstrapify = (function (self, Candy, $) {

    var _options = {
    };

    self.init = function (options) {

        $.extend(true, _options, options);

        self.overrideHideModal();

        //Override the default login form
        self.overrideShowLoginForm();
        self.overrideShowEnterPasswordForm();

        //Override the modal pane
        Candy.View.Template.Chat.modal =
            '<div class="modal" id="chat-modal-overlay">\
                <div class="modal-dialog" id="chat-modal">\
                    <div class="modal-content">\
                        <div class="modal-body" id="chat-modal-body"></div>\
                        <img src="{{assetsPath}}img/modal-spinner.gif" id="chat-modal-spinner" />\
                         <button type="button" class="close" data-dismiss="modal" id="admin-message-cancel">\
                            <span aria-hidden="true">&times;</span><span class="sr-only">Close</span>\
                        </button>\
                    </div><!-- /.modal-content -->\
                </div><!-- /.modal-dialog -->\
            </div><!-- /.modal -->\
            <div class="modal-backdrop in"></div>';

        //Override the Login form
        Candy.View.Template.Login.form =
            '<form method="post" id="login-form" class="login-form form-horizontal">\
                {{#message}}\
                <div class="alert alert-warning">{{message}}</div>\
                {{/message}}\
                {{#displayNickname}}\
                    <div class="form-group">\
                        <label for="username" class="control-label col-sm-3">{{_labelNickname}}</label>\
                        <div class="col-sm-9">\
                        <input type="text" id="username" name="username" class="form-control" required/>\
                    </div></div>\
                {{/displayNickname}}\
                {{#displayUsername}}\
                    <div class="form-group">\
                        <label for="username" class="control-label col-sm-3">{{_labelUsername}}</label>\
                        <div class="col-sm-9">\
                        <input type="text" id="username" name="username" class="form-control" required/>\
                    </div></div>\
                {{/displayUsername}}\
                {{#presetJid}}\
                    <div class="form-group">\
                        <label for="username" class="control-label col-sm-3">{{_labelUsername}}</label>\
                        <div class="col-sm-9">\
                        <input type="text" id="username" name="username" class="form-control" value="{{presetJid}}" required/>\
                    </div></div>\
                {{/presetJid}}\
                {{#displayPassword}}\
                    <div class="form-group">\
                        <label for="password" class="control-label col-sm-3">{{_labelPassword}}</label>\
                        <div class="col-sm-9">\
                        <input type="password" id="password" name="password" class="form-control" required/>\
                    </div></div>\
                {{/displayPassword}}\
                <div class="buttons">\
                    <input type="submit" class="button btn btn-primary" value="{{_loginSubmit}}" />\
                </div>\
            </form>';

        Candy.View.Template.PresenceError.enterPasswordForm =
            '<form method="post" id="enter-password-form" class="enter-password-form form-horizontal">\
            <div class="form-title">{{_label}}</div>\
            <div class="form-group">\
                <label for="password" class="control-label col-sm-3">{{_labelPassword}}</label>\
                <div class="col-sm-9">\
                <input type="password" id="password" name="password" class="form-control" required/>\
            </div></div>\
            <div class="buttons">\
                <input type="submit" class="button btn btn-primary" value="{{_joinSubmit}}" />\
            </div></form>';

        Candy.View.Template.PresenceError.nicknameConflictForm =
            '<form method="post" id="nickname-conflict-form" class="nickname-conflict-form form-horizontal">\
            <div class="form-title">{{_label}}</div>\
            <div class="form-group">\
                <label for="nickname" class="control-label col-sm-3">{{_labelNickname}}</label>\
                <div class="col-sm-9">\
                <input type="text" id="nickname" name="nickname" class="form-control" required/>\
            </div></div>\
            <div class="buttons">\
                <input type="submit" class="button btn btn-primary" value="{{_loginSubmit}}" />\
            </div></form>';

    };

    //What should be self, what object and property are we overriding,
    // and a function generator expecting (self, plugin, original)
    self.override = function (context, object, property, replacementGenerator) {
        var original = object[property];
        object[property] = replacementGenerator(context, self, original);
    };

    self.overrideHideModal = function () {
        self.override(
            Candy.View.Pane,
            Candy.View.Pane.Chat.Modal, 'hide',
            function (self, plugin, original) {
                return function (callback) {
                    $('#chat-modal').fadeOut('fast', function () {
                        $('#chat-modal-body').text('');
                        $('#chat-modal-overlay').hide();
                        $('.modal-backdrop').removeClass('in').hide(); // just added this to remove the backdrop
                    });

                    // restore initial esc handling
                    $(document).keydown(function (e) {
                        if (e.which === 27) {
                            e.preventDefault();
                        }
                    });
                    if (callback) {
                        callback();
                    }
                };
            });
    };

    self.overrideShowLoginForm = function () {
        //We override this method so we can use Bootstrap error messages in the template
        self.override(
            Candy.View.Pane,
            Candy.View.Pane.Chat.Modal, 'showLoginForm',
            function (self, plugin, original) {

                return function (message, presetJid) {

                    self.Chat.Modal.show(Mustache.to_html(Candy.View.Template.Login.form, {
                        _labelNickname: $.i18n._('labelNickname'),
                        _labelUsername: $.i18n._('labelUsername'),
                        _labelPassword: $.i18n._('labelPassword'),
                        _loginSubmit: $.i18n._('loginSubmit'),
                        message: message,
                        displayPassword: !Candy.Core.isAnonymousConnection(),
                        displayUsername: !presetJid,
                        displayNickname: Candy.Core.isAnonymousConnection(),
                        presetJid: presetJid ? presetJid : false
                    }));
                    $('#login-form').children(':input:first').focus();

                    // register submit handler
                    $('#login-form').submit(function () {
                        var username = $('#username').val(),
                            password = $('#password').val();

                        if (!Candy.Core.isAnonymousConnection()) {
                            // guess the input and create a jid out of it
                            var jid = Candy.Core.getUser() && username.indexOf("@") < 0 ?
                                username + '@' + Strophe.getDomainFromJid(Candy.Core.getUser().getJid()) : username;

                            if (jid.indexOf("@") < 0 && !Candy.Core.getUser()) {
                                Candy.View.Pane.Chat.Modal.showLoginForm($.i18n._('loginInvalid'));
                            } else {
                                //Candy.View.Pane.Chat.Modal.hide();
                                Candy.Core.connect(jid, password);
                            }
                        } else { // anonymous login
                            Candy.Core.connect(presetJid, null, username);
                        }
                        return false;
                    });
                };
            });
    };

    self.overrideShowEnterPasswordForm = function () {
        //We override this method so we can use Bootstrap error messages in the template

        self.override(
            Candy.View.Pane,
            Candy.View.Pane.Chat.Modal, 'showEnterPasswordForm',
            function (self, plugin, original) {
                return function (roomJid, roomName, message) {
                    self.Chat.Modal.show(Mustache.to_html(Candy.View.Template.PresenceError.enterPasswordForm, {
                        roomName: roomName,
                        message: message,
                        _labelPassword: $.i18n._('labelPassword'),
                        _label: (message ? message : $.i18n._('enterRoomPassword', [roomName])),
                        _joinSubmit: $.i18n._('enterRoomPasswordSubmit')
                    }), true);
                    $('#password').focus();

                    // register submit handler
                    $('#enter-password-form').submit(function () {
                        var password = $('#password').val();

                        self.Chat.Modal.hide(function () {
                            Candy.Core.Action.Jabber.Room.Join(roomJid, password);
                        });
                        return false;
                    });
                };
            });
    };

    return self;

})
(CandyShop.Bootstrapify || {}, Candy, jQuery);
