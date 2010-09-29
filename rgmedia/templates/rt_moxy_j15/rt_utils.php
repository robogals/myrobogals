<?php
defined( '_JEXEC' ) or die( 'Restricted index access' );

jimport('joomla.filesystem.file');

global $Itemid, $modules_list, $mainmodulesBlocks, $template_real_width, $leftcolumn_width, $rightcolumn_width, $menu_rows_per_column, $menu_columns, $menu_multicollevel;

if ($mtype!="module") :
	// menu code
	$document	= &JFactory::getDocument();
	$renderer	= $document->loadRenderer( 'module' );
	$options	 = array( 'style' => "raw" );
	$module	 = JModuleHelper::getModule( 'mod_roknavmenu' );
	$topnav = false; $subnav = false;
	
	// Get the params for the menu type and render the main menu
	$menu_params_file = JPATH_ROOT.DS.'templates'.DS.$this->template.DS."menus".DS.$mtype.".ini";
	
	if (JFile::exists($menu_params_file)) :
		$menu_params_content = file_get_contents($menu_params_file);
		eval("\$module->params = \"$menu_params_content\";");
	endif;

	$topnav = $renderer->render( $module, $options );
	
	// See if this is a splitmenu and render the subnav 
	if ($mtype=="splitmenu") :		
		$module	 = JModuleHelper::getModule( 'mod_roknavmenu' );
		$menu_params_file = JPATH_ROOT.DS.'templates'.DS.$this->template.DS."menus".DS.$mtype."_subnav.ini";
		if (JFile::exists($menu_params_file)) :
			$menu_params_content = file_get_contents($menu_params_file);
			eval("\$module->params = \"$menu_params_content\";");
		endif;
		$options = array( 'style' => "submenu");
		$subnav = $renderer->render( $module, $options );
	endif;

	elseif ($mtype=="module") :
		$subnav = false;

endif;

$menus     = &JSite::getMenu();
$menu       = $menus->getActive();
$pageclass = "";

if (is_object( $menu )) : 
$params = new JParameter( $menu->params );
$pageclass = $params->get( 'pageclass_sfx' );
endif;

// make sure subnav is empty
if (strlen($subnav) < 10) $subnav = false;
//Are we in edit mode
$editmode = false;
if (JRequest::getCmd('task') == 'edit' ) :
	$editmode = true;
endif;

$mainmodulesBlocks = array(
	'case1' => array('showcase', 'showcase2', 'showcase3'),
	'case2' => array('user1', 'user2', 'user3'),
	'case3' => array('user4', 'user5', 'user6'),
	'case4' => array('bottom', 'bottom2', 'bottom3'),
	'case5' => array('user7', 'user8', 'user9'),
	'case6' => array('footer', 'footer2', 'footer3')
);

$menu = &JSite::getMenu();
$active = $menu->getActive();

$showmod_count = ($this->countModules('showcase')>0) + ($this->countModules('showcase2')>0) + ($this->countModules('showcase3')>0);
$showmod_width = $showmod_count > 0 ? ' w' . floor(99 / $showmod_count) : '';
$mainmod_count = ($this->countModules('user1')>0) + ($this->countModules('user2')>0) + ($this->countModules('user3')>0);
$mainmod_width = $mainmod_count > 0 ? ' w' . floor(99 / $mainmod_count) : '';
$mainmod2_count = ($this->countModules('user4')>0) + ($this->countModules('user5')>0) + ($this->countModules('user6')>0);
$mainmod2_width = $mainmod2_count > 0 ? ' w' . floor(99 / $mainmod2_count) : '';
$mainmod3_count = ($this->countModules('user7')>0) + ($this->countModules('user8')>0) + ($this->countModules('user9')>0);
$mainmod3_width = $mainmod3_count > 0 ? ' w' . floor(99 / $mainmod3_count) : '';
$mainmod4_count = ($this->countModules('bottom')>0) + ($this->countModules('bottom2')>0) + ($this->countModules('bottom3')>0);
$mainmod4_width = $mainmod4_count > 0 ? ' w' . floor(99 / $mainmod4_count) : '';
$mainmod5_count = ($this->countModules('footer')>0) + ($this->countModules('footer2')>0) + ($this->countModules('footer3')>0);
$mainmod5_width = $mainmod5_count > 0 ? ' w' . floor(99 / $mainmod5_count) : '';

$leftcolumn_width = ((!$active and $this->countModules('inactive')) or $this->countModules('left')>0 or ($subnav and $splitmenu_col=="leftcol")) ? $leftcolumn_width : 0;
$rightcolumn_width = (!$editmode and ($this->countModules('right')>0 or ($subnav and $splitmenu_col=="rightcol"))) ? $rightcolumn_width : 0;

$col_mode = "s-c-s";
if ($leftcolumn_width==0 and $rightcolumn_width>0) $col_mode = "x-c-s";
if ($leftcolumn_width>0 and $rightcolumn_width==0) $col_mode = "s-c-x";
if ($leftcolumn_width==0 and $rightcolumn_width==0) $col_mode = "x-c-x";

$leftinset_width = ($this->countModules('inset')>0 and !$editmode) ? $leftinset_width : "0";
$rightinset_width = ($this->countModules('inset2')>0 and !$editmode) ? $rightinset_width : "0";
$template_real_width = $template_width;
/* IE6 Template_width Fix */
if (rok_isIe(6)) $template_width = $template_width;
/* end */
$template_width = 'margin: 0 auto; width: ' . $template_width . 'px;';
$template_path = $this->baseurl . "/templates/" . $this->template;

//fix for IIS
if (!isset($_SERVER['REQUEST_URI']))
{
       $_SERVER['REQUEST_URI'] = substr($_SERVER['PHP_SELF'],1 );
       if (isset($_SERVER['QUERY_STRING'])) { $_SERVER['REQUEST_URI'].='?'.$_SERVER['QUERY_STRING']; }
}

$fullpath = 'http://'.JRequest::getVar('SERVER_NAME','','SERVER','STRING').$_SERVER['REQUEST_URI'];
$user =& JFactory::getUser();


									
function rok_isIe($version = false) {   

	$agent=$_SERVER['HTTP_USER_AGENT'];  

	$found = strpos($agent,'MSIE ');  
	if ($found) { 
	        if ($version) {
	            $ieversion = substr(substr($agent,$found+5),0,1);   
	            if ($ieversion == $version) return true;
	            else return false;
	        } else {
	            return true;
	        }
	        
        } else {
                return false;
        }
	if (stristr($agent, 'msie'.$ieversion)) return true;
	return false;        
}

function modulesClasses($case, $loaded_only = false) {
  global $mainmodulesBlocks;
  $document	= &JFactory::getDocument();

  $modules = $mainmodulesBlocks[$case];
  $loaded = 0;
  $loadedModule = array();
  $classes = array();

  foreach($mainmodulesBlocks[$case] as $block) if ($document->countModules($block)>0) { $loaded++; array_push($loadedModule, $block); }
  if ($loaded_only) return $loaded;

  $width = getModuleWidth($case, $loaded);

  switch ($loaded) {
    case 1:
      $classes[$loadedModule[0]][0] = 'full';
      $classes[$loadedModule[0]][1] = $width[0];
      break;
    case 2: 
      for ($i = 0; $i < count($loadedModule); $i++){
        if (!$i) {
		$classes[$loadedModule[$i]][0] = 'first';
		$classes[$loadedModule[$i]][1] = $width[0];
	}
        else {
		$classes[$loadedModule[$i]][0] = 'last';
		$classes[$loadedModule[$i]][1] = $width[1];
	}
      }
      break;
    case 3:
      for ($i = 0; $i < count($loadedModule); $i++){
        if (!$i) {
		$classes[$loadedModule[$i]][0] = 'first';
		$classes[$loadedModule[$i]][1] = $width[0];
	}
        elseif ($i == 1) {
		$classes[$loadedModule[$i]][0] = 'middle';
		$classes[$loadedModule[$i]][1] = $width[1];
	}
        else {
		$classes[$loadedModule[$i]][0] = 'last';
		$classes[$loadedModule[$i]][1] = $width[2];
	}
      }
      break;
  }
  
  return $classes;
  
}

function getModuleWidth($type, $loaded) {
	global $template_real_width, $leftcolumn_width, $rightcolumn_width, $leftbanner_width, $rightbanner_width;
	$width = ($template_real_width - 2) - (($leftcolumn_width == "0") ? 0 : $leftcolumn_width + 1) - (($rightcolumn_width == "0") ? 0 : $rightcolumn_width + 1) - $leftbanner_width - $rightbanner_width;

	$ieFix = ($leftbanner_width == "0") ? 0 : 0;
	$ieFix += ($rightbanner_width == "0") ? 0 : 0;

	$result = array();
	
	$width_original = $width;

	switch ($loaded) {
		case 1:
			$result[0] = $width_original;
			if (rok_isIe(6)) $result[0] -= $ieFix;
			break;
		case 2:
			$width = floor($width / 2);
			$result[0] = $width - 1;
			$result[1] = $width_original - ($result[0] + 2);
			if (rok_isIe(6)) {
				$result[0] -= 1;
				$result[1] -= $ieFix;
			}
 			break;
		case 3:
			$width = floor($width / 3);
			$result[0] = $result[1] = $width - 1;
			$result[2] = $width_original - ($result[0] + $result[1] + 2);
			if (rok_isIe(6)) {
				$result[0] -= 1;
				$result[1] -= 1;
				$result[2] -= $ieFix;
			}
			break;
	}
	
	return $result;
}

function getMainWidth(){
	$mainWidth = getModuleWidth(false, 1);
	$result = $mainWidth[0];
	
	return $result;
}

?>