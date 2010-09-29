<?php
/**
 * RokAjaxSearch Module
 *
 * @package		Joomla
 * @subpackage	RokAjaxSearch Module
 * @copyright Copyright (C) 2009 RocketTheme. All rights reserved.
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL, see RT-LICENSE.php
 * @author RocketTheme, LLC
 *
 *
 * Inspired on PixSearch Joomla! module by Henrik Hussfelt <henrik@pixpro.net>
 */

defined('_JEXEC') or die('Restricted access');

class modRokajaxsearchHelper {
	function inizialize($css_style, $offset, &$params){
		global $mainframe;
		$theme = $params->get('theme', 'blue');
		
		JHTML::_('behavior.mootools');
		$doc =& JFactory::getDocument();
		
		$css = modRokajaxsearchHelper::getCSSPath('rokajaxsearch.css', 'mod_rokajaxsearch');
		$iebrowser = modRokajaxsearchHelper::getBrowser();
		
		if($css_style == 1 && $css != false) {
			$doc->addStyleSheet($css);
			$doc->addStyleSheet(JURI::Root(true)."/modules/mod_rokajaxsearch/themes/$theme/rokajaxsearch-theme.css");
			
			if ($iebrowser) {
				$style = JURI::Root(true)."/modules/mod_rokajaxsearch/themes/$theme/rokajaxsearch-theme-ie$iebrowser";
				$check = dirname(__FILE__)."/themes/$theme/rokajaxsearch-theme-ie$iebrowser";

				if (file_exists($check.".css")) $doc->addStyleSheet($style.".css");
				elseif (file_exists($check.".php")) $doc->addStyleSheet($style.".php");
			}
			
		}
		$doc->addScript(JURI::Root(true)."/modules/mod_rokajaxsearch/js/rokajaxsearch.js");

		
		/* RokAjaxSearch Init */
		$websearch = ($params->get('websearch', 0)) ? 1 : 0;
		$blogsearch = ($params->get('blogsearch', 0)) ? 1 : 0;
		$imagesearch = ($params->get('imagesearch', 0)) ? 1 : 0;
		$videosearch = ($params->get('videosearch', 0)) ? 1 : 0;
		$ras_init = "window.addEvent((window.webkit) ? 'load' : 'domready', function() {
				window.rokajaxsearch = new RokAjaxSearch({
					'results': '".JText::_('RESULTS')."',
					'close': '',
					'websearch': ".$websearch.",
					'blogsearch': ".$blogsearch.",
					'imagesearch': ".$imagesearch.",
					'videosearch': ".$videosearch.",
					'imagesize': '".$params->get('image_size', 'MEDIUM')."',
					'safesearch': '".$params->get('safesearch', 'MODERATE')."',
					'search': '".JText::_('SEARCH')."',
					'readmore': '".JText::_('READMORE')."',
					'noresults': '".JText::_('NORESULTS')."',
					'advsearch': '".JText::_('ADVSEARCH')."',
					'page': '".JText::_('PAGE')."',
					'page_of': '".JText::_('PAGE_OF')."',
					'searchlink': '".JURI::Base().htmlentities($params->get('search_page'))."',
					'advsearchlink': '".JURI::Base().htmlentities($params->get('adv_search_page'))."',
					'uribase': '".JURI::Base()."',
					'limit': '".$params->get('limit', '10')."',
					'perpage': '".$params->get('perpage', '3')."',
					'ordering': '".$params->get('ordering', 'newest')."',
					'phrase': '".$params->get('searchphrase', 'any')."',
					'hidedivs': '".$params->get('hide_divs', '')."',
					'includelink': ".$params->get('include_link', 1).",
					'viewall': '".JText::_('VIEWALL')."',
					'estimated': '".JText::_('ESTIMATED')."',
					'showestimated': ".$params->get('show_estimated', 1).",
					'showpagination': ".$params->get('show_pagination', 1).",
					'showcategory': ".$params->get('include_category', 1).",
					'showreadmore': ".$params->get('show_readmore', 1).",
					'showdescription': ".$params->get('show_description', 1)."
				});
			});";
		$doc->addScriptDeclaration($ras_init);
		
		
		/* Google API */
		if ($params->get('websearch', 0) == 1 && $params->get('websearch_api') != '') { 
			$doc->addScript("http://www.google.com/jsapi?key=".$params->get('websearch_api'));
			$doc->addScriptDeclaration("google.load('search', '1.0', {nocss: true});");
		}
	}
	
	function getCSSPath($cssfile, $module) {
		global $mainframe;
		$tPath = 'templates/'.$mainframe->getTemplate().'/css/' . $cssfile . '-disabled';
		$bPath = 'modules/'.$module.'/css/' . $cssfile;

		// If the template is asking for it, 
		// don't include default rokajaxsearch css
		if (!file_exists(JPATH_BASE.DS.$tPath)) {
			return JURI::Base().'/'.$bPath;
		} else {
			return false;
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
	
}