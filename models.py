# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class ParkingLot(models.Model):
    plotid = models.IntegerField(primary_key=True)
    plotname = models.CharField(max_length=45, blank=True, null=True)
    location = models.CharField(max_length=45, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    fee = models.IntegerField(blank=True, null=True)
    total_space = models.IntegerField(blank=True, null=True)
    available_space = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parking_lot'


class ParkingSlot(models.Model):
    slotid = models.CharField(primary_key=True, max_length=45)
    plotid = models.ForeignKey(ParkingLot, models.DO_NOTHING, db_column='plotid')
    available = models.CharField(max_length=45)
    ptime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parking_slot'


class Reservation(models.Model):
    resnum = models.IntegerField(primary_key=True)
    plotid = models.IntegerField()
    slotid = models.ForeignKey(ParkingSlot, models.DO_NOTHING, db_column='slotid')
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userid')
    carnum = models.CharField(max_length=45)
    intime = models.DateTimeField(blank=True, null=True)
    outtime = models.DateTimeField(blank=True, null=True)
    usagetime = models.IntegerField(blank=True, null=True)
    finished = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reservation'


class TutorialPost(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    text = models.TextField()

    class Meta:
        managed = False
        db_table = 'tutorial_post'


class User(models.Model):
    userid = models.CharField(primary_key=True, max_length=45)
    carnum = models.CharField(max_length=45, blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=45, blank=True, null=True)
    phone = models.CharField(max_length=45, blank=True, null=True)
    password = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
