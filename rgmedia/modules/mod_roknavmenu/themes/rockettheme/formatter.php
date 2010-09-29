<?php
// no direct access
defined('_JEXEC') or die('Restricted access');

require_once (JPATH_BASE.DS.'modules'.DS.'mod_roknavmenu'.DS.'lib'.DS.'BaseRokNavMenuFormatter.php');

class RokNavMenuFormatterDefaultRockettheme extends BaseRokNavMenuFormatter {
	function format(&$node, &$menu_params) {
		// Format the current node
		if ($node->level == 0) {
			$node->addLinkClass("topdaddy");
		}
		else if ($node->hasChildren() ) {
			$node->addLinkClass("daddy");
		}
	}
}