<?php // @version $Id: default.php 10381 2008-06-01 03:35:53Z pasamio $
defined('_JEXEC') or die('Restricted access');
?>

<?php if (count($list)) : ?>
<div class="<?php echo $params->get('pageclass_sfx'); ?>">
	<ul class="latestnews">
		<?php foreach ($list as $item) : ?>
		<li class="latestnews">
			<a href="<?php echo $item->link; ?>" class="latestnews"><?php echo $item->text; ?></a>
		</li>
		<?php endforeach; ?>
	</ul>
</div>
<?php endif;
