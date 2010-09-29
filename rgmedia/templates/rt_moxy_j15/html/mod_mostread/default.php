<?php // no direct access
defined('_JEXEC') or die('Restricted access'); ?>
<ul class="mostread">
<?php foreach ($list as $item) : ?>
	<li class="mostread">
		<a href="<?php echo $item->link; ?>" class="mostread">
			<?php echo $item->text; ?></a>
	</li>
<?php endforeach; ?>
</ul>