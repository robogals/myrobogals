<?php // @version $Id: default_address.php 12387 2009-06-30 01:17:44Z ian $
defined('_JEXEC') or die('Restricted access');
?>

<div class="main-address">
  <!--open contact_address div -->
<?php

$show_address = (($this->contact->params->get('address_check') > 0) &&
		($this->contact->address || $this->contact->suburb || $this->contact->state || $this->contact->country || $this->contact->postcode)) ||
		(($this->contact->email_to && $this->contact->params->get('show_email')) || $this->contact->telephone || $this->contact->fax );

if ($show_address):
	echo '<div class="contact-address">';
endif;

if (($this->contact->params->get('address_check') > 0) && ($this->contact->address || $this->contact->suburb || $this->contact->state || $this->contact->country || $this->contact->postcode)) :
	if ( $this->contact->params->get('address_check') > 0) :
		if (( $this->contact->params->get('contact_icons') ==0) || ($this->contact->params->get('contact_icons') ==1)):
			echo '<div class="icon">'.$this->contact->params->get('marker_address').'</div>';
		endif;
	endif;

	if ($this->contact->address && $this->contact->params->get('show_street_address')) :
	   	echo '<div class="surround"><div class="street-address"><div class="data">';
	    echo nl2br($this->escape($this->contact->address)).'<br /></div></div></div>';
	endif;

	if ($this->contact->suburb && $this->contact->params->get('show_suburb')) :
		echo '<div class="surround"><div class="suburb"><div class="icon">&nbsp;</div><div class="data">'.$this->escape($this->contact->suburb).'</div></div></div>';
	endif;

	if ($this->contact->state && $this->contact->params->get('show_state')) :
		echo '<div class="surround"><div class="state"><div class="icon">&nbsp;</div><div class="data">'.$this->escape($this->contact->state).'</div></div></div>';
	endif;

	if ($this->contact->country && $this->contact->params->get('show_country')) :
		echo '<div class="surround"><div class="country"><div class="icon">&nbsp;</div><div class="data">'.$this->escape($this->contact->country).'</div></div></div>';
	endif;

	if ($this->contact->postcode && $this->contact->params->get('show_postcode')) :
		echo '<div class="surround"><div class="postcode"><div class="icon">&nbsp;</div><div class="data">'.$this->escape($this->contact->postcode).'</div></div></div>';
	endif;
	
	echo '<br />';

endif;

if (($this->contact->email_to && $this->contact->params->get('show_email')) || $this->contact->telephone || $this->contact->fax ) :
	echo '<div class="other">';
	if ($this->contact->email_to && $this->contact->params->get('show_email')) :
		echo '<div class="surround"><div class="email">';
		if (( $this->contact->params->get('contact_icons') ==0) || ( $this->contact->params->get('contact_icons') ==1)):
			echo '<div class="icon">'.$this->contact->params->get('marker_email').'</div>';
		endif;

		echo '<div class="data">'.$this->contact->email_to.'</div>';
		echo '</div></div>';
	endif;

	if ($this->contact->telephone && $this->contact->params->get('show_telephone')) :
		echo '<div class="surround"><div class="telephone">';
		if (( $this->contact->params->get('contact_icons') ==0) || ( $this->contact->params->get('contact_icons') ==1)):
			echo '<div class="icon">'.$this->contact->params->get('marker_telephone').'</div>';
		endif;
		echo '<div class="data">'.$this->escape($this->contact->telephone).'</div>';
		echo '</div></div>';
	endif;

	if ($this->contact->fax && $this->contact->params->get('show_fax')) :
		echo '<div class="surround"><div class="fax">';
		if (( $this->contact->params->get('contact_icons') ==0) || ( $this->contact->params->get('contact_icons') ==1)):
			echo '<div class="icon">'.$this->contact->params->get('marker_fax').'</div>';
		endif;
		echo '<div class="data">'.$this->escape($this->contact->fax).'</div>';
		echo '</div></div>';
	endif;
	
	if ($this->contact->mobile && $this->contact->params->get('show_mobile')) :
		echo '<div class="surround"><div class="mobile">';
		if (( $this->contact->params->get('contact_icons') ==0) || ( $this->contact->params->get('contact_icons') ==1)):
			echo '<div class="icon">'.$this->contact->params->get('marker_mobile').'</div>';
		endif;
		echo '<div class="data">'.$this->escape($this->contact->mobile).'</div>';
		echo '</div></div>';
	endif;

	if ($this->contact->webpage && $this->contact->params->get('show_webpage')) :
		echo '<div class="surround"><div class="postcode"><div class="icon">&nbsp;</div><div class="data"><a href="'.$this->escape($this->contact->webpage).'" target="_blank"> '.$this->escape($this->contact->webpage).'</a></div></div></div>';
	endif;

	echo '</div>';
endif;

if ($show_address):
	echo '</div>';
endif; ?>

</div>
<!--close contact_address div -->

<?php if ($this->contact->misc && $this->contact->params->get('show_misc')) : 
	echo '<br />';
	echo '<div class="surround"><div class="mobile">';
	if (( $this->contact->params->get('contact_icons') ==0) || ( $this->contact->params->get('contact_icons') ==1)):		
		echo '<div class="icon">'.$this->contact->params->get('marker_misc').'</div>';
	endif;
	echo '<div class="data">'.$this->contact->misc.'</div>';
	echo '</div></div>';
endif; ?>

<br />