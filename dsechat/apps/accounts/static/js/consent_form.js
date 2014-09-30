/**
 * Created by mjbrooks on 9/30/2014.
 */
(function () {

    $(document).ready(function() {
        var conf = window.consent_form;

        if (!conf || !conf.consent_field_selector) {
            return;
        }


        var consentField = $(conf.consent_field_selector);
        var consentForm = $('.consent-form form');

        consentForm.find('.no-consent-button').on('click', function() {
            consentField.val(undefined);
            consentForm.submit();
        });

        consentForm.find('.consent-button').on('click', function() {
            consentField.val(1);
            consentForm.submit();
        });
    })

})();
