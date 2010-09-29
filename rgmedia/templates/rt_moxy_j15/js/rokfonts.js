/**
 * RokBuildSpans - A multicolor-span helper that let the first word be colored.
 * 
 * @version		2.0
 * 
 * @license		MIT-style license
 * @author		Djamil Legato <djamil [at] djamil.it>
 * @client		Andy Miller @ Rockettheme
 * @copyright	Author
 */

var RokBuildSpans=function(g,j,k){(g.length).times(function(i){var e="."+g[i];var f=function(a){a.setStyle('visibility','visible');var b=a.getText();var c=b.split(" ");first=c[0];rest=c.slice(1).join(" ");html=a.innerHTML;if(rest.length>0){var d=a.clone().setText(' '+rest),span=new Element('span').setText(first);span.inject(d,'top');a.replaceWith(d)}};$$(e).each(function(c){j.each(function(h){c.getElements(h).each(function(b){var a=b.getFirst();if(a&&a.getTag()=='a')f(a);else f(b)})})})})};
