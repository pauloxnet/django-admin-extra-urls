# -*- coding: utf-8 -*-

import pytest
from django.contrib.auth.models import Permission
from django_dynamic_fixture import G

from admin_extra_urls.extras import reverse
from demo.models import DemoModel2


@pytest.mark.django_db
def test_action(app, demomodel2, admin_user):
    url = reverse('admin:demo_demomodel2_change', args=[demomodel2.pk])
    res = app.get(url, user=admin_user)
    res = res.click(r'Update', index=1).follow()
    assert str(res.context['messages']._loaded_messages[0].message) == 'action called'


@pytest.mark.django_db
def test_action_noresponse(app, demomodel2, admin_user):
    url = reverse('admin:demo_demomodel2_change', args=[demomodel2.pk])
    res = app.get(url, user=admin_user)

    res = res.click(r'No Response').follow()
    assert str(res.context['messages']._loaded_messages[0].message) == 'No_response'


def test_action_preserve_filters(django_app, admin_user):
    a, b, c = G(DemoModel2, n=3)
    base_url = reverse('admin:demo_demomodel2_changelist')
    url = "%s?filter=on" % base_url
    res = django_app.get(url, user=admin_user)
    res = res.click('DemoModel2 #%s' % a.pk)
    link = res.pyquery('#btn-update')[0]
    assert link.get('href') == '/admin/demo/demomodel2/update/1/?_changelist_filters=filter%3Don'


def test_action_permission(app, staff_user):
    obj = G(DemoModel2)
    perms = Permission.objects.filter(codename__in=['change_demomodel2'])
    staff_user.user_permissions.add(*perms)

    url = reverse('admin:demo_demomodel2_change', args=[obj.pk])
    res = app.get(url, user=staff_user)
    assert not res.pyquery('#btn-update')

    url = reverse('admin:demo_demomodel2_update', args=[obj.pk])

    res = app.get(url, user=staff_user, expect_errors=True)
    assert res.status_code == 403


def test_action_permission_callable(app, staff_user):
    obj = G(DemoModel2)
    perms = Permission.objects.filter(codename__in=['change_demomodel2'])
    staff_user.user_permissions.add(*perms)

    url = reverse('admin:demo_demomodel2_change', args=[obj.pk])
    res = app.get(url, user=staff_user)
    assert not res.pyquery('#btn-update-callable-permission')

    url = reverse('admin:demo_demomodel2_update_callable_permission', args=[obj.pk])
    res = app.get(url, user=staff_user, expect_errors=True)
    assert res.status_code == 403
