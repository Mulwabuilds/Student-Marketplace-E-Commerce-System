from django.db import models

from django.conf import settings

from django.core.exceptions import ValidationError



class Good(models.Model):

    CONDITION_CHOICES = [

        ('new', 'New'),

        ('used', 'Used'),

    ]

    STATUS_CHOICES = [

        ('available', 'Available'),

        ('unavailable', 'Unavailable'),

    ]



    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    category = models.ForeignKey('catalog.Category', on_delete=models.CASCADE)

    title = models.CharField(max_length=150)

    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)



    class Meta:

        constraints = [

            models.CheckConstraint(

                check=models.Q(price__gte=0),

                name='price_must_be_positive'

            ),

            models.CheckConstraint(

                check=models.Q(condition__in=['new', 'used']),

                name='valid_condition'

            ),

            models.CheckConstraint(

                check=models.Q(status__in=['available', 'unavailable']),

                name='valid_status'

            ),

        ]



    def __str__(self):

        return self.title





class GoodImage(models.Model):

    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='images')

    # URLField is slightly safer than CharField here as it validates URL formatting

    image_url = models.URLField(max_length=500)

    uploaded_at = models.DateTimeField(auto_now_add=True)



    def clean(self):

        # Enforces the max 15 images rule before saving

        if self.good.images.count() >= 15 and not self.pk:

            raise ValidationError("A maximum of 15 images is allowed per good.")



    def save(self, *args, **kwargs):

        # Force the clean method to run on save

        self.clean()

        super().save(*args, **kwargs)



    def __str__(self):

        return f"Image for {self.good.title}" 

