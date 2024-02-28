from django.urls import reverse, resolve

from .models import Card, CardSettings, Connection, Revision, Setup, TDC


def queryset_for_admin_card_field(field, request, **kwargs):
    resolved = resolve(request.path)

    if resolved.url_name == "django_pasttrec_manager_revision_add":
        return Card.objects.none()

    if resolved.url_name == "django_pasttrec_manager_revision_change":
        obj_id = resolved.kwargs["object_id"]
        if obj_id is not None:
            q = Revision.objects.get(pk=obj_id)
            q2 = Card.objects.filter(
                cardsettings__revision__setup=q.setup.pk, cardsettings__revision__creation_on__lte=q.creation_on
            ).distinct()
            return q2
        else:
            return Card.objects.none()

    if resolved.url_name == "django_pasttrec_manager_connection_add":
        return Card.objects.none()

    if resolved.url_name == "django_pasttrec_manager_connection_change":
        obj_id = resolved.kwargs["object_id"]
        if obj_id is not None:
            q = Connection.objects.get(pk=obj_id)
            q2 = Card.objects.filter(
                cardsettings__revision__setup=q.revision.setup.pk,
                cardsettings__revision__creation_on__lte=q.revision.creation_on,
            ).distinct()
            return q2
        else:
            return Card.objects.none()

    return Card.objects.none()


def queryset_for_card_field(field, request, rev=None, tdc=None):
    resolved = resolve(request.path)
    if rev is not None:
        q_r = Revision.objects.get(pk=rev)
        q_c = Card.objects.filter(cardsettings__revision__creation_on__lte=q_r.creation_on).distinct()
        return q_c
    else:
        return Card.objects.none()
