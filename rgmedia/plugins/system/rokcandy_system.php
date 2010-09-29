<?php
/**
 * RokCandy Macros RokCandy Macro System Plugin
 *
 * @package		Joomla
 * @subpackage	RokCandy Macros
 * @copyright Copyright (C) 2009 RocketTheme. All rights reserved.
 * @license http://www.gnu.org/copyleft/gpl.html GNU/GPL, see LICENSE.php
 * @author RocketTheme, LLC
 */

// no direct access
defined( '_JEXEC' ) or die( 'Restricted access' );

require_once (JPATH_ADMINISTRATOR.DS.'components'.DS.'com_rokcandy'.DS.'helpers'.DS.'rokcandyhelper.php' );

class plgSystemRokCandy_System extends JPlugin {
    
    var $_initialized = false;
	var $_instanceId = 0;
	var $_library;
	var $_debug;

	function plgSystemRokCandy_System(& $subject, $config) {
		parent :: __construct($subject, $config);
		$this->_instanceId = rand(1000, 9999);
		
		$this->_debug = JRequest::getVar('debug_rokcandy') == true ? true : false;
    }
	
	function onAfterRoute() {
		$this->_initialize();
	}
	
	function _PHP4() {
  		if (version_compare( phpversion(), '5.0' ) < 0) {
  			if (!$this->_initialized) {
  			  //Something is wrong with PHP4... let's repeat the work...	
  				$this->_instanceId = rand(1000, 9999);
  				$this->_initialize();
  			}
  			return true;
  		} else {
  		  return false;
  		}  		
    }
    
    function _initialize() {
        
		if ($this->_initialized) {
			JError::raiseWarning( '1' , 'RokCandy instanceId=' . $this->_instanceId . ' was initialized already');
			return true;
		}
		
		$document = & JFactory :: getDocument();
		$doctype = $document->getType();
		$this->_library = RokCandyHelper::getMacros();
    }
    
    // Do BBCode replacements on the whole page
	function onAfterRender() {
	    
		// don't run if disabled overrides are true
	    if ($this->_shouldProcess()) return;
	    
		$this->_PHP4();

		$document = & JFactory::getDocument();
		$doctype = $document->getType();
		if ($doctype == 'html') {
			$body = JResponse::getBody();
			if ($this->_replaceCode($body)) {
				JResponse::setBody($body);
			}
		}
	}
	
	//process on content items first
	function onPrepareContent( &$article, &$params, $limitstart=0)
	{
		// don't execute if contentPlugin disabled in system config
		$candy_params =& JComponentHelper::getParams('com_rokcandy');

		if ($candy_params->get("contentPlugin",1)==0) return;
		
		// don't run if disabled overrides are true
	    if ($this->_shouldProcess()) return;
	    
		$this->_PHP4();

		if ($this->_replaceCode($article->text)) {
		    return $article->text;
		}
   
    }
	
	function _shouldProcess() {
	    global $mainframe;
	    
	    $params =& JComponentHelper::getParams('com_rokcandy');
	    
	    //don't run if in edit mode and flag enabled
	    if (JRequest::getCmd('task') == 'edit' && $params->get('editenabled',0) == 0) return true;
	    
	    // don't process if in list view:
	    if (JRequest::getCmd('task') == 'list' && JRequest::getCmd('option') == "com_rokcandy") return true;	  
	      
	    //don't run in admin
		if ($mainframe->isAdmin() && $params->get('adminenabled',0)==0) return true;

	    // process manual overrides
	    $flag = false;
	    $is_disabled = $params->get('disabled');
	    if ($is_disabled != "") {
	        $disabled_entries = explode ("\n",$params->get('disabled'));
	        foreach ($disabled_entries as $entries) {
	            $checks = explode ("&",$entries);
	            if (count($checks) > 0) {
	                $flag = true;
    	            foreach ($checks as $check) {
    	                $bits = explode ("=",$check);
    	                if ((count($bits) == 2) && ($bits[1] != "") && (JRequest::getVar($bits[0]) == $bits[1])) {
    	                    $flag = true;
    	                }
    	                else {
    	                    $flag = false;
    	                    break;
    	                }
    	                
    	            }
                }
                if ($flag == true)
           			return true;
	        }
	    }
	    return $flag;
	}
	
	function _replaceCode(&$body) {
  

	    foreach ($this->_library as $key => $val) {
			$search         = array();
			$replace        = array();
			$tokens         = array();
            
			$opentag = substr($key,0,strpos($key,']')+1);
			$partial_open_tag = substr($opentag,0,(strpos($opentag,' '))?strpos($opentag,' '):strpos($opentag,']'));
			$tokened_opentag =  preg_replace('/\{([a-zA-Z0-9_]+)\}/', '(?P<$1>.*?)',$opentag);
			$tag_contents = substr($key, strpos($key,']')+1, strrpos($key,'[') - (strpos($key,']')+1));
			$tokened_tag_contens = preg_replace('/\{([a-zA-Z0-9_]+)\}/', '(?P<$1>((?!'.$partial_open_tag.').)*?)',$tag_contents);
			$closetag = substr($key,strrpos($key,'['),strrpos($key,']')-strrpos($key,'[')+1);
			$escaped_key = $this->_addEscapes($tokened_opentag.$tokened_tag_contens.$closetag);
			$final_tag_patern = "%".$escaped_key."%s";
	        
	        if ($this->_debug) var_dump ($final_tag_patern);
	        preg_match_all($final_tag_patern, $body, $results);
	        if (!empty($results[0])) {
	            if ($this->_debug) var_dump ($results);
    	        $search = array_merge($search, $results[0]);
    	        foreach ($results as $k => $v) {
    	            if (!is_numeric($k)) {
    	                $tokens[] = $k;
    	            }
    	        }
                for($i=0;$i< count($results[0]);$i++) {
                    $tmpval = $val;
                    foreach ($tokens as $token) {
                        $tmpval = str_replace("{".$token."}",$results[$token][$i],$tmpval);
                    }
                    $replace[] = $tmpval;
                }
	        }
	        $body = str_replace($search,$replace,$body);
	    }
        
        return true;
	}
	
	function _addEscapes($fullstring) {
		$fullstring            = str_replace("\\","\\\\",$fullstring);
		$fullstring            = str_replace("[","\[",$fullstring);
		$fullstring            = str_replace("]","\\]",$fullstring);
		return $fullstring;
	}
	    
    
    
    
    function _readIniFile($path, $library) {
        jimport( 'joomla.filesystem.file' );
        $content = JFile::read($path);
        $data = explode("\n",$content);

		foreach ($data as $line) {
		    //skip comments
		    if (strpos($line,"#")!==0 and trim($line)!="" ) {
		       $div = strpos($line,"]=");
		       $library[substr($line,0,$div+1)] = substr($line,$div+2);
		    }
		}
		return $library;
    }

}