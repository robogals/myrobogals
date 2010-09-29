<?php
/**
 * RokBox System Plugin
 *
 * @package		Joomla
 * @subpackage	RokBox System Plugin
 * @copyright Copyright (C) 2009 RocketTheme. All rights reserved.
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL, see RT-LICENSE.php
 * @author RocketTheme, LLC
 *
 * RokBox System Plugin includes:
 * ------------
 * SWFObject v1.5: SWFObject is (c) 2007 Geoff Stearns and is released under the MIT License:
 * http://www.opensource.org/licenses/mit-license.php
 * -------------
 * JW Player: JW Player is (c) released under CC by-nc-sa 2.0:
 * http://creativecommons.org/licenses/by-nc-sa/2.0/
 * 
 */

// no direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

jimport( 'joomla.plugin.plugin' );

/**
 * RokBox plugin
 *
 * @author		Djamil Legato <djamil@rockettheme.com>
 * @package		RokBox
 * @subpackage	System
 */
class  plgSystemRokBox extends JPlugin
{

	function plgSystemRokBox(& $subject, $config)
	{
		parent::__construct($subject, $config);
	}

	/**
	* Converting the site URL to fit to the HTTP request
	*
	*/
	function onAfterDispatch()
	{
		global $mainframe;

		$doc	=& JFactory::getDocument();
		$doctype	= $doc->getType();
		
		JHTML::_('behavior.mootools');

		// Only render for HTML output
		if ( $doctype !== 'html' ) { return; }

		$profiler	=& $_PROFILER;
		
		$theme = $this->params->get('theme', 'light');
		
		$rokboxJS = JURI::root(true)."/plugins/system/rokbox/rokbox.js";
		$remoteFolder = JURI::root(true)."/plugins/system/rokbox/themes";
		$localFolder = dirname($_SERVER['SCRIPT_FILENAME']) . "/plugins/system/rokbox/themes";
		if ($theme == 'custom') $theme = $this->params->get('custom-theme', 'sample');
		$config_exists = file_exists($localFolder . "/$theme/rokbox-config.js");
		
		$doc->addScript($rokboxJS);
		$doc->addScriptDeclaration("var rokboxPath = '".JURI::root(true)."/plugins/system/rokbox/';");
		$doc->addStyleSheet($remoteFolder . "/$theme/rokbox-style.css");

		// Load style for ie6 or ie7 if exist
		$iebrowser = $this->getBrowser();
		if ($iebrowser) {
			if (file_exists($localFolder . "/$theme/rokbox-style-ie$iebrowser.php")) {
			    $doc->addStyleSheet($remoteFolder . "/$theme/rokbox-style-ie$iebrowser.php");
			}
			elseif (file_exists($localFolder . "/$theme/rokbox-style-ie$iebrowser.css")) {
			    $doc->addStyleSheet($remoteFolder . "/$theme/rokbox-style-ie$iebrowser.css");
			}
		}
		
		if ($this->params->get('custom-legacy', 0) == 1) {
			$this->loadManualConfiguration($theme);
		} else {
			if ($config_exists) {
			    $doc->addScript($remoteFolder . "/$theme/rokbox-config.js");
			} else 
				$this->loadManualConfiguration($theme);
		}

	}
	
	function getBrowser() 
	{
		$agent = ( isset( $_SERVER['HTTP_USER_AGENT'] ) ) ? strtolower( $_SERVER['HTTP_USER_AGENT'] ) : false;
		$ie_version = false;
				
		if (eregi("msie", $agent) && !eregi("opera", $agent)){
            $val = explode(" ",stristr($agent, "msie"));
            $ver = explode(".", $val[1]);
			$ie_version = $ver[0];
			$ie_version = ereg_replace("[^0-9,.,a-z,A-Z]", "", $ie_version);
		}
		
		return $ie_version;
	}
	
	function loadManualConfiguration($theme)
	{
	    $doc	=& JFactory::getDocument();
	    
	    $config = "
		if (typeof(RokBox) !== 'undefined') {
			window.addEvent('domready', function() {
				var rokbox = new RokBox({
					'className': '".$this->params->get('classname', 'rokbox')."',
					'theme': '".$theme."',
					'transition': Fx.Transitions.".$this->params->get('transition', 'Quad.easeOut').",
					'duration': ".$this->params->get('duration', 200).",
					'chase': ".$this->params->get('chase', 40).",
					'frame-border': ".$this->params->get('frame-border', 0).",
					'content-padding': ".$this->params->get('content-padding', 0).",
					'arrows-height': ".$this->params->get('arrows-height', 50).",
					'effect': '".$this->params->get('effect', 'quicksilver')."',
					'captions': ".$this->params->get('captions', 1).",
					'captionsDelay': ".$this->params->get('captionsDelay', 800).",
					'scrolling': ".$this->params->get('scrolling', 0).",
					'keyEvents': ".$this->params->get('keyEvents', 1).",
					'overlay': {
						'background': '".$this->params->get('overlay_background', '#000000')."',
						'opacity': ".$this->params->get('overlay_opacity', '0.85').",
						'duration': ".$this->params->get('overlay_duration', '200').",
						'transition': Fx.Transitions.".$this->params->get('overlay_transition', 'Quad.easeInOut')."
					},
					'defaultSize': {
						'width': ".$this->params->get('width', '640').",
						'height': ".$this->params->get('height', '460')."
					},
					'autoplay': '".$this->params->get('autoplay', 'true')."',
					'controller': '".$this->params->get('controller', 'true')."',
					'bgcolor': '".$this->params->get('bgcolor', '#f3f3f3')."',
					'youtubeAutoplay': ".$this->params->get('ytautoplay', 1).",
					'youtubeHighQuality': ".$this->params->get('ythighquality', 0).",
					'vimeoColor': '".$this->params->get('vimeoColor', '00adef')."',
					'vimeoPortrait': ".$this->params->get('vimeoPortrait', 0).",
					'vimeoTitle': ".$this->params->get('vimeoTitle', 0).",
					'vimeoFullScreen': ".$this->params->get('vimeoFullScreen', 1).",
					'vimeoByline': ".$this->params->get('vimeoByline', 0)."
				});
			});
		};";
		$doc->addScriptDeclaration($config);
		
	}
}