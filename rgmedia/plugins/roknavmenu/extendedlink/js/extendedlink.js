window.addEvent('domready', function() {
	var add = $('add_more'), more = $('more-fields');
	var rendered = $$('.roknavmenu-extendedlink');
	
	if (rendered.length) {
		rendered.each(function(render) {
			var inputs = render.getElements('input');
			inputs.each(function(input, i) {
				input.addEvents({
					'focus': function() {if ((this.value == "Name" && !i) || (this.value == "Value" && i == 1)) this.value = "";},
					'blur': function() {
						if (this.value == "" && !i) this.value = "Name";
						else if (this.value == "" && i == 1) this.value = "Value";
					}
				});
			});
		});
	}
	
	if (!add) return;
	
	extendedlinkInit(more);
	
	add.addEvent('click', function(e) {
		new Event(e).stop();
		more.getParent().getParent().getParent().getParent().getParent().setStyle('height', '');
		if (more.getLast() == null) {
			last = 0;
		}
		else {
			var last = more.getLast().id;
			last = last.split("_").slice(-1)[0].toInt();
		}
		var id = {
			'div': extendedlinkSettings.basename + '_' + (last + 1),
			'name': extendedlinkSettings.params + '[' + extendedlinkSettings.basename + '_name_' + (last + 1) + ']',
			'value': extendedlinkSettings.params + '[' + extendedlinkSettings.basename + '_value_' + (last + 1) + ']'
		};
		var div = new Element('div', {'id': id.div, 'class': 'roknavmenu-extendedlink', 'styles': {'margin': '5px 0'}});
		
		var input1 = new Element('input', {'type': 'text', 'name': id.name, 'size': '10'}).inject(div).setProperty('value', 'Name');
		var input2 = new Element('input', {'type': 'text', 'name': id.value, 'size': '10'}).inject(div).setProperty('value', 'Value');
		
		var remove = new Element('button', {'class': 'remove'}).setText('-').inject(div);
		
		var fx = {
			'remove': new Fx.Style(remove, 'opacity', {'duration': 200, 'wait': false}).set(0),
			'div': new Fx.Style(div, 'opacity', {'duration': 200, 'wait': false}).set(0)
		};
		
		div.inject(more);
		fx.div.start(1);
		
		input1.addEvents({
			'focus': function() {if (this.value == "Name") this.value = "";},
			'blur': function() {if (this.value == "") this.value = "Name";}
		});
		
		input2.addEvents({
			'focus': function() {if (this.value == "Value") this.value = "";},
			'blur': function() {if (this.value == "") this.value = "Value";}
		});
		
		div.addEvents({
			'mouseenter': function() {
				fx.remove.start(1);
			},
			'mouseleave': function() {
				fx.remove.start(0);
			}
		});
		
		remove.addEvent('click', function(e) {
			new Event(e).stop();
			more.getParent().getParent().getParent().getParent().getParent().setStyle('height', '');
			fx.div.start(0).chain(function() {
				delete fx.remove;
				delete fx.div;
				(function() {
					div.empty().remove();
					extendedlinkReorder(more);
				}).delay(100);
			});
		});
	});
});

var extendedlinkInit = function(more) {
	more.getChildren().each(function(div, i) {
		var inputs = div.getChildren();
		var input1 = inputs[0], input2 = inputs[1];
		var remove = new Element('button', {'class': 'remove'}).setText('-').inject(div);
		
		inputs.setStyle('margin', '5px 0');
		
		var fx = {
			'remove': new Fx.Style(remove, 'opacity', {'duration': 200, 'wait': false}).set(0),
			'div': new Fx.Style(div, 'opacity', {'duration': 200, 'wait': false}).set(1)
		};
		
		input1.addEvents({
			'focus': function() {if (this.value == "Name") this.value = "";},
			'blur': function() {if (this.value == "") this.value = "Name";}
		});
		
		input2.addEvents({
			'focus': function() {if (this.value == "Value") this.value = "";},
			'blur': function() {if (this.value == "") this.value = "Value";}
		});
		
		div.addEvents({
			'mouseenter': function() {
				fx.remove.start(1);
			},
			'mouseleave': function() {
				fx.remove.start(0);
			}
		});
		
		remove.addEvent('click', function(e) {
			new Event(e).stop();
			more.getParent().getParent().getParent().getParent().getParent().setStyle('height', '');
			fx.div.start(0).chain(function() {
				delete fx.remove;
				delete fx.div;
				(function() {
					div.empty().remove();
					extendedlinkReorder(more);
				}).delay(100);
			});
		});
		
	});
};

var extendedlinkReorder = function(more) {
	more.getChildren().each(function(div, i) {
		div.setProperty('id', extendedlinkSettings.basename  + '_' + (i + 1));
		div.getElements('input').each(function(input, j) {
			if (!j) input.setProperty('name', extendedlinkSettings.params + '[' + extendedlinkSettings.basename + '_name_' + (i + 1) + ']');
			else input.setProperty('name', extendedlinkSettings.params + '[' + extendedlinkSettings.basename + '_value_' + (i + 1) + ']');
		});
	});
};