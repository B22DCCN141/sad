from django.db import migrations, models


def copy_legacy_book_to_product(apps, schema_editor):
    Rating = apps.get_model('app', 'Rating')
    for r in Rating.objects.all():
        if r.product_id is None and r.book_id is not None:
            r.product_id = r.book_id
            r.product_type = 'book'
            r.save(update_fields=['product_id', 'product_type'])


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rating_created_at_alter_rating_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='book_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rating',
            name='product_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rating',
            name='product_type',
            field=models.CharField(default='book', max_length=20),
        ),
        migrations.RunPython(copy_legacy_book_to_product, migrations.RunPython.noop),
    ]
