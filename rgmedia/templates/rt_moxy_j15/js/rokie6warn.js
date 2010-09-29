/**
 * RokIEWarn - An IE6 Warning to invite people upgrading to IE6
 * 
 * @version		1.2-noOpacity
 * 
 * @license		MIT-style license
 * @author		Djamil Legato <djamil@rockettheme.com>
 * @client		RocketTheme, LLC.
 * @copyright	Author
 */
 
 
var RokIEWarn = new Class({
	'site': 'sitename',
	'initialize': function() {
		var warning = "<h3>You are currently browsing this site with Internet Explorer 6 (IE6).</h3><h4>NOTE: This template is compatible with IE6, however your experience will be enhanced with a newer browser.</h4><p>Internet Explorer 6 was released in August of 2001, and the lastest version of IE6 was released in August of 2004.  By continuing to run Internet Explorer 6 you are open to any and all security vulnerabilities discovered since that date.  In March of 2009, Microsoft released version 8 of Internet Explorer that, in addition to providing greater security, is faster and more standards compliant than both version 6 and 7 that came before it. The overall usage of Internet Explorer 6 has decreased to such a point that 2009 will probably be the year in which web developers stop supporting it, so please upgrade as soon as possible.  It's for your own good!</p> <br /><a class=\"external\"  href=\"http://www.microsoft.com/windows/internet-explorer/?ocid=ie8_s_cfa09975-7416-49a5-9e3a-c7a290a656e2\">Download Internet Explorer 8 NOW!</a>";
		
		this.box = new Element('div', {'id': 'iewarn'}).inject(document.body, 'top');
		var div = new Element('div').inject(this.box).setHTML(warning);
		
		var click = this.toggle.bind(this);
		var button = new Element('a', {'id': 'iewarn_close'}).addEvents({
			'mouseover': function() {
				this.addClass('cHover');
			},
			'mouseout': function() {
				this.removeClass('cHover');
			},
			'click': function() {
				click();	
			}
		}).inject(div, 'top');
		
		this.height = $('iewarn').getSize().size.y;
		
		this.fx = new Fx.Styles(this.box, {duration: 1000}).set({'margin-top': $('iewarn').getStyle('margin-top').toInt()});
		this.open = false;
		
		var cookie = Cookie.get('rokIEWarn'), height = this.height;
		//cookie = 'open'; // added for debug to not use the cookie value
		if (!cookie || cookie == "open") this.show();
		else this.fx.set({'margin-top': -height});

		
		return ;
	},
	
	'show': function() {
		this.fx.start({
			'margin-top': 0
		});
		this.open = true;
		Cookie.set('rokIEWarn', 'open', {duration: 7});
	},	
	'close': function() {
		var margin = this.height;
		this.fx.start({
			'margin-top': -margin
		});
		this.open = false;
		Cookie.set('rokIEWarn', 'close', {duration: 7});
	},	
	'status': function() {
		return this.open;
	},
	'toggle': function() {
		if (this.open) this.close();
		else this.show();
	}
});

window.addEvent('domready', function() {
	if (window.ie6) { (function() {var iewarn = new RokIEWarn();}).delay(2000); }
});