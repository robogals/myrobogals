<?php
// no direct access
defined('_JEXEC') or die('Restricted access');

class plgRokNavMenuExtendedLink extends JPlugin 
{	

	
	function plgRokNavMenuExtendedLink(&$subject, $config)
	{
		parent::__construct($subject, $config);
		$this->loadLanguage( '', JPATH_ADMINISTRATOR );
	}
	
	function onRokNavMenuRegisterParamsFile(&$param_files, $item_id){
		$param_files['PLG.ROKNAVMENU.EXTENDEDLINK.PARAMTERS.TITLE']=dirname(__FILE__).DS.'extendedlink'.DS.'params.xml';
	}
	
	function onRokNavMenuModifyLink(&$node, &$menu_params) {
		$count = 0;
		while (true) { 
			$count++;
			$current_name = $node->_params->get('roknavmenu_extendedlink_name_'.$count, '');
			if ($current_name=='') {
				break;
			}
			$current_value = $node->_params->get('roknavmenu_extendedlink_value_'.$count, '');
			$node->addLinkAddition($current_name, $current_value);
		}

	}
}