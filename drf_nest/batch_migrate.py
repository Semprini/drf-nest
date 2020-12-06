import sys
from distutils.util import strtobool
from django.contrib.humanize.templatetags.humanize import intcomma


def confirm(question):
    'Display a message and get a command-line yes/no response as a boolean.'
    sys.stdout.write('%s [y/n] ' % question)
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            sys.stdout.write('Please respond with \'y\' or \'n\'.\n')


def batch_migrate(model, dest_db, src_db='default', chunk_size=1000, start=0):
    '''Migrate model data from one db to the other using django's
    capabability to save db records in an alternate database
    and bulk create.  If data is present in the destination db,
    it must be cleared out to avoid id conflicts; requests
    confirmation before deleting any records, and skips the model
    if delete is not approved.  Displays a progressbar
    when a model has more than 100 objects to migrate.
    '''
    # get a total of the objects to be copied
    count = model.objects.using(src_db).count()
    # nothing to do
    if not count:
        sys.stdout.write('No %s objects to copy' % model._meta.verbose_name)
        return
    # remove from dest before copying
    if model.objects.using(dest_db).exists():
        dest_count = model.objects.using(dest_db).count()
        plural = ''
        if dest_count != 1:
            plural = 's'
        msg = 'Delete %s %s object%s from %s and load %d from %s?' % \
            (dest_count, model._meta.verbose_name,
                plural, dest_db,
                count, src_db)
        if confirm(msg):
            model.objects.using(dest_db).all().delete()
        else:
            # if there are records that aren't deleted,
            # attempting to load will result in an integrity error,
            # so bail out
            return

    name = model._meta.verbose_name_plural
    if count == 1:
        name = model._meta.verbose_name
    sys.stdout.write("Copying %s %s" % (intcomma(count, use_l10n=False), name))

    items = model.objects.using(src_db).all().order_by('pk')
    # if count > 100:
    #    progress = progressbar.ProgressBar(max_value=count)
    # else:
    #    progress = None

    item_count = 0
    # process in chunks, to handle models with lots of data
    for i in range(start, count, chunk_size):
        chunk_items = items[i:i + chunk_size]
        model.objects.using(dest_db).bulk_create(chunk_items)
        item_count += chunk_items.count()
        # if progress:
        #    progress.update(item_count)

    # many-to-many fields are NOT handled by bulk create; check for
    # them and use the existing implicit through models to copy them
    # e.g. User.groups.through.objects.using('pg').all()

    # NOTE: this should only affect groups and user models; pid models
    # do not include any many-to-many relationships
    for m2mfield in model._meta.many_to_many:
        m2m_model = getattr(model, m2mfield.name).through
        batch_migrate(m2m_model, dest_db, src_db, chunk_size, start)
