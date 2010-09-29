var sfHover = function(search, replaced) {
	if (!replaced) replaced = 'sfHover';
	var replacedActive = 'sfActive';

	var els = $$('.' + search).getElements('li');
	els[0].each(function(el) {
	    var first = el.getFirst();
	    if (first) els[0].push(first);
	});
	
	var actives = $$('.' + search).getElements('li.active');
	if (actives[0] && actives[0].length) {
		actives = actives[0];
		actives.each(function(active) {
			var first = active.getFirst();
			if (first) {
				first.addClass('active');
				var classes = first.getProperty('class').split(" ");
				var tmp = [];
				for (i = 1, l = classes.length; i<l;i++) tmp.push(classes[0] + '-' + classes[i]);
                tmp.push(classes.join('-'));
				tmp.each(function(cls) {first.addClass(cls);});
			}
		});
	};
	
	if (!els.length) return false;

	els.each(function(el) {
		el.addEvents({
			'mouseenter': function() {
				var classes = this.getProperty('class').split(" ");
				classes = classes.filter(function(y) { return !y.test("-" + replaced) && !y.test("-" + replacedActive); });
				
				classes.each(function(cls) { if (this.hasClass(cls)) this.addClass(cls + "-" + replaced); }, this);
				var hackish = classes.join("-") + "-" + replaced;
				if (!this.hasClass(hackish)) this.addClass(hackish);
				this.addClass(replaced);
			},
			'mouseleave': function() {
				var classes = this.getProperty('class').split(" ");
				classes = classes.filter(function(y) { return y.test("-" + replaced); });
				
				classes.each(function(cls) { if (this.hasClass(cls)) this.removeClass(cls); }, this);
				var hackish = classes.join("-") + "-" + replaced;
				if (!this.hasClass(hackish)) this.removeClass(hackish);
				this.removeClass(replaced);
			}
		});
	});
};

window.addEvent('domready', function() {
	sfHover('menutop');
});