<?php
/**
 * @version $Id$
 * @package RocketWerx
 * @subpackage	RokNavMenu
 * @copyright Copyright (C) 2009 RocketWerx. All rights reserved.
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL, see LICENSE.php
 */

// Check to ensure this file is within the rest of the framework
defined('JPATH_BASE') or die();

/**
 * Renders a file list from a directory in the current templates directory
 */

class JElementExtendedLinkNameValue extends JElement
{
	/**
	* Element name
	*
	* @access	protected
	* @var		string
	*/
	var	$_name = 'ExtendedLinkNameValue';
	
	function fetchElement($name, $value, &$node, $control_name)
	{
		$doc =& JFactory::getDocument();
		$all_params = $this->_parent;
		$count = 0;
		
	
		
		$namevalues = array(); 
		//get all current values
		while (true) { 
			$count++;
			$current_name = $all_params->get($name.'_name_'.$count, '');
			if ($current_name=='') {
				break;
			}
			$current_value = $all_params->get($name.'_value_'.$count, '');
			$namevalues[$count]=array('name'=>$current_name,'value'=>$current_value);
		}
		
//		if (count($namevalues) == 0) {
//			$namevalues[1]=array('name'=>'','value'=>'');
//		}
		
		$html='';
		$html = '<button id="add_more">Add</button><br /><br />' .
				'<div id="more-fields">';
		for($i=1; $i <= count($namevalues); $i++){
			$html .= '<div id="'. $name. '_' .$i. '" class="roknavmenu-extendedlink" style="margin: 5px 0pt;">' 
				.'<input type="text" name="' . $control_name.'['.$name. '_name_' .$i. ']" value="'.$namevalues[$i]['name'].'" size="10 " /><input type="text" name="' . $control_name.'['. $name. '_value_' .$i. ']" value="'.$namevalues[$i]['value'].'" size="10" />' 
				.'</div>';
		}
		$html .= '</div>';
		
		$plugin_js_path = JURI::root(true).'/plugins/roknavmenu/extendedlink/js';
    	$doc->addScript($plugin_js_path."/extendedlink.js");
		$doc->addScriptDeclaration("var extendedlinkSettings = {'basename': '" . $name.   "', 'params': '" . $control_name. "'};");
	
		return $html;
	}
}
