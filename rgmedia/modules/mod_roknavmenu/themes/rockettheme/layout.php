<?php
// no direct access
defined('_JEXEC') or die('Restricted access');
?>
<?php
if ( ! defined('modRokNavMenuShowItems') )
{
function showItem(&$item, &$menu) {
?>
<li <?php if($item->hasListItemClasses()) : ?>class="<?php echo $item->getListItemClasses();?>"<?php endif;?> <?php if(isset($item->css_id)):?>id="<?php echo $item->css_id;?>"<?php endif;?>>
	<?php if ($item->type == 'menuitem') : ?>
		<a <?php if($item->hasLinkClasses()):?>class="<?php echo $item->getLinkClasses();?>"<?php endif;?> <?php if($item->hasLink()):?>href="<?php echo $item->getLink();?>"<?php endif;?> <?php if(isset($item->target)):?>target="<?php echo $item->target;?>"<?php endif;?> <?php if(isset($item->onclick)):?>onclick="<?php echo $item->onclick;?>"<?php endif;?><?php if($item->hasLinkAttribs()):?> <?php echo $item->getLinkAttribs();?><?php endif;?>>
			<?php if (isset($item->image)):?><img alt="<?php echo $item->alias;?>" src="<?php echo $item->image;?>"/><?php endif; ?>
			<span <?php if($item->hasSpanClasses()):?>class="<?php echo $item->getSpanClasses();?>"<?php endif; ?>><?php echo $item->title;?></span>
		</a>
	<?php elseif($item->type == 'separator') : ?>
			<span <?php if($item->hasSpanClasses()):?>class="<?php echo $item->getSpanClasses();?>"<?php endif; ?>><?php echo $item->title;?></span>
	<?php endif; ?>
	<?php if ($item->hasChildren()): ?>
	<ul>
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
<ul class="menu<?php echo $menu->getParameter('class_sfx');?>" <?php if($menu->getParameter('tag_id') != null):?>id="<?php echo $menu->getParameter('tag_id');?>"<?php endif;?>>
	<?php foreach ($menu->getChildren() as $item) :  ?>
		<?php showItem($item, $menu); ?>
	<?php endforeach; ?>
</ul>
