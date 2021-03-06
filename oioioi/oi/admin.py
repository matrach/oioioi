from django.contrib.admin import RelatedFieldListFilter
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from oioioi.base import admin
from oioioi.base.permissions import make_request_condition
from oioioi.contests.menu import contest_admin_menu_registry
from oioioi.contests.utils import is_contest_admin
from oioioi.participants.admin import ParticipantAdmin
from oioioi.oi.models import Region, School, OIRegistration, \
                                OIOnsiteRegistration
from oioioi.oi.forms import OIRegistrationForm, RegionForm
from oioioi.participants.utils import is_contest_with_participants


@make_request_condition
def is_onsite_contest(request):
    rcontroller = request.contest.controller.registration_controller()
    return is_contest_with_participants(request.contest) \
        and issubclass(rcontroller.participant_admin,
            OIOnsiteRegistrationParticipantAdmin)


class RegionAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name')
    fields = ['short_name', 'name']
    form = RegionForm

    def has_add_permission(self, request):
        return is_contest_admin(request)

    def has_change_permission(self, request, obj=None):
        return is_contest_admin(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def queryset(self, request):
        qs = super(RegionAdmin, self).queryset(request)
        qs = qs.filter(contest=request.contest)
        return qs

    def save_model(self, request, obj, form, change):
        obj.contest = request.contest
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        Form = super(RegionAdmin, self).get_form(request, obj, **kwargs)

        def form_wrapper(*args, **kwargs):
            form = Form(*args, **kwargs)
            form.request_contest = request.contest
            return form
        return form_wrapper

admin.site.register(Region, RegionAdmin)
contest_admin_menu_registry.register('regions', _("Regions"),
    lambda request: reverse('oioioiadmin:oi_region_changelist'),
    condition=is_onsite_contest, order=21)


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'postal_code', 'city', 'province',
                    'phone', 'email')
    list_filter = ('province', 'city')
    search_fields = ('name', 'address', 'postal_code')
    ordering = ('city', 'name')

admin.site.register(School, SchoolAdmin)
admin.system_admin_menu_registry.register('schools',
    _("Schools"), lambda request:
    reverse('oioioiadmin:oi_school_changelist'), order=20)


class OIRegistrationInline(admin.StackedInline):
    model = OIRegistration
    fk_name = 'participant'
    form = OIRegistrationForm
    can_delete = False
    inline_classes = ('collapse open',)


class OIRegistrationParticipantAdmin(ParticipantAdmin):
    list_display = ParticipantAdmin.list_display \
            + ['school_name', 'school_city', 'school_province']
    inlines = ParticipantAdmin.inlines + [OIRegistrationInline, ]
    readonly_fields = ['user']
    search_fields = ParticipantAdmin.search_fields \
            + ['oi_oiregistration__school__name',
               'oi_oiregistration__school__city']

    list_filter = ParticipantAdmin.list_filter \
            + ['oi_oiregistration__school__province']

    def get_list_select_related(self):
        return super(OIRegistrationParticipantAdmin, self) \
                .get_list_select_related() + ['oi_oiregistration',
                                              'oi_oiregistration__school']

    def school_name(self, instance):
        return instance.oi_oiregistration.school.name
    school_name.short_description = _("School")
    admin_order_field = 'oi_oiregistration__school__name'

    def school_city(self, instance):
        return instance.oi_oiregistration.school.city
    school_city.admin_order_field = 'oi_oiregistration__school__city'

    def school_province(self, instance):
        return instance.oi_oiregistration.school.province
    school_province.admin_order_field = 'oi_oiregistration__school__province'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(OIRegistrationParticipantAdmin, self) \
                .get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class OIOnsiteRegistrationInline(admin.TabularInline):
    model = OIOnsiteRegistration
    fk_name = 'participant'
    can_delete = False

    def has_add_permission(self, request):
        return is_contest_admin(request)

    def has_change_permission(self, request, obj=None):
        return is_contest_admin(request)


class RegionFilter(RelatedFieldListFilter):
    def __init__(self, field, request, *args, **kwargs):
        super(RegionFilter, self).__init__(field, request, *args, **kwargs)
        contest = request.contest
        self.lookup_choices = [(r.id, unicode(r))
                               for r in contest.region_set.all()]


class OIOnsiteRegistrationParticipantAdmin(ParticipantAdmin):
    list_display = ParticipantAdmin.list_display \
            + ['number', 'region', 'local_number']
    inlines = ParticipantAdmin.inlines + [OIOnsiteRegistrationInline]
    list_filter = ParticipantAdmin.list_filter \
            + [('oi_oionsiteregistration__region', RegionFilter)]
    ordering = ['oi_oionsiteregistration__number']
    search_fields = ParticipantAdmin.search_fields \
            + ['oi_oionsiteregistration__number']

    def get_list_select_related(self):
        return super(OIOnsiteRegistrationParticipantAdmin, self) \
                .get_list_select_related() + ['oi_oionsiteregistration',
                                              'oi_oionsiteregistration__region']

    def number(self, instance):
        return instance.oi_oionsiteregistration.number
    number.admin_order_field = 'oi_oionsiteregistration__number'

    def region(self, instance):
        return instance.oi_oionsiteregistration.region
    region.admin_order_field = 'oi_oionsiteregistration__region'

    def local_number(self, instance):
        return instance.oi_oionsiteregistration.local_number
    local_number.admin_order_field = 'oi_oionsiteregistration__local_number'
