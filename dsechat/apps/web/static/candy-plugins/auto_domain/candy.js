var CandyShop = (function (self) {
    return self;
}(CandyShop || {}));

CandyShop.AutoDomain = (function (self, Candy, $) {

    var _options = {
        xmppDomain: ''
    };

    self.init = function (options) {

        $.extend(true, _options, options);

        //Wrap the connect method
        self.wrapConnect();

        //Override the default login form
        self.overrideShowLoginForm();
    };

    self.wrapConnect = function() {

        //Pretend we're inside Candy.Core where self=Candy.Core
        (function(self, plugin) {
            var originalConnect = self.connect;

            self.connect = function (jidOrHost, password, nick) {

                //Add the domain onto the jid
                if (jidOrHost && jidOrHost.indexOf("@") < 0) {
                    jidOrHost = jidOrHost + "@" + _options.xmppDomain;
                }

                return originalConnect.call(self, jidOrHost, password, nick);
            };
        })(Candy.Core, self);
    };

    self.overrideShowLoginForm = function() {

        //Pretend we're inside the Candy.View.Pane definition where self=Candy.View.Pane
        (function(self, plugin) {

            var originalFunction = self.Chat.Modal.showLoginForm;

            self.Chat.Modal.showLoginForm = function (message, presetJid) {

                //Call the original to generate the form
                originalFunction.call(self, message, presetJid);

                // override the default submit handler
                $('#login-form').unbind('submit');
                $('#login-form').submit(function (e) {
                    e.preventDefault();

                    var username = $('#username').val(),
                        password = $('#password').val();

                    if (!Candy.Core.isAnonymousConnection()) {

                        // guess the input and create a jid out of it
                        var jid = Candy.Core.getUser() && username.indexOf("@") < 0 ?
                            username + '@' + Strophe.getDomainFromJid(Candy.Core.getUser().getJid()) : username;

                        //Add the xmpp domain if one is not specified
                        if (jid.indexOf('@') < 0) {
                            jid += "@" + _options.xmppDomain;
                        }

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
        })(Candy.View.Pane, self);
    };

    return self;

})(CandyShop.AutoDomain || {}, Candy, jQuery);