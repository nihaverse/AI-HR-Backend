from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        HR = "HR", "HR"
        EMPLOYEE = "EMPLOYEE", "Employee"
        JOB_SEEKER = "JOB_SEEKER", "Job Seeker"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.JOB_SEEKER,
    )
