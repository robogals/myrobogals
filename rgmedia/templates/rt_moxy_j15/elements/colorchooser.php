<?php
defined('_JEXEC') or die();
define('TEMPLATE', 'rt_moxy_j15');
include_once('../templates/'.TEMPLATE.'/styles.php');

class JElementColorChooser extends JElement {
	

	function fetchElement($name, $value, &$node, $control_name)
	{
		global $stylesList;
		$output = '';
		$document 	=& JFactory::getDocument();
		
		if (!defined('MOORAINBOW')) {
			
			$document->addStyleSheet('../templates/'.TEMPLATE.'/admin/preview/preview.css');
			
			$scriptconfig  = $this->populateStyles($stylesList);
			$scriptconfig .= $this->rainbowInit();
			
			$document->addScriptDeclaration($scriptconfig);
			
			define('MOORAINBOW',1);
		}
	
		$scriptconfig = $this->newRainbow($name);
		
		$document->addScriptDeclaration($scriptconfig);

		

		/*$output .= "<input class=\"picker-input\" id=\"".$control_name.$name."\" name=\"".$control_name."[".$name."]\" type=\"text\" size=\"7\" maxlength=\"7\" value=\"".$value."\" />";
		$output .= "<div class=\"picker\" id=\"myRainbow_".$name."_input\"><div class=\"overlay\"></div></div>\n";*/
		$output = false;
		
		return $output;
	}
	
	function newRainbow($name)
	{
		return "window.addEvent('domready', function() {		
			$$('#paramsheaderStyle', '#paramsbodyStyle').addEvent('change', function() {
				$('paramspresetStyle').selectedIndex = $('paramspresetStyle').getChildren().length - 1;
			});
		});\n";
	}
	
	function populateStyles($list)
	{
		$script = "
		var stylesList = new Hash({});
		var styleSelected = null;
		window.addEvent('domready', function() {
			styleSelected = $('paramspresetStyle').getValue();
			$('paramspresetStyle').empty();\n";
		
		foreach($list as $name => $style) {
			$js = "			stylesList.set('$name', ['{$style[0]}'";
			for ($i = 1, $l = count($style); $i < $l; $i++) {
				$js .= ", '{$style[$i]}'";
			}
			$js .= "]);\n";
			$script .= $js;
		}
			
		$script .= "		});";
		
		return $script;
	}
	
	function rainbowInit()
	{
		return "			
			/* START_DEBUG ONLY */
			var debug_only = function() {
				var td = new Element('td', {'id': 'toolbar-colorstyle', 'class': 'button'}).inject('toolbar-preview', 'before');
				var a = new Element('a', {'class': 'toolbar', 'href': '#'}).inject(td).setText('Custom style');
				new Element('span', {'class': 'icon-32-colorstyle', 'title': 'Output custom style'}).inject(a, 'top');
				
				var tr = new Element('tr').inject($('paramsbodyStyle').getParent().getParent(), 'after');
				var td1 = new Element('td', {'class': 'paramlist_key', 'styles': 'width: 40%;'}).inject(tr);
				var span = new Element('span', {'class': 'editlinktip'}).inject(td1).setHTML('Custom style output');
				
				var td2 = new Element('td', {'class': 'paramlist_value'}).inject(tr);
				var tarea = new Element('textarea', {'styles': 'width: 100%; height: 100px'}).inject(td2);
				
				var scroll = new Fx.Scroll(window, {offset: {x: false, y: -5}});
				a.addEvent('click', function(e) {
					new Event(e).stop();
					var arr = [];
					
					var output = [
						$('paramsheaderStyle').getValue(),
						$('paramsbodyStyle').getValue()
					];
					
					output = output.join('\', \'');
					
					tarea.setHTML('\'style_name\' => array(\''+output+'\')');
					
					tarea.focus();
					tarea.select();
					
					scroll.toElement(tarea);
				});
			};
			
			/* END_DEBUG ONLY */
			
			window.addEvent('domready', function() {
				
				debug_only();
				
				// Styles Combo
				var stylesCombo = $('paramspresetStyle');
				var header = $('paramsheaderStyle');
				var body = $('paramsbodyStyle');
				
				stylesList.each(function(key, value) {
					var option = new Element('option', {'value': value.toLowerCase()}).setHTML(value.capitalize());
					if (value == styleSelected) option.setProperty('selected', 'selected');
					option.inject(stylesCombo);
				});
				var option = new Element('option', {'value': 'custom'}).setHTML('Custom').inject(stylesCombo);
				if (styleSelected == 'custom') option.setProperty('selected', 'selected');
				
				stylesCombo.addEvent('change', function(e) {
					new Event(e).stop();
					if (this.value == 'custom') return;
					header.getChildren().each(function(el) {
						if (el.value == stylesList.get(this.value)[0]) el.selected = true;
					}, this);
					body.getChildren().each(function(el) {
						if (el.value == stylesList.get(this.value)[1]) el.selected = true;
					}, this);
				});				
			});
		";
	}
}

?>