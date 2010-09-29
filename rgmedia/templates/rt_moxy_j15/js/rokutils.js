/**
 * rokUtils - A set of tools for Refraction
 * 
 * @version		1.0
 * 
 * @license		MIT-style license
 * @author		Djamil Legato <djamil [at] djamil.it>
 * @client		Andy Miller @ Rockettheme
 * @copyright	Author
 */

window.addEvent('domready', function() {
	new SmoothScroll();
});

eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('c m=u,3;g.k(\'14\',5(){c p=$(\'13-12\');2(p){m=7 J.15(g);p.a(\'16\',\'B\').k(\'o\',5(e){7 z(e).y();m.R()})};2(g.18){c r=$(\'17-11\').10(\'.h\');2(r.q){r.S(5(h,i){2(h.U(\'G\'))h.T(\'h-G\')})}}3=7 A(g.Z);c n=$$(\'.Y 19\');2(n.q){2(g.1a)n.a(\'-1m-I-E\',\'K\');2(g.H)n.a(\'-H-I-E\',\'K\')}});c A=7 1d({4:{\'8\':\'\',\'t\':u,\'j\':1c,\'v\':0.9,\'p\':s,\'M\':s,\'C\':s},1e:5(4){1.1f(4);2(!1.4.8.q)d;1.8=$$(1.4.8);1.3=$(\'D-3\');1.l=$(\'D-3-6\');1.f=\'6\';2(!1.3)d;2(!1.4.C&&1.l)1.l.a(\'1h\',\'B\');2(1.4.t)1.3.a(\'1o\',\'1n\');1.x(1.3);1.w=7 J.X(1.3,\'v\',{1k:u,1j:1i}).1g(0);1.N(1.8)},x:5(3){2(!1.4.t)d;c j=1.4.j;d 3.a(\'j\',j)},N:5(8){2(1.l){1.l.k(\'o\',5(e){7 z(e).y();1.6()}.O(1))};2(1.4.M){1.3.k(\'o\',1.6.O(1))}8.S(5(P){P.k(\'o\',1.Q.1b(1))},1)},Q:5(e){7 z(e).y();1[(1.f==\'b\')?\'6\':\'b\']()},b:5(){2(1.f=="b")d;1.x(1.3);2(m)m.R();1.w.L(1.4.v);1.f=\'b\';1.F(\'b\')},6:5(){2(1.f==\'6\')d;1.w.L(0);1.f=\'6\';1.F(\'6\')}});A.W(7 V,7 1l);',62,87,'|this|if|panel|options|function|close|new|hooks||setStyle|open|var|return||status|window|separator||height|addEvent|panelClose|rokscroll|styles|click|scrollToTop|length|separators|true|fixedHeight|false|opacity|fx|setHeight|stop|Event|showcasePanel|none|showCloseButton|showcase|radius|fireEvent|daddy|webkit|border|Fx|12px|start|closeByClick|addEvents|bind|hook|toggle|toTop|each|addClass|hasClass|Options|implement|Style|styleslist|showcasePanelOptions|getElements|menu|scroll|top|domready|Scroll|outline|horiz|ie6|div|gecko|bindWithEvent|337|Class|initialize|setOptions|set|display|300|duration|wait|Events|moz|hidden|overflow'.split('|'),0,{}))


// IE6 bad looking hack :)
if (window.ie6) {
	window.addEvents({
		'domready': function() {
			$(document.body).addClass('ie-please-wait').setStyle('visibility', 'hidden');
		},
	
		'load': function() {
			(function() {$(document.body).removeClass('ie-please-wait').setStyle('visibility', 'visible');}).delay(10);
			var arrow = $$('.feature-arrow-r')[0], li = $$('ul.menutop').getFirst()[0];
			if (arrow) arrow.fireEvent('mouseleave', false, 500);
			if (li) li.addEvents({
				'mouseenter': function() {
					li.setStyle('padding-right', 1);
				},
				'mouseleave': function() {
					li.setStyle('padding-right', 0);
				}
			});
			
		},
		
		'unload': function() {
			$(document.body).addClass('ie-please-wait').setStyle('visibility', 'hidden');
		}
	});
}

// IE7 RokStories Hack
if (window.ie) {
	window.addEvent('domready', function() {
		var rokstories = $$('.rokstories-layout2 .desc-container'), list = [];
		rokstories.each(function(rokstory, i) {
			if (!rokstory.getElements('.description span').length) list.push(i);
		});
		if (list.length) list.each(function(value) {
			rokstories[value].setStyle('display', 'none');
		});
		
		var horizmenu = $('horizmenu-surround');
		if (horizmenu) {
			var ul = horizmenu.getFirst();
			var size = ul.getSize().size.x;
			horizmenu.setStyle('width', size);
			
		}
	});
}