from django.db import models
from pytz import timezone, utc

class JosContent(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=765)
    alias = models.CharField(max_length=765)
    title_alias = models.CharField(max_length=765)
    introtext = models.TextField()
    fulltext = models.TextField()
    state = models.IntegerField()
    sectionid = models.IntegerField()
    mask = models.IntegerField()
    catid = models.IntegerField()
    created = models.DateTimeField()
    created_by = models.IntegerField()
    created_by_alias = models.CharField(max_length=765)
    modified = models.DateTimeField()
    modified_by = models.IntegerField()
    checked_out = models.IntegerField()
    checked_out_time = models.DateTimeField()
    publish_up = models.DateTimeField()
    publish_down = models.DateTimeField()
    images = models.TextField()
    urls = models.TextField()
    attribs = models.TextField()
    version = models.IntegerField()
    parentid = models.IntegerField()
    ordering = models.IntegerField()
    metakey = models.TextField()
    metadesc = models.TextField()
    access = models.IntegerField()
    hits = models.IntegerField()
    metadata = models.TextField()

    def __unicode__(self):
    	return self.title

    class Meta:
        db_table = u'jos_content'

class JosDonate(models.Model):
    id = models.IntegerField(primary_key=True)
    active = models.IntegerField()
    options = models.TextField(blank=True)
    class Meta:
        db_table = u'jos_donate'

class JosUsers(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=765)
    username = models.CharField(max_length=450)
    email = models.CharField(max_length=300)
    password = models.CharField(max_length=300)
    usertype = models.CharField(max_length=75)
    block = models.IntegerField()
    sendemail = models.IntegerField(null=True, db_column='sendEmail', blank=True) # Field name made lowercase.
    gid = models.IntegerField()
    registerdate = models.DateTimeField(db_column='registerDate') # Field name made lowercase.
    lastvisitdate = models.DateTimeField(db_column='lastvisitDate') # Field name made lowercase.
    activation = models.CharField(max_length=300)
    params = models.TextField()

    def __unicode__(self):
    	return self.username

    class Meta:
        db_table = u'jos_users'

class JosDonations(models.Model):
    PAYMENT_STATUSES = (
        ('PENDING', 'PENDING'),
        ('Completed ', 'Completed '),
        ('Pending echeck', 'Pending echeck'),
    )

    id = models.IntegerField(primary_key=True)
    firstname = models.CharField(max_length=765, verbose_name="Name")
    lastname = models.CharField(max_length=765)
    title = models.CharField(max_length=765)
    organization = models.CharField(max_length=765, verbose_name="Age")
    credit_card = models.CharField(max_length=48)
    expiration = models.CharField(max_length=12)
    expiration_month = models.CharField(max_length=12)
    expiration_year = models.CharField(max_length=12)
    cvv = models.CharField(max_length=9)
    address1 = models.CharField(max_length=765)
    address2 = models.CharField(max_length=765)
    city = models.CharField(max_length=765)
    state = models.CharField(max_length=765)
    country = models.CharField(max_length=765)
    postalcode = models.CharField(max_length=30)
    email = models.CharField(max_length=765)
    phone = models.CharField(max_length=765)
    extension = models.CharField(max_length=765)
    comments = models.TextField()
    amount = models.FloatField()
    xaction_result = models.CharField(max_length=765, verbose_name="Payment status")
    # choices=PAYMENT_STATUSES)
    xaction_id = models.CharField(max_length=765, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    card_type = models.CharField(max_length=765, blank=True)
    country_currency = models.CharField(max_length=15, blank=True)
    length = models.CharField(max_length=60, blank=True)
    unit = models.CharField(max_length=60, blank=True)
    duration = models.CharField(max_length=60, blank=True)
    configuration_id = models.IntegerField(null=True, blank=True)
    program = models.CharField(max_length=765, blank=True)
    matching_company = models.CharField(max_length=765, blank=True)
    anonymous_donation = models.IntegerField(null=True, blank=True)
    from_company = models.IntegerField(null=True, blank=True)
    referral_source = models.CharField(max_length=765, blank=True)
    tribute_recipient_first = models.CharField(max_length=765, blank=True)
    tribute_recipient_last = models.CharField(max_length=765, blank=True)
    tribute_type = models.CharField(max_length=765, blank=True)
    acknowledgee_sendmail = models.CharField(max_length=765, blank=True)
    acknowledgee_first = models.CharField(max_length=765, blank=True)
    acknowledgee_last = models.CharField(max_length=765, blank=True)
    acknowledgee_address1 = models.CharField(max_length=765, blank=True)
    acknowledgee_address2 = models.CharField(max_length=765, blank=True)
    acknowledgee_city = models.CharField(max_length=765, blank=True)
    acknowledgee_state = models.CharField(max_length=765, blank=True)
    acknowledgee_zip = models.CharField(max_length=765, blank=True)
    acknowledgee_phone = models.CharField(max_length=765, blank=True)
    acknowledgee_email = models.CharField(max_length=765, blank=True)
    invoice = models.CharField(max_length=765, blank=True)
    other = models.TextField(help_text="You MUST strictly adhere to the following format: mentor|relationship|school|||")
    user = models.ForeignKey(JosUsers, null=True, blank=True)
    
    def mentor(self):
    	return self.other.split('|')[0]

    def relationship(self):
    	return self.other.split('|')[1]

    def school(self):
    	return self.other.split('|')[2]
    	
    def submitted(self):
    	c = JosContent.objects.filter(created_by=self.user.pk)
    	if len(c) > 0:
    	    return "CONT" + str(c[0].pk)
    	else:
    	    return "No"
    
    def payment_status(self):
    	if self.xaction_result == "PENDING":
    	    return "PEND" + str(self.pk)
    	else:
    	    return self.xaction_result
    
    def date_registered(self):
    	utc_dt = utc.localize(self.timestamp)
    	user_tz = timezone('Australia/Melbourne')
    	user_dt = user_tz.normalize(utc_dt.astimezone(user_tz))
    	return user_dt.replace(tzinfo=None).strftime("%a %d %b, %I:%M %p")

    def __unicode__(self):
    	return self.firstname

    class Meta:
        db_table = u'jos_donations'
        ordering = ['-timestamp']
        verbose_name = 'entrant'
