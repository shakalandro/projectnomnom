$(document).ready(function() {
	window.fbAsyncInit = function() {
        FB.init({appId: '161204603981737', status: true, cookie: true,
        		 xfbml: true, oauth: true});
        FB.Event.subscribe('auth.login',
        	function(response) {
            	FB.api('/me', function(data) {
            		alert(data.name);
            	});
            }
        );
    };
    (function(d){
       var js, id = 'facebook-jssdk'; if (d.getElementById(id)) {return;}
       js = d.createElement('script'); js.id = id; js.async = true;
       js.src = "//connect.facebook.net/en_US/all.js";
       d.getElementsByTagName('head')[0].appendChild(js);
    }(document));
});
