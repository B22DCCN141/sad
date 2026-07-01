from django.db import migrations, models


def copy_legacy_book_to_product(apps, schema_editor):
    OrderItem = apps.get_model('app', 'OrderItem')
    for item in OrderItem.objects.all():
        if item.product_id is None and item.book_id is not None:
            item.product_id = item.book_id
            item.product_type = 'book'
            item.save(update_fields=['product_id', 'product_type'])


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='book_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_type',
            field=models.CharField(default='book', max_length=20),
        ),
        migrations.RunPython(copy_legacy_book_to_product, migrations.RunPython.noop),
    ]
