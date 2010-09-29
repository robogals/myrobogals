<?php
defined( '_JEXEC' ) or die( 'Restricted index access' );

$cookie_prefix = "moxy-";
$cookie_time = time()+31536000;
$template_properties = array('fontstyle','fontfamily','tstyle','mtype');

foreach ($template_properties as $tprop) {
    $my_session = &JFactory::getSession();
	if (isset($_REQUEST[$tprop])) {
	    $$tprop = htmlentities(JRequest::getString($tprop, null, 'get'));

		// support the font size toggler
		if ($$tprop=="f-smaller" || $$tprop =="f-larger") {
			$fsize = "f-default";
	
		 	if ($my_session->get($cookie_prefix. $tprop)) {
				 $fsize = $my_session->get($cookie_prefix. $tprop);
			 } elseif (isset($_COOKIE[$cookie_prefix. $tprop])) {
				 $fsize = htmlentities(JRequest::getVar($cookie_prefix. $tprop, '', 'COOKIE', 'STRING'));
			 }
			if ($$tprop=="f-smaller" && $fsize=="f-default") $$tprop = "f-small";
			elseif ($$tprop=="f-smaller" && $fsize=="f-small") $$tprop = "f-small";
			elseif ($$tprop=="f-smaller" && $fsize=="f-large") $$tprop = "f-default";
			elseif ($$tprop=="f-larger" && $fsize=="f-large") $$tprop = "f-large";
			elseif ($$tprop=="f-larger" && $fsize=="f-default") $$tprop = "f-large";
			elseif ($$tprop=="f-larger" && $fsize=="f-small") $$tprop = "f-default";
		}	
	
    	$my_session->set($cookie_prefix.$tprop, $$tprop);
    	setcookie ($cookie_prefix. $tprop, $$tprop, $cookie_time, '/', false);   
    	global $$tprop; 
    }
}

?>
