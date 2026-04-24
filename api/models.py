from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    """Manager for User model."""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model.
    Fields: email, first_name, last_name, is_active, is_staff
    """
    ROLE_CHOICES = [
        ('ASSOCIER', 'ASSOCIER'),
        ('MANAGER', 'MANAGER'),
        ('ADMIN', 'ADMIN'),
    ]
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MANAGER')
    


    
    # New fields for Associate/Manager relationship
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='associates')
    is_approved = models.BooleanField(default=False)
    access_level = models.CharField(
        max_length=20, 
        choices=[('FULL', 'Full'), ('LIMITED', 'Limited')], 
        null=True, 
        blank=True
    )
    temp_manager_email = models.EmailField(max_length=255, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class Budget(models.Model):
    titre = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre


class BudgetHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255, default="")
    total_budget = models.DecimalField(max_digits=15, decimal_places=2)
    date_modification = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.total_budget} at {self.date_modification}"


class Depense(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    titre = models.CharField(max_length=255, blank=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='depenses')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_depenses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPROVED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titre} - {self.montant_total} ({self.status})"


class DepenseItem(models.Model):
    depense = models.ForeignKey(Depense, related_name='items', on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nom}: {self.prix}"


class UserAccess(models.Model):
    ACCESS_LEVEL_CHOICES = [
        ('FULL', 'Full Access'),
        ('LIMITED', 'Limited Access'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_accesses_given')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_accesses_received')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner', 'shared_with')

    def __str__(self):
        return f"{self.shared_with.email} has {self.access_level} on {self.owner.email}'s account"


