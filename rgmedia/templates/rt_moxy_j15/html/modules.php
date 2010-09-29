<?php
/**
 * @version $Id: modules.php 5556 2006-10-23 19:56:02Z Jinx $
 * @package Joomla
 * @copyright Copyright (C) 2005 - 2006 Open Source Matters. All rights reserved.
 * @license GNU/GPL, see LICENSE.php
 * Joomla! is free software. This version may have been modified pursuant
 * to the GNU General Public License, and as distributed it includes or
 * is derivative of works licensed under the GNU General Public License or
 * other free or open source software licenses.
 * See COPYRIGHT.php for copyright notices and details.
 */

// no direct access
defined('_JEXEC') or die('Restricted access');

/**
 * This is a file to add template specific chrome to module rendering.  To use it you would
 * set the style attribute for the given module(s) include in your template to use the style
 * for each given modChrome function.
 *
 * eg.  To render a module mod_test in the sliders style, you would use the following include:
 * <jdoc:include type="module" name="test" style="slider" />
 *
 * This gives template designers ultimate control over how modules are rendered.
 *
 * NOTICE: All chrome wrapping methods should be named: modChrome_{STYLE} and take the same
 * two arguments.
 */

/*
 * Module chrome for rendering the module in a slider
 */

function modChrome_submenu($module, &$params, &$attribs)
{
	global $Itemid;
	
	$start	= $params->get('startLevel');
	
	$tabmenu = &JSite::getMenu();
	$item = $tabmenu->getItem($Itemid);
	

	if (isset($item)) {
		$tparent = $tabmenu->getItem($item->parent);
		$menuname = "";

	    	while ($tparent != null) {
	    		$item = $tabmenu->getItem($item->parent);
	    		if ($tparent->parent == $start-1) break;
				$tparent = $tabmenu->getItem($item->parent);
				
	    	}
	    	if (!empty ($module->content) && strlen($module->content) > 40) { ?>
			<div class="side-mod">
				<div class="moduletable">
					<h3 class="module-title"><?php echo $item->name; ?> Menu</h3>
					<?php echo $module->content; ?>
				</div>
			</div>
	    	<?php 
		    }
	}
}

function modChrome_showcase($module, &$params, &$attribs)
{
    	
	if (!empty ($module->content)) : ?>
	<div class="<?php echo $params->get('moduleclass_sfx'); ?>">
		<div class="moduletable">
			<div class="module-top"><div class="module-top2"></div><div class="module-top3"></div></div>
				<div class="module-inner">
					<?php if ($module->showtitle != 0) : ?>
					<h3 class="module-title"><?php echo $module->title; ?></h3>
					<?php endif; ?>
					<?php echo $module->content; ?>
				</div>
			<div class="module-bottom"><div class="module-bottom2"></div><div class="module-bottom3"></div></div>
		</div>
	</div>
	<?php endif;
}

function modChrome_main($module, &$params, &$attribs)
{
	
$moduleclass_sfx = $params->get('moduleclass_sfx',false);
	
	if (!empty ($module->content) and $moduleclass_sfx) : ?>
	<div class="<?php echo $moduleclass_sfx; ?>">
		<div class="moduletable">
			<div class="module-surround">
				<div class="module-grad"></div>
				<div class="module-surround2"></div><div class="module-surround3"></div><div class="module-surround4"></div><div class="module-surround5"></div>
				<div class="module-inner">
					<?php if ($module->showtitle != 0) : ?>
					<h3 class="module-title"><?php echo $module->title; ?></h3>
					<?php endif; ?>
					<?php echo $module->content; ?>
				</div>
			</div>
		</div>
	</div>
	<?php elseif (!empty ($module->content)) : ?>
	<div class="moduletable">
		<?php if ($module->showtitle != 0) : ?>
		<h3 class="module-title"><?php echo $module->title; ?></h3>
		<?php endif; ?>
		<?php echo $module->content; ?>
	</div>
	<?php endif;
}

?>