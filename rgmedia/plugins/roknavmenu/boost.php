<?php
// no direct access
defined('_JEXEC') or die('Restricted access');
jimport( 'joomla.filesystem.file' );

class plgRokNavMenuBoost extends JPlugin 
{		
	function plgRokNavMenuBoost(&$subject, $config)
	{
		parent::__construct($subject, $config);
		$this->loadLanguage( '', JPATH_ADMINISTRATOR );
	}

		
	function onRokNavMenuRegisterParamsFile(&$param_files, $item_id){
		$template_path = JPATH::clean(JPATH_ROOT.'/templates/'.$this->_getFrontSideTemplate().'/html/mod_roknavmenu/items/item.xml');
		if (JFile::exists($template_path)){
			$param_files['PLG.ROKNAVMENU.PARAMTERS.TEMPLATE']=$template_path;
		}
		
		$template_themes_path = '/templates/'.$this->_getFrontSideTemplate().'/html/mod_roknavmenu/themes';
		$template_themes_full_path = JPath::clean(JPATH_ROOT.$template_themes_path);
		$template_theme_text = JText::_("Template theme"); 
		
		$module_themes_path = '/modules/mod_roknavmenu/themes'; 
		$module_themes_full_path = JPath::clean(JPATH_ROOT.$module_themes_path);
		$module_theme_text = JText::_("Default theme");
		$lang = JFactory::getLanguage();
		// get the template items.
		/** Get the Template Themes **/
		if (JFolder::exists($template_themes_full_path)) { 
			$folders = JFolder::folders($template_themes_full_path);
			if ( is_array($folders) )
			{
				reset($folders);
				while (list($key, $val) = each($folders)) {
					$folder =& $folders[$key]; 
					$langfile = $template_themes_full_path.DS.$folder.DS.'language'.DS.$lang->_lang.'.ini';
					if (JFile::exists($langfile)) {
						$lang->_load($langfile,'roknavmenu_theme_template_'.$folder);
					}
					
					$theme_item_file = $template_themes_full_path.DS.$folder.DS.'item.xml';
					if (JFile::exists($theme_item_file)) {
						$param_files[JText::sprintf('PLG.ROKNAVMENU.PARAMTERS.THEME', $template_theme_text." - ".$folder)]=$theme_item_file;
						
					}
				}
			}
		}
		if (JFolder::exists($module_themes_full_path)) { 
			$folders = JFolder::folders($module_themes_full_path);
			if ( is_array($folders) )
			{
				reset($folders);
				while (list($key, $val) = each($folders)) {
					$folder =& $folders[$key]; 
					$langfile = $module_themes_full_path.DS.$folder.DS.'language'.DS.$lang->_lang.'.ini';
					if (JFile::exists($langfile)) {
						$lang->_load($langfile,'roknavmenu_theme_module_'.$folder);
					}
					
					$theme_item_file = $module_themes_full_path.DS.$folder.DS.'item.xml';
					if (JFile::exists($theme_item_file)) {
						$param_files[JText::sprintf('PLG.ROKNAVMENU.PARAMTERS.THEME', $module_theme_text." - ".$folder)]=$theme_item_file;
					}
				}
			}
		}
	}
	
	function _getFrontSideTemplate($item_id = 0) {
		$db =& JFactory::getDBO();
		// Get the current default template
		
		$query = 'SELECT template'
			. ' FROM #__templates_menu'
			. ' WHERE client_id = 0 AND (menuid = 0 OR menuid = '.(int) $item_id.')'
			. ' ORDER BY menuid DESC';
		$db->setQuery($query, 0, 1);
		$defaultemplate = $db->loadResult();
		return $defaultemplate;
	}
}