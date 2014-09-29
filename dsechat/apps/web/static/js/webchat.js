$(document).ready(function () {
    Candy.init('http-bind/', {
        core: {
            // only set this to true if developing / debugging errors
            debug: false,
            // autojoin is a *required* parameter if you don't have a plugin (e.g. roomPanel) for it
            //   true
            //     -> fetch info from server (NOTE: does only work with openfire server)
            //   ['test@conference.example.com']
            //     -> array of rooms to join after connecting
            autojoin: true
        },
        view: {
            assets: window.webchat.assets
        }
    });

    CandyShop.InlineImages.initWithMaxImageSize(200);
    CandyShop.Notifications.init();
    CandyShop.Replies.init();
    CandyShop.Timeago.init();
    CandyShop.TypingNotifications.init();
//    CandyShop.Refocus.init();

    Candy.Core.connect();

});
