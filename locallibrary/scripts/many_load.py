import csv  # https://docs.python.org/3/library/csv.html

# https://django-extensions.readthedocs.io/en/latest/runscript.html

# python3 manage.py runscript many_load

from unesco.models import Site, Category, Region, Iso, States

def run():
    fhand = open('unesco/whc-sites-2018-clean.csv')
    reader = csv.reader(fhand)

    Site.objects.all().delete()
    Category.objects.all().delete()
    Region.objects.all().delete()
    Iso.objects.all().delete()
    States.objects.all().delete()

    # Format
    """
    category    states                 region                      iso

    Cultural    Afghanistan            Asia and the Pacific        af
    Cultural    Afghanistan            Asia and the Pacific        af
    Cultural    Albania                Europe and North America    al
    Cultural    Albania                Europe and North America    al
    Cultural    Algeria                Arab States                 dz
    Mixed       Algeria                Arab States                 dz
    Cultural    Algeria                Arab States                 dz
    Cultural    Algeria                Arab States                 dz
    """



    for index,row in enumerate(reader):
        if index >= 1: #first row is the header of csv

            try:
                y = int(row[3])
            except:
                y = None

            try:
                d = str(row[2]) # d = description
            except:
                d = None

            try:
                lo = float(row[4]) # lo = longtitude
            except:
                lo = None

            try:
                la = float(row[5]) # la = lantitude
            except:
                la = None

            try:
                a  = float(row[6]) # a = area_hectares
            except:
                a = None

            # Parse foreign keys
            c, created = Category.objects.get_or_create(name=row[7])
            i, created = Iso.objects.get_or_create(name=row[10])
            r, created = Region.objects.get_or_create(name=row[9])
            s, created = States.objects.get_or_create(name=row[8])

            m = Site(
                # unique
                name = row[0],
                description = d,
                justification = row[2],
                year = y,
                longtitude = lo,
                latitude = la,
                area_hectares = a,

                # foriegn keys
                category = c,
                iso = i,
                region = r,
                states = s
                )
            m.save()
