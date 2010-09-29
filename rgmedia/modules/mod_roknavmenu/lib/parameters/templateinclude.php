<?php
/**
 * @version $Id$
 * @package RocketWerx
 * @subpackage	RokNavMenu
 * @copyright Copyright (C) 2009 RocketWerx. All rights reserved.
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL, see LICENSE.php
 */
defined('_JEXEC') or die();
require_once (dirname(__FILE__).DS.'..'.DS.'BaseRokNavMenuTemplateParams.php');

class JElementTemplateInclude extends JElement
{
	function fetchElement($name, $value, &$node, $control_name)
	{
		global $mainframe;
		$html = "";
		$values = array();
		
		// get the current from side tem

		//Run the template formatter if its there if not run the default formatter
		$tPath = JPATH_ROOT.DS.'templates'.DS.$this->_getFrontSideTemplate().DS.'html'.DS.'mod_roknavmenu'.DS.'parameters.php';   
		if (file_exists($tPath)) {
			
			// get all the params for the module
			$all_params = $this->_parent;		
			require_once ($tPath);
			$template_params = new RokNavMenuTemplateParams();
			$html .= $template_params->getTemplateParams($name, $control_name, $all_params);
		}
		
		if (strlen($html) == 0) {
			$html = JText::_("ROKNAVMENU.MSG.NO_TEMPLATE_CONFIG");
		}
		return $html;
	}
	
	function _getFrontSideTemplate() {
		$db =& JFactory::getDBO();
		// Get the current default template
		$query = ' SELECT template '
				.' FROM #__templates_menu '
				.' WHERE client_id = 0 '
				.' AND menuid = 0 ';
		$db->setQuery($query);
		$defaultemplate = $db->loadResult();
		return $defaultemplate;
	}
	
}

