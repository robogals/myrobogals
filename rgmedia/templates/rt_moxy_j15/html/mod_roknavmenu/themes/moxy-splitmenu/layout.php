<?php
// no direct access
defined('_JEXEC') or die('Restricted access');
if (!defined('SPLITMENU_TEMPLATE')) define('SPLITMENU_TEMPLATE','rt_moxy_j15');

if (!class_exists('SplitmenuScriptLoader')) {
    class SplitmenuScriptLoader { 
    	function loadScripts(&$menu)
    	{
    		$doc = &JFactory::getDocument();
		
    		JHTML::_('behavior.mootools');
    		if (SplitmenuScriptLoader::isIe(6)) {
                $doc->addScript(JURI::Root(true).'/modules/mod_roknavmenu/themes/fusion/js/sfhover.js');
    	    }
    	}
	
    	function isIe($version = false) {   
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
    }
}

SplitmenuScriptLoader::loadScripts($menu);

global $activeid;
$activeid = $menu->getParameter('splitmenu_fusion_enable_current_id',0) == 0 ? false : true;

?>
<?php
if ( ! defined('modRokNavMenuShowItems') )
{
function showItem(&$item, &$menu) {
    
    global $activeid;
   
    //not so elegant solution to add subtext
    $item->subtext = $item->getParameter('splitmenu_item_subtext','');
    if ($item->subtext=='') $item->subtext = false;
    else $item->addLinkClass('subtext');
?>
<li <?php if($item->hasListItemClasses()) : ?>class="<?php echo $item->getListItemClasses()?>"<?php endif;?> <?php if(isset($item->css_id) && $activeid):?>id="<?php echo $item->css_id;?>"<?php endif;?>>
	<?php if ($item->type == 'menuitem') : ?>
		<a <?php if($item->hasLinkClasses()):?>class="<?php echo $item->getLinkClasses();?>"<?php endif;?> <?php if($item->hasLink()):?>href="<?php echo $item->getLink();?>"<?php endif;?> <?php if(isset($item->target)):?>target="<?php echo $item->target;?>"<?php endif;?> <?php if(isset($item->onclick)):?>onclick="<?php echo $item->onclick;?>"<?php endif;?><?php if($item->hasLinkAttribs()):?> <?php echo $item->getLinkAttribs();?><?php endif;?>>
			<span>
			<?php echo $item->title;?>
			<?php if (!empty($item->subtext)) :?>
			<em><?php echo $item->subtext; ?></em>    
			<?php endif; ?>    
			</span>
		</a>
	<?php elseif($item->type == 'separator') : ?>
		<span <?php if($item->hasLinkClasses()):?>class="<?php echo $item->getLinkClasses();?> nolink"<?php endif;?>>
		    <span>
		    <?php echo $item->title;?>
		    <?php if (!empty($item->subtext)) :?>
			<em><?php echo $item->subtext; ?></em>    
			<?php endif; ?>
		    </span>
		</span>
	<?php endif; ?>
	<?php if ($item->hasChildren()): ?>
	<ul class="level<?php echo intval($item->level)+2; ?>">
		<?php foreach ($item->getChildren() as $child) : ?>			
			<?php showItem($child, $menu); ?>
		<?php endforeach; ?>
	</ul>
	<?php endif; ?>
	
</li>	
<?php
} 
define('modRokNavMenuShowItems', true);
}
?>
<ul class="menu<?php echo $menu->getParameter('class_sfx');?> level1" <?php if($menu->getParameter('tag_id') != null):?>id="<?php echo $menu->getParameter('tag_id');?>"<?php endif;?>>
	<?php foreach ($menu->getChildren() as $item) :  ?>
		<?php showItem($item, $menu); ?>
	<?php endforeach; ?>
</ul>
