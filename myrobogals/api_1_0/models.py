from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField('Username', max_length=30, unique=True, help_text="Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores).")
    first_name = models.CharField('First name', max_length=30, blank=True)
    last_name = models.CharField('Last name', max_length=30, blank=True)   
    email = models.EmailField('E-mail address', blank=True)
    password = models.CharField('Password', max_length=128, help_text="Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>.")
    is_staff = models.BooleanField('Exec access', default=False, help_text="Designates whether the user can use exec functions on the site. Note that this option is completely independent of positions defined below.")
    is_active = models.BooleanField('Active', default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.")
    is_superuser = models.BooleanField('Superuser access', default=False, help_text="Designates that this user is able to access superuser functions on the site, and ALL functions in the Global Admin Panel.")
#Bagus comment: I changed datetime.datetime.now into auto_now_add=True for last_login and date_joined variables, since datetime.datetime doesn't work --> more detail in http://stackoverflow.com/questions/2771676/django-default-datetime-now-problem
    last_login = models.DateTimeField('Last login', auto_now_add=True) 
    date_joined = models.DateTimeField('Date joined', auto_now_add=True)
#Bagus comment: I am not sure how user_permissions field works and why we need to set M2M  relationship in this field. The variable 'Permission' here is also undefined. Temporarily, I modified it into "CharField" to pass the error  
    user_permissions = models.CharField('Permission', max_length=30, blank=True)#models.ManyToManyField(Permission, verbose_name='Django user permissions', blank=True, help_text="Allow access to individual functions in the Global Admin Panel. The user must have exec access for this to work. Don't change this unless you really know what you're doing!")  
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'email', 'password', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'user_permissions']



class Profile(models.Model):
    user = models.OneToOneField(User)
    preferred_name = models.CharField('Preferred name', max_length=30, help_text='Supports Unicode and permits names to be displayed however the user sees fit within reasonable bounds. For example, first="Yamato"+last="Takahashi" could have "é«˜æ©‹ å¤§å’Œ" for his preferred name. The preferred name shall appear preferentially in the profile page. The first/last name shall be used for URLs, core database, and menu selections, with the preferred name appearing as a secondary element.')
    dob = models.DateField('Date of Birth', null=True, blank=True)
    GENDERS = (
        (0, 'No answer'),
        (1, 'Male'),
        (2, 'Female'),
    )
    gender = models.IntegerField('Gender', choices=GENDERS, default=0)
    COUNTRIES = (
        ('AUS', 'Australia'),
        ('GBR', 'United Kingdom'), #Bagus comment: I added coma here to make it works
        ('USA', 'United States of America'),
    )
#Bagus comment: I added max_length on country, subscriptions, and biography variables to make it works
    country = models.CharField('Country', choices=COUNTRIES, max_length=30, default="AUS", blank=True, null=True)
    postcode = models.CharField('Postcode', max_length=10)
    mobile = models.CharField('Mobile', max_length=16, blank=True)
    mobile_verified = models.BooleanField(default=False)
#Bagus comment: I don't understand why we set "subscriptions" field with models.ForeignKey. Temporarily, I changed into "CharField" to pass the error     
    subscriptions = models.CharField('Subscriptions', max_length=30, default="") #models.ForeignKey('Subscriptions', default="")
    biography = models.CharField('Biography', max_length=30, default="")
    photo = models.FileField(upload_to='profilepics', blank=True)
    VISIBILITY = (
        (0, 'Private'),
        (10, 'Managers of your Robogals chapter'),
        (20, 'Everyone in your Robogals chapter'),
        (50, 'All Robogals chapters'),
        (99, 'Public'),
    )
    dob_visibility = models.IntegerField('Date of Birth Visibility', choices=VISIBILITY, default=0)
    email_visibility = models.IntegerField('Email Visibility', choices=VISIBILITY, default=0)
    profile_visibility = models.IntegerField('Profile Visibility', choices=VISIBILITY, default=0)
    REQUIRED_FIELDS = ['dob', 'gender', 'country', 'postcode', 'mobile_verified', 'subscriptions', 'biography', 'dob_visibility', 'email_visibility', 'profile_visibility']