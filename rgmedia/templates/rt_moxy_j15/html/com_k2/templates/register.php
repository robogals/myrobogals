<?php
/*
// "K2" Component by JoomlaWorks for Joomla! 1.5.x - Version 2.0
// Copyright (c) 2006 - 2009 JoomlaWorks Ltd. All rights reserved.
// Released under the GNU/GPL license: http://www.gnu.org/copyleft/gpl.html
// More info at http://www.joomlaworks.gr and http://k2.joomlaworks.gr
// Designed and developed by the JoomlaWorks team
// *** Last update: August 6th, 2009 ***
*/

// no direct access
defined('_JEXEC') or die ('Restricted access');

?>

<script type="text/javascript">
window.onDomReady(function(){
	document.formvalidator.setHandler('passverify', function (value) { return ($('password').value == value); }	);
});
</script>

<?php if(isset($this->message)) $this->display('message'); ?>

<form action="<?php echo JRoute::_( 'index.php?option=com_user' ); ?>" enctype="multipart/form-data" method="post" id="josForm" name="josForm" class="form-validate">

  <?php if ( $this->params->def( 'show_page_title', 1 ) ) : ?>
  <div class="componentheading<?php echo $this->escape($this->params->get('pageclass_sfx')); ?>">
  	<?php echo $this->escape($this->params->get('page_title')); ?>
  </div>
  <?php endif; ?>
  
  <table cellpadding="0" cellspacing="0" border="0" width="100%" class="contentpane">
    <tr>
      <td width="30%" height="40"><label id="namemsg" for="name"> <?php echo JText::_( 'Name' ); ?>: </label></td>
      <td><input type="text" name="name" id="name" size="40" value="<?php echo $this->escape($this->user->get( 'name' ));?>" class="inputbox required" maxlength="50" />
        * </td>
    </tr>
    <tr>
      <td height="40"><label id="usernamemsg" for="username"> <?php echo JText::_( 'User name' ); ?>: </label></td>
      <td><input type="text" id="username" name="username" size="40" value="<?php echo $this->escape($this->user->get( 'username' ));?>" class="inputbox required validate-username" maxlength="25" />
        * </td>
    </tr>
    <tr>
      <td height="40"><label id="emailmsg" for="email"> <?php echo JText::_( 'Email' ); ?>: </label></td>
      <td><input type="text" id="email" name="email" size="40" value="<?php echo $this->escape($this->user->get( 'email' ));?>" class="inputbox required validate-email" maxlength="100" />
        * </td>
    </tr>
    <tr>
      <td height="40"><label id="pwmsg" for="password"> <?php echo JText::_( 'Password' ); ?>: </label></td>
      <td><input class="inputbox required validate-password" type="password" id="password" name="password" size="40" value="" />
        * </td>
    </tr>
    <tr>
      <td height="40"><label id="pw2msg" for="password2"> <?php echo JText::_( 'Verify Password' ); ?>: </label></td>
      <td><input class="inputbox required validate-passverify" type="password" id="password2" name="password2" size="40" value="" />
        * </td>
    </tr>
  </table>
  
  <!-- K2 -->
  <table cellpadding="0" cellspacing="0" border="0" width="100%" class="contentpane">
    <tr>
      <td width="30%" height="40"><label id="gendermsg" for="gender"> <?php echo JText::_( 'Gender' ); ?>: </label></td>
      <td><?php echo $this->lists['gender']; ?></td>
    </tr>
    <tr>
      <td height="40"><label id="descriptionmsg" for="description"> <?php echo JText::_( 'Description' ); ?>: </label></td>
      <td><?php echo $this->editor;?></td>
    </tr>
    <tr>
      <td width="30%" height="40"><label id="imagemsg" for="image"> <?php echo JText::_( 'User Avatar' ); ?>: </label></td>
      <td><input type="file" id="image" name="image"/>
        <?php if ($this->K2User->image):?>
        <img class="k2AdminImage" src="<?php echo JURI::root().'media/k2/users/'.$this->K2User->image;?>" alt="<?php echo $this->user->name; ?>" />
        <input type="checkbox" name="del_image" id="del_image" />
        <label for="del_image"><?php echo JText::_('Upload new image to replace existing avatar or check this box to delete user avatar');?></label>
        <?php endif;?></td>
    </tr>
    <tr>
      <td width="30%" height="40"><label id="urlmsg" for="url"> <?php echo JText::_( 'Url' ); ?>: </label></td>
      <td><input type="text" size="50" value="<?php echo $this->K2User->url; ?>" name="url" id="url"/></td>
    </tr>
    <?php if (count($this->K2Plugins)):?>
    <?php foreach ($this->K2Plugins as $K2Plugin) : ?>
    <tr>
      <td colspan="2"><?php echo $K2Plugin->fields;?></td>
    </tr>
    <?php endforeach; ?>
    <?php endif;?>
    <tr>
      <td colspan="2" height="40"><?php echo JText::_( 'REGISTER_REQUIRED' ); ?></td>
    </tr>
  </table>
  
  <button class="button validate" type="submit"><?php echo JText::_('Register'); ?></button>
  <input type="hidden" name="task" value="register_save" />
  <input type="hidden" name="id" value="0" />
  <input type="hidden" name="gid" value="0" />
  <?php echo JHTML::_( 'form.token' ); ?>
</form>
