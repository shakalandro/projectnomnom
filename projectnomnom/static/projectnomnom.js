$(document).ready(function() {
	(function(d){
		var js, id = 'facebook-jssdk'; if (d.getElementById(id)) {return;}
		js = d.createElement('script'); js.id = id; js.async = true;
		if (document.URL.indexOf('127.0.0.1') != -1 || document.URL.indexOf('localhost') != -1) {
			js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=275585199158118";
		} else {
			js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=161204603981737";
		}
     	d.getElementsByTagName('head')[0].appendChild(js);
	}(document));
});