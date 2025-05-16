'use strict';
{
    const initData = JSON.parse(document.getElementById('django-admin-popup-response-constants').dataset.popupResponse);
    window.onunload = refreshParent;
    function refreshParent() {
        window.opener.location.reload();
    }
    window.close();
}
