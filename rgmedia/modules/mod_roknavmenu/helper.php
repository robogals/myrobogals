<?php
/**
 * @version $Id$
 * @package RocketWerx
 * @subpackage	RokNavMenu
 * @copyright Copyright (C) 2009 RocketWerx. All rights reserved.
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL, see LICENSE.php
 */
// no direct access
defined('_JEXEC') or die('Restricted access');

require_once (dirname(__FILE__).DS.'lib'.DS.'RokNavMenuTree.php');
jimport( 'joomla.filesystem.file' );


/**
 * mod_roknavmenu Helper class
 *
 * @static
 * @package		Joomla
 * @subpackage	Menus
 * @since		1.5
 */
class modRokNavMenuHelper
{
	function getMenuData(&$params)
	{
		$menu = new RokNavMenuTree();
		$menu->_params = &$params;
		$items = &JSite::getMenu();
		// Get Menu Items
		$rows = $items->getItems('menutype', $params->get('menutype'));
		$maxdepth = $menu->getParameter('maxdepth',10);

		// Build Menu Tree root down (orphan proof - child might have lower id than parent)
		$user =& JFactory::getUser();
		$ids = array();
		$ids[0] = true;
		$last = null;
		$unresolved = array();
		// pop the first item until the array is empty if there is any item
		if ( is_array($rows)) {
			while (count($rows) && !is_null($row = array_shift($rows)))
			{
				$row->ionly = $params->get('menu_images_link');
				if (!$menu->addNode($params, $row)) {
					if(!array_key_exists($row->id, $unresolved) || $unresolved[$row->id] < $maxdepth) {
						array_push($rows, $row);
						if(!isset($unresolved[$row->id])) $unresolved[$row->id] = 1;
						else $unresolved[$row->id]++;
					}	
				}
			}
		}
		return $menu;
	}
	
	function getThemePath(&$params){
		$default_module_theme_dir = JPath::clean('/modules/mod_roknavmenu/themes');
		$basic_theme = $default_module_theme_dir.'/basic';
		$theme = $params->get('theme', $basic_theme);
		// Set the theme to the old school default theme if it exists 
		if ($params->get('default_formatter', false)){
			$theme =  $default_module_theme_dir.'/'.$params->get('default_formatter', 'default');
		} 
		return $theme;
	}
	
	function getFormatterPath(&$params) {
		global $mainframe;
		$theme = modRokNavMenuHelper::getThemePath($params);
		
		// Get the formatters path 
		$formatter_path = JPath::clean(JPATH_ROOT.$params->get('theme', $theme)."/formatter.php");
		
		$template_default_formatter_path = JPath::clean(JPATH_ROOT.'/templates/'.$mainframe->getTemplate().'/html/mod_roknavmenu/formatter.php');
		if (JFile::exists($template_default_formatter_path)) {
			$formatter_path = 	$template_default_formatter_path;
		}
		
		//see if the backwards compat custom_formatter is set.		
		$template_formatter = $params->get('custom_formatter', "default");
		$template_named_formatter_path = JPath::clean(JPATH_ROOT.'/templates/'.$mainframe->getTemplate().'/html/mod_roknavmenu/formatters/'.$template_formatter.'.php');
		if (JFile::exists($template_named_formatter_path)) {
			$formatter_path = 	$template_named_formatter_path;
		}
		return $formatter_path;
	}
	
	function getLayoutPath(&$params) {
		global $mainframe;
		$theme = modRokNavMenuHelper::getThemePath($params);
		
		// Get the layout path
		$layout_path = JPath::clean(JPATH_ROOT.$theme."/layout.php");
		
		$joomla_layout_path = JModuleHelper::getLayoutPath('mod_roknavmenu');
		if (JFile::exists($joomla_layout_path)) {
			$layout_path = $joomla_layout_path;
		}
		
		//see if the backwards compat custom_formatter is set.		
		if ($params->get('custom_layout', false)) { 
			$template_layout = $params->get('custom_layout', "default");
			$template_named_layput_path = JPath::clean(JPATH_ROOT.'/templates/'.$mainframe->getTemplate().'/html/mod_roknavmenu/layouts/'.$template_layout.'.php');
			if (JFile::exists($template_named_layput_path)) {
				$layout_path = 	$template_named_layput_path;
			}
		}
		return $layout_path;
	}
	
	function getFormattedMenu($menu, &$params){
        global $mainframe;
		// get the base menu data structure
		
		// Run the basic formatter
		modRokNavMenuHelper::formatMenu($menu);
		
		$default_module_theme_dir = JPath::clean('/modules/mod_roknavmenu/themes');
		
		$theme = modRokNavMenuHelper::getThemePath($params);
		
		$theme_name = basename($params->get('theme', $theme));
		
		$formatter_path = modRokNavMenuHelper::getFormatterPath($params);
		
		//load the formatter
		require_once ($formatter_path);

		$theme_type = 'Template';
		// Find if this is a Default or Template theme
		if (dirname(JPath::clean($params->get('theme'))) == $default_module_theme_dir ) {
			$theme_type = 'Default';
		}

		// run the formatter class
		$theme_formatter_class = 'RokNavMenuFormatter'. str_replace('-','',$theme_type.$theme_name);		
		if (class_exists($theme_formatter_class)) {
			$formatter = new $theme_formatter_class();
			$formatter->format_tree($menu);
		}
		else if (class_exists  ('RokNavMenuFormatter')){ 
			$formatter = new RokNavMenuFormatter();
			$formatter->format_tree($menu);
		}
        
        return $menu;
	}
	
	/**
	 * Perform the basic common formatting to all menu nodes
	 */
	function formatMenu(&$menu) {
		
		
		//set the active tree branch
		$joomlamenu	= &JSite::getMenu();
		$active	= $joomlamenu->getActive();
		if (isset($active) && isset($active->tree) && count($active->tree)) {
			reset($active->tree);
			while (list($key, $value) = each($active->tree)) {
				$active_node =& $active->tree[$key]; 
				$active_child =& $menu->findChild($active_node);
				if ($active_child !== false) {
					$active_child->addListItemClass('active');
				}
			} 
		}
	
		// set the current node
		if (isset($active)) { 
			$current_child =& $menu->findChild($active->id);
			if ($current_child !== false && !$current_child->menualias) {
				$current_child->css_id = 'current';
			}
		}
		
		
		// Limit the levels of the tree is called for By limitLevels
		if ($menu->getParameter('limit_levels')) {
			$start	= $menu->getParameter('startLevel');
			$end	= $menu->getParameter('endLevel');
			
			//Limit to the active path if the start is more the level 0
			if ($start > 0) {
				$found = false;
				// get active path and find the start level that matches
				if (isset($active) && isset($active->tree) && count($active->tree)) { 
					reset($active->tree);
					while (list($key, $value) = each($active->tree)) {
						$active_child = & $menu->_children[$active->tree[$key]];
						if ($active_child != null && $active_child !== false) {
							if ($active_child->level == $start-1) {
								$menu->resetTop($active_child->id);
								$found = true;
								break;
							}
						}
					} 
				}
				if (!$found){
					$menu->_children= array();
				}
			}	
			//remove lower then the defined end level
			$menu->removeLevel($end);
		}
		
		// Remove the child nodes that were not needed to display unless showAllChildren is set
		$showAllChildren = $menu->getParameter('showAllChildren');
		if (!$showAllChildren) {
			if ($menu->hasChildren()){
				reset($menu->_children);
				while (list($key, $value) = each($menu->_children)) {
					$toplevel =& $menu->_children[$key]; 
					if (isset($active) && isset($active->tree) && in_array($toplevel->id, $active->tree) !== false){
						$last_active =& $menu->findChild($active->tree[count($active->tree)-1]);
						if ($last_active !==  false) {
							$toplevel->removeIfNotInTree($active->tree, $last_active->id);
							//$toplevel->removeLevel($last_active->level+1);
						}
					}
					else { 
						$toplevel->removeLevel($toplevel->level);
					}
				} 
			}
		}
	}
}