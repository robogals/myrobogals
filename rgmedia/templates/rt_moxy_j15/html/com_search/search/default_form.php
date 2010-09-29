<?php // @version $Id: default_form.php 11917 2009-05-29 19:37:05Z ian $
defined('_JEXEC') or die('Restricted access');
?>

<form action="<?php echo JRoute::_( 'index.php?option=com_search#content' ) ?>" method="post" class="search_result">
<a name="form1"></a>
<fieldset class="word">
<label for="search_searchword"><?php echo JText::_('Search Keyword') ?> </label>
<input type="text" name="searchword" id="search_searchword"  maxlength="20" value="<?php echo $this->escape($this->searchword) ?>" class="inputbox" />
</fieldset>

<fieldset class="phrase">
<legend><?php echo JText::_('Search Parameters') ?></legend>
<label for="ordering" class="ordering"><?php echo JText::_('Ordering') ?>:</label>
<?php echo $this->lists['ordering']; ?>
<?php echo $this->lists['searchphrase']; ?>
</fieldset>

<?php if ($this->params->get('search_areas', 1)) : ?>
<fieldset class="only"><legend><?php echo JText::_('Search Only') ?>:</legend>
	<?php foreach ($this->searchareas['search'] as $val => $txt) : ?>
		<?php $checked = is_array($this->searchareas['active']) && in_array($val, $this->searchareas['active']) ? 'checked="true"' : ''; ?>
		<input type="checkbox" name="areas[]" value="<?php echo $val ?>" id="area_<?php echo $val ?>" <?php echo $checked ?> />
		<label for="area_<?php echo $val ?>">
		<?php echo JText::_($txt); ?>
		</label>
	<?php endforeach; ?>
</fieldset>
<?php endif; ?>
<p>
	<div class="readon-wrap1"><div class="readon1-l"></div><a class="readon-main"><span class="readon1-m"><span class="readon1-r"><input type="submit" name="Search" onClick="this.form.submit()" class="button" value="<?php echo JText::_( 'Search' );?>" /></span></span></a></div>
</p>


<?php if (count($this->results)) : ?>
<div class="display">
<label for="limit"><?php echo JText :: _('Display Num') ?></label>
	<?php echo $this->pagination->getLimitBox(); ?>
	<p>
		<?php echo $this->pagination->getPagesCounter(); ?>
	</p>
</div>
<?php endif; ?>

<input type="hidden" name="task"   value="search" />
</form>