<?php
// no direct access
defined('_JEXEC') or die('Restricted access');

require_once (JPATH_BASE.DS.'modules'.DS.'mod_roknavmenu'.DS.'lib'.DS.'BaseRokNavMenuFormatter.php');

/*
 * Created on Jan 16, 2009
 *
 * To change the template for this generated file go to
 * Window - Preferences - PHPeclipse - PHP - Code Templates
 */
class RokNavMenuFormatterTemplateMoxyFusion extends BaseRokNavMenuFormatter {
	function format(&$node, &$menu_params) {
	    // Format the current node
		
		if ($node->type == 'menuitem' or $node->type == 'separator') {
		    if ($node->hasChildren() ) {
    			$node->addLinkClass("daddy");
    		}  else {
    		    $node->addLinkClass("orphan");
    		}
    		
    		$node->addLinkClass("item");
            
		}
		
		if ($node->level == "0") {
		$node->addListItemClass("root");
		}
		
	}
}