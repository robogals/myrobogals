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

class JElementThemeParameters extends JElement
{
	/**
	* Element name
	*
	* @access	protected
	* @var		string
	*/
	var	$_name = 'TemplateFilelist';

	var $_front_side_template;
	
	function fetchElement($name, $value, &$node, $control_name)
	{
		jimport( 'joomla.filesystem.folder' );
		jimport( 'joomla.filesystem.file' );
		$doc =& JFactory::getDocument();
			
		$filter		= $node->attributes('filter');
		$exclude	= $node->attributes('exclude');
		
		// path to directory
		$template_themes_path = '/templates/'.$this->_getFrontSideTemplate().'/html/mod_roknavmenu/themes';
		$template_themes_full_path = JPath::clean(JPATH_ROOT.$template_themes_path);
		$template_theme_text = JText::_("Template theme");
		
		$module_themes_path = '/modules/mod_roknavmenu/themes'; 
		$module_themes_full_path = JPath::clean(JPATH_ROOT.$module_themes_path);
		$module_theme_text = JText::_("Default theme");
		
		$module_js_path = JURI::root(true).'/modules/mod_roknavmenu/lib/js';
		$doc->addScript($module_js_path."/switcher.js");
		$doc->addScriptDeclaration("window.addEvent('domready', function() {new NavMenuSwitcher('paramtheme');});");
		$lang = JFactory::getLanguage();
		$parameter_sets = array();

		 /** Get the Template Themes parameters **/
		if (JFolder::exists($template_themes_full_path)) { 
			$folders = JFolder::folders($template_themes_full_path, $filter);
			if ( is_array($folders) )
			{
				reset($folders);
				while (list($key, $val) = each($folders)) {
					$folder =& $folders[$key];
					if ($exclude)
					{
						if (preg_match( chr( 1 ) . $exclude . chr( 1 ), $folder ))
						{
							continue;
						}
					}
					$theme_path = $template_themes_path.DS.$folder;
					
					$langfile = JPath::clean(JPATH_ROOT.$theme_path.DS.'language'.DS.$lang->_lang.'.ini');
					if (JFile::exists($langfile)) {
						$lang->_load($langfile,'roknavmenu_theme_template_'.$folder);
					}
					
					$param_file_path =  $theme_path.DS.'parameters.xml';
					if (JFile::exists(JPath::clean(JPATH_ROOT.$param_file_path))) { 
						
						$parameters = new JParameter( $this->_parent->_raw, JPath::clean(JPATH_ROOT.$param_file_path));
						$parameter_sets[$theme_path] = $parameters->getParams();
					}
				}
			}
		}
		 /** Get the Default Themes parameters **/
		if (JFolder::exists($module_themes_full_path)) { 
			$folders = JFolder::folders($module_themes_full_path, $filter);
			if ( is_array($folders) )
			{
				reset($folders);
				while (list($key, $val) = each($folders)) {
					$folder =& $folders[$key];
					if ($exclude)
					{
						if (preg_match( chr( 1 ) . $exclude . chr( 1 ), $folder ))
						{
							continue;
						}
					}

					$theme_path = $module_themes_path.DS.$folder;

					$langfile = JPath::clean(JPATH_ROOT.$theme_path.DS.'language'.DS.$lang->_lang.'.ini');
					if (JFile::exists($langfile)) {
						$lang->_load($langfile,'roknavmenu_theme_module_'.$folder);
					}
					
					$param_file_path =  $theme_path.DS.'parameters.xml';
					
					$parameter_sets[$theme_path]  = array();
					if (JFile::exists(JPath::clean(JPATH_ROOT.$param_file_path))) { 	
						$parameters = new JParameter( $this->_parent->_raw, JPath::clean(JPATH_ROOT.$param_file_path));
						$parameter_sets[$theme_path] = $parameters->getParams();
					}
				}
			}
		}
		$parameter_renders = array();
		reset($parameter_sets);
		
		$html = '';
		// render a parameter set
		while(list($key, $val) = each($parameter_sets)) {
			$params =& $parameter_sets[$key];
			$cls = basename($key);
			if (empty($params)){
				$html .= '<p class="'.$cls.'"><span>' . JText::_('ROKNAVMENU.MSG.NO_THEME_OPTIONS_AVAILABLE') . ' </span></p>';	
			}
			else { 
				//render an individual parameter
				for ($i=0; $i < count($params); $i++) { 
					$param =& $params[$i];
					$html .= '<p class="'.$cls.'"><span>'.$param[0].':</span>' .$param[1] . '</p>';
				}
			}
		}
		
		return $html;
	}
	
	function _getFrontSideTemplate() {
		if (empty($this->_front_side_template)) { 
			$db =& JFactory::getDBO();
			// Get the current default template
			$query = ' SELECT template '
					.' FROM #__templates_menu '
					.' WHERE client_id = 0 '
					.' AND menuid = 0 ';
			$db->setQuery($query);
			$defaultemplate = $db->loadResult();
			$this->_front_side_template = $defaultemplate;
		}
		return $this->_front_side_template;
	}
}
