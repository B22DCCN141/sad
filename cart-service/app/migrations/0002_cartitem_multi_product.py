from django.db import migrations, models


def copy_legacy_book_to_product(apps, schema_editor):
    CartItem = apps.get_model('app', 'CartItem')
    for item in CartItem.objects.all():
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
            model_name='cartitem',
            name='book_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product_type',
            field=models.CharField(default='book', max_length=20),
        ),
        migrations.RunPython(copy_legacy_book_to_product, migrations.RunPython.noop),
    ]
