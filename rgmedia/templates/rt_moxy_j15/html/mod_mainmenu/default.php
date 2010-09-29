<?php

// no direct access
defined('_JEXEC') or die('Restricted access');

$index = 0;

if ( ! defined('modMainMenuXMLCallbackDefined') )
{
function modMainMenuXMLCallback(&$node, $args)
{
	
	global $mainframe, $index;
	$user	= &JFactory::getUser();
	$menu	= &JSite::getMenu();
	$active	= $menu->getActive();
	$path	= isset($active) ? array_reverse($active->tree) : null;
	
	$mcolors = $mainframe->get('mcolors');
	$default_color = $mainframe->get('default_color');
	
	if (!isset($index)) $index = 0;

	if (($args['end']) && ($node->attributes('level') >= $args['end']))
	{
		$children = $node->children();
		foreach ($node->children() as $child)
		{
			if ($child->name() == 'ul') {
				$node->removeChild($child);
			}
		}
	}

	if ($node->name() == 'ul') {
		foreach ($node->children() as $child)
		{
			if ($child->attributes('access') > $user->get('aid', 0)) {
				$node->removeChild($child);
			}
		}
	}

	if (($node->name() == 'li') && isset($node->ul)) {
		$node->addAttribute('class', 'parent');
		$children = $node->children();
		if ($node->attributes('level') == 1) {
			if ($children[0]->name() == 'a' or $children[0]->name() == 'span') {
				if ($children[0]->attributes('class')) {
					$children[0]->addAttribute('class', $children[0]->attributes('class').' topdaddy');
				} else {
					$children[0]->addAttribute('class', 'topdaddy');
				}
			}
		} else {
			if ($children[0]->name() == 'a' or $children[0]->name() == 'span') {
				if ($children[0]->attributes('class')) {
					$children[0]->addAttribute('class', $children[0]->attributes('class').' daddy');
				} else {
					$children[0]->addAttribute('class', 'daddy');
				}
			}
		}
		
	}
	
	if ($node->name() == 'li' && $node->attributes('level') == 1) {
		
		if (isset($mcolors[$index])) {
			$color = $mcolors[$index];
		} else {
			$color = $default_color;
		}
		
		if ($node->attributes('class')) {
			$node->addAttribute('class', $node->attributes('class').' '.$color);
		} else {
			$node->addAttribute('class', $color);
		}
		$index++;
	}

	if (isset($path) && (in_array($node->attributes('id'), $path) || in_array($node->attributes('rel'), $path)))
	{
		if ($node->attributes('class')) {
			$node->addAttribute('class', $node->attributes('class').' active');
		} else {
			$node->addAttribute('class', 'active');
		}
	}
	else
	{
		if (isset($args['children']) && !$args['children'])
		{
			$children = $node->children();
			foreach ($node->children() as $child)
			{
				if ($child->name() == 'ul') {
					$node->removeChild($child);
				}
			}
		}
	}

	if (($node->name() == 'li') && ($id = $node->attributes('id'))) {
		if ($node->attributes('class')) {
			$node->addAttribute('class', $node->attributes('class').' item'.$id);
		} else {
			$node->addAttribute('class', 'item'.$id);
		}
	}

	if (isset($path) && $node->attributes('id') == $path[0]) {
		$node->addAttribute('id', 'current');
	} else {
		$node->removeAttribute('id');
	}
	$node->removeAttribute('rel');
	$node->removeAttribute('level');
	$node->removeAttribute('access');
}
	define('modMainMenuXMLCallbackDefined', true);
}

modMainMenuHelper::render($params, 'modMainMenuXMLCallback');
